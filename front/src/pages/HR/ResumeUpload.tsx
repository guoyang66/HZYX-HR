/**
 * 简历上传页面
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import { useState } from 'react'
import { Card, Upload, Button, message, Typography, Steps, Result, Tag, Space, Select, List } from 'antd'
import { InboxOutlined, FileTextOutlined, SearchOutlined, CheckCircleOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import type { UploadProps, UploadFile } from 'antd'
import { resumeApi, ResumeUploadResponse } from '../../api/resume'
import { positionApi, Position } from '../../api/position'
import { matchApi, MatchResult } from '../../api/match'
import { useAuthStore } from '../../store/authStore'

const { Dragger } = Upload
const { Title, Paragraph, Text } = Typography

const ResumeUpload = () => {
  const [currentStep, setCurrentStep] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [uploadResult, setUploadResult] = useState<ResumeUploadResponse | null>(null)
  const [positions, setPositions] = useState<Position[]>([])
  const [selectedPositionId, setSelectedPositionId] = useState<number | null>(null)
  const [matchResults, setMatchResults] = useState<MatchResult[]>([])
  const { token } = useAuthStore()
  const navigate = useNavigate()

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    accept: '.pdf,.doc,.docx,.txt',
    customRequest: async ({ file, onSuccess, onError }) => {
      try {
        setUploading(true)
        const result = await resumeApi.upload(file as File)
        setUploadResult(result)
        onSuccess?.(result)
        setCurrentStep(1)
        message.success('简历上传成功，正在自动匹配所有岗位...')
        // 获取岗位列表供 HR 选择
        const positionList = await positionApi.getAll()
        setPositions(positionList)
        setSelectedPositionId(null)

        // 自动遍历所有岗位进行匹配
        await autoMatchAllPositions(result.resumeId)
      } catch (error) {
        onError?.(error as Error)
        message.error('简历上传失败')
      } finally {
        setUploading(false)
      }
    },
  }

  /** 自动遍历所有岗位进行匹配分析 */
  const autoMatchAllPositions = async (resumeId: number) => {
    try {
      setAnalyzing(true)
      setCurrentStep(2)
      const results = await matchApi.matchResumeToPositions(resumeId)
      if (results.length > 0) {
        setMatchResults(results)
        setCurrentStep(3)
        message.success(`自动匹配完成，共匹配 ${results.length} 个岗位`)
      } else {
        message.info('暂无适合岗位')
        setCurrentStep(1)
      }
    } catch (error) {
      console.error('自动匹配失败', error)
      setCurrentStep(1)
    } finally {
      setAnalyzing(false)
    }
  }

  const handleAnalyze = async (resumeId?: number) => {
    const id = resumeId ?? uploadResult?.resumeId
    if (!id) return
    if (!selectedPositionId) {
      message.warning('请先选择要匹配的岗位')
      return
    }

    try {
      console.log('开始匹配分析', { resumeId: id, positionId: selectedPositionId })
      setAnalyzing(true)
      setCurrentStep(2)
      
      // 执行匹配分析
      const result = await matchApi.match({
        resumeId: id,
        positionId: selectedPositionId,
      })
      setMatchResults([result])
      setCurrentStep(3)
      message.success('匹配分析完成')
    } catch (error) {
      console.error('匹配分析失败', error)
      const errMsg = error instanceof Error ? error.message : '分析失败，请重试'
      message.error(errMsg)
      setCurrentStep(1)
    } finally {
      setAnalyzing(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#52c41a'
    if (score >= 60) return '#faad14'
    return '#ff4d4f'
  }

  const getGradeTag = (grade: string) => {
    const colors: Record<string, string> = { A: 'green', B: 'cyan', C: 'orange', D: 'red' }
    return <Tag color={colors[grade] || 'default'}>{grade} 级</Tag>
  }

  const steps = [
    { title: '上传简历', icon: <FileTextOutlined /> },
    { title: '解析完成', icon: <CheckCircleOutlined /> },
    { title: '匹配分析', icon: <SearchOutlined /> },
    { title: '查看结果', icon: <CheckCircleOutlined /> },
  ]

  return (
    <div>
      <Title level={4}>简历上传与匹配分析</Title>
      <Paragraph type="secondary">
        上传简历文件，系统将自动解析并匹配最佳岗位
      </Paragraph>

      <Steps current={currentStep} items={steps} style={{ marginBottom: 24 }} />

      {currentStep === 0 && (
        <Card>
          <Dragger {...uploadProps}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
            <p className="ant-upload-hint">
              支持 PDF、Word、纯文本格式，文件大小不超过 10MB
            </p>
          </Dragger>
        </Card>
      )}

      {currentStep === 1 && uploadResult && (
        <Card>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Result
              status="success"
              title="简历上传成功"
              subTitle={
                <div>
                  <Paragraph>文件名：{uploadResult.fileName}</Paragraph>
                  <Paragraph>
                    提取的技能：
                    <Space wrap style={{ marginTop: 8 }}>
                      {uploadResult.extractedSkills?.map(skill => (
                        <Tag key={skill} color="blue">{skill}</Tag>
                      ))}
                    </Space>
                  </Paragraph>
                </div>
              }
            >
              <div style={{ marginTop: 16 }}>
                {analyzing ? (
                  <Button loading type="primary">正在自动匹配所有岗位...</Button>
                ) : (
                  <Space wrap>
                    <Button type="primary" onClick={() => autoMatchAllPositions(uploadResult.resumeId)} loading={analyzing}>
                      重新遍历所有岗位匹配
                    </Button>
                    <Select placeholder="或指定岗位手动匹配" value={selectedPositionId ?? undefined}
                      onChange={value => setSelectedPositionId(value ?? null)}
                      options={positions.map(item => ({ label: item.title, value: item.id }))}
                      style={{ minWidth: 200 }} allowClear />
                    <Button onClick={() => handleAnalyze()} loading={analyzing} disabled={!selectedPositionId}>手动匹配</Button>
                    <Button onClick={() => { setCurrentStep(0); setUploadResult(null); setSelectedPositionId(null); }}>重新上传</Button>
                  </Space>
                )}
              </div>
            </Result>
          </Space>
        </Card>
      )}

      {currentStep === 2 && (
        <Card>
          <Result
            status="info"
            title="正在进行匹配分析"
            subTitle="系统正在进行知识图谱匹配和 LLM 综合评估（50:50 权重）..."
          />
        </Card>
      )}

      {currentStep === 3 && (
        <Card title="匹配结果">
          <List
            dataSource={matchResults.slice(0, 10)}
            renderItem={(item, index) => (
              <List.Item
                extra={
                  <Button type="link" onClick={() => navigate(`/hr/match-result/${item.id}`)}>
                    查看详情
                  </Button>
                }
              >
                <List.Item.Meta
                  avatar={
                    <div style={{ 
                      width: 48, height: 48, borderRadius: '50%', 
                      background: getScoreColor(item.finalScore), 
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      color: '#fff', fontWeight: 'bold'
                    }}>
                      {Math.round(item.finalScore)}
                    </div>
                  }
                  title={
                    <Space>
                      <Text strong>#{index + 1} {item.positionTitle}</Text>
                      {getGradeTag(item.matchGrade)}
                      <Text type="secondary">推荐指数: {'⭐'.repeat(item.recommendLevel)}</Text>
                    </Space>
                  }
                  description={
                    <Space wrap>
                      <Text>匹配技能: </Text>
                      {item.matchedSkills?.slice(0, 5).map(skill => (
                        <Tag key={skill} color="green">{skill}</Tag>
                      ))}
                      {item.matchedSkills?.length > 5 && <Tag>+{item.matchedSkills.length - 5}</Tag>}
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
          <div style={{ marginTop: 16, textAlign: 'center' }}>
            <Button onClick={() => { setCurrentStep(0); setUploadResult(null); setMatchResults([]); }}>
              上传新简历
            </Button>
          </div>
        </Card>
      )}
    </div>
  )
}

export default ResumeUpload
