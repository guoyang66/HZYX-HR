/**
 * 简历相关 API
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import request from './request'

export interface Resume {
  id: number
  userId: number
  fileName: string
  filePath: string
  content: string
  extractedSkills: string[]
  createdAt: string
}

export interface ResumeUploadResponse {
  resumeId: number
  fileName: string
  parsedContent: string
  extractedSkills: string[]
  message: string
}

export interface ResumeListResponse {
  content: Resume[]
  totalElements: number
  totalPages: number
  number: number
  size: number
}

export const resumeApi = {
  // 上传简历
  upload: async (file: File): Promise<ResumeUploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    return await request.post<ResumeUploadResponse>('/hr/resumes/upload', formData)
  },

  // 获取简历列表
  getList: async (params?: { page?: number; size?: number; keyword?: string }): Promise<ResumeListResponse> => {
    return await request.get<ResumeListResponse>('/hr/resumes', { params })
  },

  // 获取所有简历
  getAll: async (): Promise<Resume[]> => {
    return await request.get<Resume[]>('/hr/resumes/all')
  },

  // 获取简历详情
  getById: async (id: number): Promise<Resume> => {
    return await request.get<Resume>(`/hr/resumes/${id}`)
  },

  // 删除简历
  delete: async (id: number): Promise<void> => {
    await request.delete(`/hr/resumes/${id}`)
  },
}
