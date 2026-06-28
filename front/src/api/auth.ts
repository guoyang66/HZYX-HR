/**
 * 认证相关 API
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import request from './request'
import { User } from '../store/authStore'

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  password: string
  email: string
  role: 'HR' | 'INTERVIEWER'
}

// 后端实际返回的认证响应格式
export interface AuthResponseData {
  accessToken: string
  refreshToken: string
  tokenType: string
  expiresIn: number
  user: User
}

// 前端使用的简化格式
export interface AuthResponse {
  token: string
  user: User
}

export const authApi = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const res: AuthResponseData = await request.post('/auth/login', data)
    return {
      token: res.accessToken,
      user: res.user,
    }
  },

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const res: AuthResponseData = await request.post('/auth/register', data)
    return {
      token: res.accessToken,
      user: res.user,
    }
  },

  logout: (): Promise<void> => {
    return request.post('/auth/logout')
  },

  getCurrentUser: (): Promise<User> => {
    return request.get('/auth/me')
  },
}
