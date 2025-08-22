import io
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import datetime
import pytz
import docx
from urllib.parse import quote

from core.db import DB
from core.models import Feed, Article
from apis.base import error_response

# 创建一个新的路由实例
router = APIRouter(prefix="/exporter", tags=["Exporter"])

# 定义北京时区，用于时间转换
beijing_tz = pytz.timezone('Asia/Shanghai')


def add_hyperlink(paragraph, text, url):
    """
    一个辅助函数，用于在段落中添加可点击的超链接。
    python-docx本身不直接支持，需要操作底层的XML。
    """
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

    hyperlink = docx.oxml.shared.OxmlElement('w:hyperlink')
    hyperlink.set(docx.oxml.shared.qn('r:id'), r_id)

    new_run = docx.oxml.shared.OxmlElement('w:r')
    rPr = docx.oxml.shared.OxmlElement('w:rPr')

    # 设置超链接样式为蓝色和下划线
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
        # 1. 将前端传入的北京时间字符串转换为带时区的datetime对象
        start_dt_naive = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        end_dt_naive = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        start_dt_beijing = beijing_tz.localize(start_dt_naive)
        end_dt_beijing = beijing_tz.localize(end_dt_naive)

        # 2. 转换为Unix时间戳 (Integer) 以便与数据库中的 publish_time 比较
        start_timestamp = int(start_dt_beijing.timestamp())
        end_timestamp = int(end_dt_beijing.timestamp())

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=error_response(code=40001, message="日期格式错误，应为 'YYYY-MM-DD HH:MM:SS'")
        )

    # 3. 查询数据库，连接Article和Feed表以获取公众号名称
    query = db.query(Article, Feed).join(Feed, Article.mp_id == Feed.id)

    if feed_id != "all":
        query = query.filter(Article.mp_id == feed_id)

    # 按时间范围筛选，并按发布时间升序排序
    articles_with_feed = query.filter(
        Article.publish_time >= start_timestamp,
        Article.publish_time <= end_timestamp
    ).order_by(Article.publish_time.asc()).all()

    if not articles_with_feed:
        raise HTTPException(
            status_code=404,
            detail=error_response(code=40401, message="在指定时间范围内未找到任何文章")
        )

    # 4. 创建DOCX文档
    document = docx.Document()
    document.add_heading('星火选题库', 0)

    for article, feed in articles_with_feed:
        # 格式：标题(公众号名称)
        title_text = f"{article.title} ({feed.mp_name})"
        p_title = document.add_paragraph()
        p_title.add_run(title_text).bold = True

        # 格式：发布时间 (从时间戳转换为北京时间)
        publish_dt_beijing = datetime.datetime.fromtimestamp(article.publish_time, tz=beijing_tz)
        time_text = publish_dt_beijing.strftime('%Y-%m-%d_%H:%M:%S')
        document.add_paragraph(time_text)

        # 格式：文章链接 (可点击的超链接)
        p_link = document.add_paragraph()
        add_hyperlink(p_link, article.url, article.url)

        # 添加一个空行作为分隔
        document.add_paragraph()

    # 5. 生成动态文件名
    # 获取第一篇和最后一篇文章的发布时间来命名
    first_article_time = datetime.datetime.fromtimestamp(articles_with_feed[0][0].publish_time, tz=beijing_tz)
    last_article_time = datetime.datetime.fromtimestamp(articles_with_feed[-1][0].publish_time, tz=beijing_tz)

    filename = f"星火选题库({first_article_time.strftime('%m.%d')}_{last_article_time.strftime('%m.%d')}).docx"

    # 6. 将文档保存到内存流并作为响应返回
    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0)

    # 设置响应头，告知浏览器这是一个需要下载的文件
    headers = {
        'Content-Disposition': f"attachment; filename*=UTF-8''{quote(filename)}",
        'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }

    return StreamingResponse(file_stream, headers=headers)