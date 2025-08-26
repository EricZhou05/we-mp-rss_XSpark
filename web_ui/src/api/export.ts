import http from './http'
export const ExportOPML = () => {
  return http.get<{code: number, data: string}>('/wx/export/mps/opml', {
    params: {
      limit: 1000,
      offset: 0
    }
  })
}

export const ExportMPS = () => {
  return http.get('/wx/export/mps/export', {
    params: { limit: 1000, offset: 0 },
    responseType: 'blob',
  });
};

export const ImportMPS = (formData) => {
  return http.post<{code: number, data: string}>('/wx/export/mps/import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 定义导出 DOCX 请求的参数类型。
 * feed_id 和 tag_id 是互斥的，调用时应只提供一个。
 */
interface ExportDocxParams {
  start_date: string;
  end_date: string;
  feed_id?: string; // 可选的公众号ID ('all' 代表全部)
  tag_id?: string;  // 可选的标签ID
}

/**
 * 按时间范围和筛选条件（公众号或标签）导出文章为 DOCX 文件。
 * 此函数对应 apis/exporter.py 中的新 API。
 * @param params 包含时间范围和筛选条件的参数对象。
 *               例如: { start_date: '...', end_date: '...', feed_id: 'some_id' }
 *               或者: { start_date: '...', end_date: '...', tag_id: 'some_tag_id' }
 */
export const exportArticlesAsDocx = (params: ExportDocxParams) => {
  // URL 从 /docx/{feed_id} 变更为 /docx
  // feed_id 从路径参数变为可选的查询参数
  // 路由前缀是 /wx/exporter，对应 exporter_router
  return http.get('/wx/exporter/docx', {
    params, // 将整个 params 对象作为查询参数传递
    responseType: 'blob', // 关键配置：告诉http客户端期望接收二进制文件数据
  });
};