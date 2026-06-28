/**
 * Axios 请求封装
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { message } from 'antd'
import { useAuthStore } from '../store/authStore'

// API 响应格式
interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
  timestamp?: string
}

const request = axios.create({
  baseURL: '/api',
  timeout: 180000,
})

// 请求拦截器
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const res = response.data as ApiResponse

    // 如果后端返回的 code 不是 200，视为业务错误
    if (res.code && res.code !== 200) {
      message.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }

    // 返回 data 部分，如果没有 data 则返回整个响应
    return res.data !== undefined ? res.data : res
  },
  (error: AxiosError<ApiResponse>) => {
    const { response } = error

    if (response) {
      // 优先使用服务器返回的 message
      const serverMessage = response.data?.message

      switch (response.status) {
        case 401:
          message.error(serverMessage || '登录已过期，请重新登录')
          useAuthStore.getState().logout()
          window.location.href = '/login'
          break
        case 403:
          message.error(serverMessage || '没有权限访问')
          break
        case 404:
          message.error(serverMessage || '请求的资源不存在')
          break
        case 500:
          // 500 错误时显示服务器返回的具体错误信息
          message.error(serverMessage || '服务器内部错误')
          break
        default:
          message.error(serverMessage || '请求失败')
      }
    } else {
      message.error('网络错误，请检查网络连接')
    }

    return Promise.reject(error)
  }
)

export default request
