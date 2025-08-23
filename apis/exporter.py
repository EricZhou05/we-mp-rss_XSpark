import io
import datetime
import pytz
from urllib.parse import quote

import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from core.db import DB
from core.models import Feed, Article
from apis.base import error_response

# 创建一个新的路由实例
router = APIRouter(prefix="/exporter", tags=["Exporter"])

# 定义时区
beijing_tz = pytz.timezone('Asia/Shanghai')
utc_tz = pytz.utc  # 定义UTC时区


def set_modern_compatibility(document):
    """
    修改文档的兼容性设置，使其符合最新的Word标准。
    """
    settings = document.settings.element
    compat_elements = settings.xpath('w:compat')
    if compat_elements:
        compat = compat_elements[0]
    else:
        compat = OxmlElement('w:compat')
        settings.append(compat)

    compat_setting = OxmlElement('w:compatSetting')
    compat_setting.set(qn('w:name'), 'compatibilityMode')
    compat_setting.set(qn('w:uri'), 'http://schemas.microsoft.com/office/word')
    compat_setting.set(qn('w:val'), '16')
    compat.append(compat_setting)


def add_hyperlink(paragraph, text, url):
    """
    一个辅助函数，用于在段落中添加可点击的超链接。
    """
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

    hyperlink = docx.oxml.shared.OxmlElement('w:hyperlink')
    hyperlink.set(docx.oxml.shared.qn('r:id'), r_id)

    new_run = docx.oxml.shared.OxmlElement('w:r')
    rPr = docx.oxml.shared.OxmlElement('w:rPr')

    font_name = '新宋体'
    rFonts = docx.oxml.shared.OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:eastAsia'), font_name)
    rPr.append(rFonts)

    c = docx.oxml.shared.OxmlElement('w:color')
    c.set(docx.oxml.shared.qn('w:val'), '0000FF')
    rPr.append(c)
    u = docx.oxml.shared.OxmlElement('w:u')
    u.set(docx.oxml.shared.qn('w:val'), 'single')
    rPr.append(u)

    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)

    return hyperlink


@router.get("/docx/{feed_id}", summary="按时间范围导出公众号文章为DOCX")
async def export_articles_to_docx(
        feed_id: str,
        start_date: str = Query(..., description="开始日期 (北京时间, 格式: YYYY-MM-DD HH:MM:SS)"),
        end_date: str = Query(..., description="结束日期 (北京时间, 格式: YYYY-MM-DD HH:MM:SS)"),
        db: Session = Depends(DB.session_dependency)
):
    try:
        start_dt_naive = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        end_dt_naive = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        start_dt_beijing = beijing_tz.localize(start_dt_naive)
        end_dt_beijing = beijing_tz.localize(end_dt_naive)
        start_timestamp = int(start_dt_beijing.timestamp())
        end_timestamp = int(end_dt_beijing.timestamp())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=error_response(code=40001, message="日期格式错误，应为 'YYYY-MM-DD HH:MM:SS'")
        )

    query = db.query(Article, Feed).join(Feed, Article.mp_id == Feed.id)
    if feed_id != "all":
        query = query.filter(Article.mp_id == feed_id)

    articles_with_feed = query.filter(
        Article.publish_time >= start_timestamp,
        Article.publish_time <= end_timestamp
    ).order_by(Article.publish_time.asc()).all()

    if not articles_with_feed:
        raise HTTPException(
            status_code=404,
            detail=error_response(code=40401, message="在指定时间范围内未找到任何文章")
        )

    document = docx.Document()

    set_modern_compatibility(document)

    # (一) 设置文档元数据
    # --- 核心修改部分 ---
    # 必须使用UTC时间来设置文档属性，以避免时区转换错误
    now_utc = datetime.datetime.now(utc_tz)

    core_properties = document.core_properties
    core_properties.author = '星火调研易'
    core_properties.last_modified_by = '星火调研易'
    # 将标准的UTC时间赋给创建和修改日期
    core_properties.created = now_utc
    core_properties.modified = now_utc
    core_properties.comments = ''
    # --- 核心修改结束 ---

    # (二) 设置全局样式
    style = document.styles['Normal']
    font = style.font
    font.name = '新宋体'
    style.element.rPr.rFonts.set(qn('w:eastAsia'), '新宋体')

    paragraph_format = style.paragraph_format
    paragraph_format.first_line_indent = Pt(0)
    paragraph_format.left_indent = Pt(0)
    paragraph_format.space_after = Pt(6)
    paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

    # (三) 设置页面布局
    section = document.sections[0]
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)

    for article, feed in articles_with_feed:
        title_text = f"{article.title} ({feed.mp_name})"
        p_title = document.add_paragraph()
        p_title.add_run(title_text).bold = True

        publish_dt_beijing = datetime.datetime.fromtimestamp(article.publish_time, tz=beijing_tz)
        time_text = publish_dt_beijing.strftime('%Y-%m-%d %H:%M:%S')
        document.add_paragraph(time_text)

        p_link = document.add_paragraph()
        add_hyperlink(p_link, article.url, article.url)

    first_article_time = datetime.datetime.fromtimestamp(articles_with_feed[0][0].publish_time, tz=beijing_tz)
    last_article_time = datetime.datetime.fromtimestamp(articles_with_feed[-1][0].publish_time, tz=beijing_tz)
    filename = f"星火选题库({first_article_time.strftime('%m.%d')}_{last_article_time.strftime('%m.%d')}).docx"

    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0)

    headers = {
        'Content-Disposition': f"attachment; filename*=UTF-8''{quote(filename)}",
        'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }

    return StreamingResponse(file_stream, headers=headers)