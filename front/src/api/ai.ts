/**
 * AI 模型相关 API
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import request from './request'
import { AIModel } from '../store/aiStore'

export const aiApi = {
  // 获取可用模型列表
  getModels: (): Promise<AIModel[]> => {
    return request.get('/ai/models')
  },

  // 获取当前使用的模型
  getCurrentModel: (): Promise<{ modelId: string; modelName: string }> => {
    return request.get('/ai/current')
  },

  // 切换模型
  switchModel: (modelId: string): Promise<{ success: boolean; message: string }> => {
    return request.post('/ai/switch', { modelId })
  },
}


