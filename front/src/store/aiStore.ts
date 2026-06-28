/**
 * AI 模型状态管理
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import { create } from 'zustand'

export interface AIModel {
  modelId: string
  modelName: string
  enabled: boolean
  current: boolean
}

interface AIState {
  models: AIModel[]
  currentModel: string | null
  loading: boolean
  setModels: (models: AIModel[]) => void
  setCurrentModel: (modelId: string) => void
  setLoading: (loading: boolean) => void
}

export const useAIStore = create<AIState>((set) => ({
  models: [],
  currentModel: null,
  loading: false,

  setModels: (models: AIModel[]) => {
    const current = models.find((m) => m.current)
    set({
      models,
      currentModel: current?.modelId || null,
    })
  },

  setCurrentModel: (modelId: string) =>
    set((state) => ({
      currentModel: modelId,
      models: state.models.map((m) => ({
        ...m,
        current: m.modelId === modelId,
      })),
    })),

  setLoading: (loading: boolean) => set({ loading }),
}))


