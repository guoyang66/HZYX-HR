/**
 * 匹配分析相关 API
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import request from './request'

export interface MatchResult {
  id: number
  resumeId: number
  positionId: number
  resumeName: string
  positionTitle: string
  finalScore: number
  ragScore: number
  graphScore: number
  llmScore: number
  matchedSkills: string[]
  missingSkills: string[]
  extraSkills: string[]
  llmReport: string
  matchGrade: string
  recommendLevel: number
  scoreDetails: Record<string, unknown>
  createdAt: string
}

export interface MatchRecordListResponse {
  content: MatchResult[]
  totalElements: number
  totalPages: number
  number: number
  size: number
}

export interface MatchRequest {
  resumeId: number
  positionId: number
}

export const matchApi = {
  // 执行单次匹配
  match: async (data: MatchRequest): Promise<MatchResult> => {
    return await request.post<MatchResult>('/hr/match', data)
  },

  // 一份简历匹配多个岗位
  matchResumeToPositions: async (resumeId: number): Promise<MatchResult[]> => {
    return await request.post<MatchResult[]>(`/hr/match/resume/${resumeId}/positions`, null, { timeout: 120000 })
  },

  // 一个岗位匹配多份简历
  matchPositionToResumes: async (positionId: number): Promise<MatchResult[]> => {
    return await request.post<MatchResult[]>(`/hr/match/position/${positionId}/resumes`)
  },

  // 获取匹配记录列表
  getRecords: async (params?: { page?: number; size?: number }): Promise<MatchRecordListResponse> => {
    return await request.get<MatchRecordListResponse>('/hr/match', { params })
  },

  // 获取匹配详情
  getRecordById: async (id: number): Promise<MatchResult> => {
    return await request.get<MatchResult>(`/hr/match/${id}`)
  },

  // 获取简历的匹配历史
  getResumeMatchHistory: async (resumeId: number): Promise<MatchResult[]> => {
    return await request.get<MatchResult[]>(`/hr/match/resume/${resumeId}/history`)
  },

  // 获取岗位的匹配历史
  getPositionMatchHistory: async (positionId: number): Promise<MatchResult[]> => {
    return await request.get<MatchResult[]>(`/hr/match/position/${positionId}/history`)
  },
}
