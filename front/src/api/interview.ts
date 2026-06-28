/**
 * 面试题相关 API
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import request from './request'

export interface InterviewQuestion {
  question: string
  type: string
  difficulty: string
  skill: string
  answerPoints?: string
  evaluationDimension: string
}

export interface InterviewRecord {
  id: number
  positionId: number | null
  positionTitle: string | null
  userId: number
  difficulty: string
  questionType: string
  questions: InterviewQuestion[]
  createdAt: string
}

export interface InterviewRecordListResponse {
  content: InterviewRecord[]
  totalElements: number
  totalPages: number
  number: number
  size: number
}

export interface GenerateQuestionsRequest {
  positionId?: number
  skills?: string[]
  difficulty?: 'JUNIOR' | 'MIDDLE' | 'SENIOR'
  count?: number
  questionType?: 'TECHNICAL' | 'BEHAVIORAL' | 'SCENARIO' | 'MIXED'
  includeAnswers?: boolean
  businessDomain?: string
}

interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export const interviewApi = {
  // 生成面试题（完整参数）
  generate: async (data: GenerateQuestionsRequest): Promise<InterviewRecord> => {
    const res = await request.post<InterviewRecord>('/interview/generate', data, { timeout: 120000 })
    return res
  },

  // 根据岗位快速生成
  generateByPosition: async (positionId: number, difficulty?: string, count?: number): Promise<InterviewRecord> => {
    const params = new URLSearchParams()
    if (difficulty) params.append('difficulty', difficulty)
    if (count) params.append('count', count.toString())
    const res = await request.post<InterviewRecord>(`/interview/generate/position/${positionId}?${params.toString()}`, null, { timeout: 120000 })
    return res
  },

  // 根据技能列表生成
  generateBySkills: async (skills: string[], difficulty?: string, count?: number): Promise<InterviewRecord> => {
    const params = new URLSearchParams()
    if (difficulty) params.append('difficulty', difficulty)
    if (count) params.append('count', count.toString())
    const res = await request.post<InterviewRecord>(`/interview/generate/skills?${params.toString()}`, skills, { timeout: 120000 })
    return res
  },

  // 获取面试记录列表
  getRecords: async (params?: { page?: number; size?: number }): Promise<InterviewRecordListResponse> => {
    const res = await request.get<InterviewRecordListResponse>('/interview/records', { params })
    return res
  },

  // 获取面试记录详情
  getRecordById: async (id: number): Promise<InterviewRecord> => {
    const res = await request.get<InterviewRecord>(`/interview/records/${id}`)
    return res
  },

  // 删除面试记录
  deleteRecord: async (id: number): Promise<void> => {
    await request.delete(`/interview/records/${id}`)
  },
}
