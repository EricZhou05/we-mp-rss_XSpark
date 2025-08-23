import axios from 'axios'
import { getToken } from '@/utils/auth'
import { Message } from '@arco-design/web-vue'
import router from '@/router'

// 创建axios实例
const http = axios.create({
  baseURL: (import.meta.env.VITE_API_BASE_URL || '') + 'api/v1/',
  timeout: 100000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// 请求拦截器
http.interceptors.request.use(
  config => {
    const token = getToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  response => {
    const contentType = response.headers['content-type'] || '';

    // [修改] 检查响应是否为JSON格式
    if (contentType.includes('application/json')) {
      // 这是标准的JSON API响应
      if (response.data?.code === 0) {
        // 成功的业务逻辑
        return response.data?.data || response.data?.detail || response.data;
      }
      if (response.data?.code === 401) {
        router.push("/login");
        return Promise.reject("未登录或登录已过期，请重新登录。");
      }
      // 业务逻辑失败（但HTTP状态码是2xx）
      const errorMsg = response.data?.detail?.message || response.data?.message || '请求失败';
      Message.error(errorMsg);
      return Promise.reject(response.data);
    } else {
      // [修改]对于非JSON响应（如文件下载），返回完整的response对象
      // 这样调用方才能访问到headers，如'content-disposition'
      return response;
    }
  },
  error => {
    if (error.response?.status === 401) {
      router.push("/login");
      Message.error("未登录或登录已过期，请重新登录。");
      return Promise.reject(error);
    }

    // 对于404等错误，直接将整个error对象reject出去
    // 让具体的业务代码（如handleExport）去处理
    // 这样可以根据不同的错误状态码做不同的提示
    const errorMsg = error?.response?.data?.detail?.message ||
                     error?.response?.data?.detail ||
                     error?.message ||
                     '请求错误';

    // 只有在没有被业务代码捕获并处理时，才显示全局错误消息
    // Message.error(errorMsg);

    // [修改]返回原始的error对象，而不是一个字符串
    // 这样业务代码可以访问 error.response.data 等信息
    return Promise.reject(error);
  }
)

export default http;