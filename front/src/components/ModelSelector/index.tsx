/**
 * AI 模型选择器组件
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import { useEffect } from 'react'
import { Select, message, Tooltip } from 'antd'
import { RobotOutlined } from '@ant-design/icons'
import { useAIStore } from '../../store/aiStore'
import { aiApi } from '../../api/ai'

const ModelSelector = () => {
  const { models, currentModel, loading, setModels, setCurrentModel, setLoading } = useAIStore()

  useEffect(() => {
    fetchModels()
  }, [])

  const fetchModels = async () => {
    try {
      setLoading(true)
      const data = await aiApi.getModels()
      setModels(data)
    } catch (error) {
      console.error('获取模型列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = async (modelId: string) => {
    try {
      setLoading(true)
      await aiApi.switchModel(modelId)
      setCurrentModel(modelId)
      message.success(`已切换到 ${models.find((m) => m.modelId === modelId)?.modelName}`)
    } catch (error) {
      message.error('切换模型失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Tooltip title="选择 AI 模型">
      <Select
        className="model-selector"
        value={currentModel}
        onChange={handleChange}
        loading={loading}
        style={{ width: 150 }}
        placeholder="选择模型"
        suffixIcon={<RobotOutlined />}
        options={models.map((model) => ({
          value: model.modelId,
          label: model.modelName,
          disabled: !model.enabled,
        }))}
      />
    </Tooltip>
  )
}

export default ModelSelector

