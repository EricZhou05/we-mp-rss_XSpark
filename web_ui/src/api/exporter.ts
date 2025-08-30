import http from './http'
import qs from 'qs' // 新增：用于数组序列化

/**
 * 定义导出 DOCX 请求的参数类型。
 * feed_id 和 tag_id 仍互斥；tag_id 现在支持数组。
 */
interface ExportDocxParams {
  start_date: string;
  end_date: string;
  feed_id?: string;          // 可选的公众号ID ('all' 代表全部)
  tag_id?: string | string[]; // 可选的标签ID，支持多个：['1','2']
}

/**
 * 按时间范围和筛选条件（公众号或标签）导出文章为 DOCX 文件。
 */
export const exportArticlesAsDocx = (params: ExportDocxParams) => {
  return http.get('/wx/exporter/docx', {
    params,
    responseType: 'blob',
    // 关键：将数组序列化为重复的 key（?tag_id=1&tag_id=2），以兼容 FastAPI List[str]
    paramsSerializer: (p) => qs.stringify(p, { arrayFormat: 'repeat' }),
  });
};