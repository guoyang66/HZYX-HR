/**
 * 岗位相关 API
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import request from './request'

export interface Position {
  id: number
  title: string
  company: string
  salaryRange: string
  experience: string
  education: string
  location: string
  responsibilities: string
  requirements: string
  skills: string[]
  createdAt: string
}

export interface PositionListResponse {
  content: Position[]
  totalElements: number
  totalPages: number
  number: number
  size: number
}

export interface CreatePositionRequest {
  title: string
  company?: string
  salaryRange?: string
  experience?: string
  education?: string
  location?: string
  responsibilities: string
  requirements: string
  skills?: string[]
}

export const positionApi = {
  // 获取岗位列表
  getList: async (params?: { page?: number; size?: number; keyword?: string }): Promise<PositionListResponse> => {
    return await request.get<PositionListResponse>('/hr/positions', { params })
  },

  // 获取所有岗位
  getAll: async (): Promise<Position[]> => {
    return await request.get<Position[]>('/hr/positions/all')
  },

  // 获取岗位详情
  getById: async (id: number): Promise<Position> => {
    return await request.get<Position>(`/hr/positions/${id}`)
  },

  // 创建岗位
  create: async (data: CreatePositionRequest): Promise<Position> => {
    return await request.post<Position>('/hr/positions', data)
  },

  // 更新岗位
  update: async (id: number, data: Partial<CreatePositionRequest>): Promise<Position> => {
    return await request.put<Position>(`/hr/positions/${id}`, data)
  },

  // 删除岗位
  delete: async (id: number): Promise<void> => {
    await request.delete(`/hr/positions/${id}`)
  },
}
