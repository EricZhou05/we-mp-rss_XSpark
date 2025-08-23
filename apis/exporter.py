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

# --- 全局配置 ---
router = APIRouter(prefix="/exporter", tags=["Exporter"])
beijing_tz = pytz.timezone('Asia/Shanghai')
utc_tz = pytz.utc


# --- 辅助函数 ---

def set_modern_compatibility(document):
    """
    修改文档兼容性设置，使其符合最新的Word标准 (Word 365/2019/2016)。
    这是生成“现代化”文档最关键的一步。
    """
    settings = document.settings.element
    compat_elements = settings.xpath('w:compat')
    compat = compat_elements[0] if compat_elements else OxmlElement('w:compat')

    # 创建或更新兼容性设置
    compat_setting = OxmlElement('w:compatSetting')
    compat_setting.set(qn('w:name'), 'compatibilityMode')
    compat_setting.set(qn('w:uri'), 'http://schemas.microsoft.com/office/word')
    compat_setting.set(qn('w:val'), '16')  # '16' 代表最新的Word版本
    compat.append(compat_setting)

    if not compat_elements:
        settings.append(compat)


def add_hyperlink(paragraph, text, url):
    """在段落中添加一个格式化的超链接。"""
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)

    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')

    # 保持超链接字体与文档默认字体一致
    font_name = '新宋体'
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:eastAsia'), font_name)
    rPr.append(rFonts)

    # 设置蓝色和下划线
    color = OxmlElement('w:color')
    color.set(qn('w:val'), '0000FF')
    rPr.append(color)
    underline = OxmlElement('w:u')
    underline.set(qn('w:val'), 'single')
    rPr.append(underline)

    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
    return hyperlink


def create_modern_docx(articles_data):
    """
    一个工厂函数，用于创建一个配置完整的、现代化的DOCX文档对象。
    """
    document = docx.Document()

    # 1. 设置文档为最新标准，禁用兼容模式
    set_modern_compatibility(document)

    # 2. 设置专业的元数据 (文件属性)
    now_utc = datetime.datetime.now(utc_tz)
    core_properties = document.core_properties
    core_properties.author = '星火调研易'
    core_properties.last_modified_by = '星火调研易'
    core_properties.created = now_utc  # 使用UTC时间避免时区错误
    core_properties.modified = now_utc
    core_properties.comments = ''  # 清空备注
    core_properties.title = '星火选题库'

    # 3. 设置全局默认样式 (字体、段落)
    style = document.styles['Normal']
    font = style.font
    font.name = '新宋体'
    style.element.rPr.rFonts.set(qn('w:eastAsia'), '新宋体')

    p_format = style.paragraph_format
    p_format.first_line_indent = Pt(0)
    p_format.left_indent = Pt(0)
    p_format.space_after = Pt(6)  # 约0.5行
    p_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

    # 4. 设置页面布局 (窄边距)
    section = document.sections[0]
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)

    # 5. 填充内容
    for article, feed in articles_data:
        # 添加标题
        p_title = document.add_paragraph()
        p_title.add_run(f"{article.title} ({feed.mp_name})").bold = True

        # 添加发布时间
        publish_time = datetime.datetime.fromtimestamp(article.publish_time, tz=beijing_tz)
        document.add_paragraph(publish_time.strftime('%Y-%m-%d %H:%M:%S'))

        # 添加链接
        p_link = document.add_paragraph()
        add_hyperlink(p_link, article.url, article.url)

    return document


# --- FastAPI 路由 ---

@router.get("/docx/{feed_id}", summary="按时间范围导出公众号文章为现代DOCX")
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
        raise HTTPException(status_code=400, detail="日期格式错误，应为 'YYYY-MM-DD HH:MM:SS'")

    articles_with_feed = db.query(Article, Feed).join(Feed, Article.mp_id == Feed.id) \
        .filter(Article.mp_id == feed_id if feed_id != "all" else True) \
        .filter(Article.publish_time.between(start_timestamp, end_timestamp)) \
        .order_by(Article.publish_time.asc()).all()

    if not articles_with_feed:
        raise HTTPException(status_code=404, detail="在指定时间范围内未找到任何文章")

    # 使用工厂函数创建配置好的文档
    document = create_modern_docx(articles_with_feed)

    # 生成动态文件名
    first_time = datetime.datetime.fromtimestamp(articles_with_feed[0][0].publish_time, tz=beijing_tz)
    last_time = datetime.datetime.fromtimestamp(articles_with_feed[-1][0].publish_time, tz=beijing_tz)
    filename = f"星火选题库({first_time.strftime('%m.%d')}_{last_time.strftime('%m.%d')}).docx"

    # 保存到内存流并返回
    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0)

    headers = {
        'Content-Disposition': f"attachment; filename*=UTF-8''{quote(filename)}",
        'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    return StreamingResponse(file_stream, headers=headers)