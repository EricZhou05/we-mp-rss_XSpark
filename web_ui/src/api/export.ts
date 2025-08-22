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

// 定义导出 DOCX 请求的参数类型
interface ExportDocxParams {
  start_date: string;
  end_date: string;
}

/**
 * 按时间范围导出文章为 DOCX 文件
 * @param feedId 公众号ID，如果为 'all' 则导出全部
 * @param params 包含 start_date 和 end_date 的对象
 */
export const exportArticlesAsDocx = (feedId: string, params: ExportDocxParams) => {
  // 注意：这里的 http.get 返回的是一个 Promise<AxiosResponse<Blob>>
  // 我们直接将整个响应返回，以便在组件中可以访问 headers
  return http.get(`/exporter/docx/${feedId}`, {
    params,
    responseType: 'blob', // 关键配置：告诉http客户端期望接收二进制文件数据
  });
};