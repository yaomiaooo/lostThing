import axios from 'axios'

// 创建axios实例
const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    const token = sessionStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 直接返回响应数据
    return response.data
  },
  (error) => {
    console.error('请求错误:', error)
    
    // 处理错误响应
    if (error.response) {
      // 服务器返回错误状态码
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // 未授权，跳转到登录页
          sessionStorage.clear()
          window.location.href = '/login'
          break
        case 403:
          // 权限不足
          console.error('权限不足:', data.msg || '无权限访问')
          break
        case 404:
          // 资源不存在
          console.error('资源不存在:', data.msg || '请求的资源不存在')
          break
        case 500:
          // 服务器内部错误
          console.error('服务器错误:', data.msg || '服务器内部错误')
          break
        default:
          console.error('请求错误:', data.msg || '未知错误')
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      console.error('网络错误:', '请检查网络连接')
    } else {
      // 请求配置错误
      console.error('请求配置错误:', error.message)
    }
    
    return Promise.reject(error)
  }
)

export default request