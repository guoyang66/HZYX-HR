/**
 * 生成面试题页面
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import { useState, useEffect } from 'react'
import { Card, Form, Select, InputNumber, Button, message, List, Tag, Typography, Spin, Row, Col, Input } from 'antd'
import { RobotOutlined, CopyOutlined, PlusOutlined, DeleteOutlined } from '@ant-design/icons'
import { positionApi, Position } from '../../api/position'
import { interviewApi, InterviewQuestion, GenerateQuestionsRequest } from '../../api/interview'

const { Title, Paragraph, Text } = Typography
const { Option } = Select

const GenerateQuestions = () => {
  const [form] = Form.useForm()
  const [positions, setPositions] = useState<Position[]>([])
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [questions, setQuestions] = useState<InterviewQuestion[]>([])
  const [customSkills, setCustomSkills] = useState<string[]>([])
  const [skillInput, setSkillInput] = useState('')
  const [generateMode, setGenerateMode] = useState<'position' | 'skills'>('position')

  useEffect(() => {
    fetchPositions()
  }, [])

  const fetchPositions = async () => {
    try {
      setLoading(true)
      const list = await positionApi.getAll()
      setPositions(list)
    } catch (error) {
      message.error('获取岗位列表失败')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async (values: GenerateQuestionsRequest & { mode: string }) => {
    try {
      setGenerating(true)
      const businessDomain = values.businessDomain || '企业金融/支付'
      const payloadBase = {
        difficulty: values.difficulty || 'MIDDLE',
        count: values.count || 5,
        questionType: values.questionType || 'MIXED',
        includeAnswers: true,
        businessDomain,
      }
      
      let result
      if (values.mode === 'position' && values.positionId) {
        result = await interviewApi.generate({
          positionId: values.positionId,
          ...payloadBase,
        })
      } else if (customSkills.length > 0) {
        result = await interviewApi.generate({
          skills: customSkills,
          ...payloadBase,
        })
      } else {
        message.warning('请选择岗位或输入技能')
        return
      }

      setQuestions(result.questions || [])
      message.success('面试题生成成功')
    } catch (error) {
      message.error('生成失败，请重试')
    } finally {
      setGenerating(false)
    }
  }

  const handleAddSkill = () => {
    if (skillInput.trim() && !customSkills.includes(skillInput.trim())) {
      setCustomSkills([...customSkills, skillInput.trim()])
      setSkillInput('')
    }
  }

  const handleRemoveSkill = (skill: string) => {
    setCustomSkills(customSkills.filter(s => s !== skill))
  }

  const handleCopy = () => {
    const text = questions
      .map((q, i) => `${i + 1}. [${q.type}] ${q.question}${q.answerPoints ? `\n   参考答案: ${q.answerPoints}` : ''}`)
      .join('\n\n')
    navigator.clipboard.writeText(text)
    message.success('已复制到剪贴板')
  }

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      TECHNICAL: '技术题',
      BEHAVIORAL: '行为题',
      SCENARIO: '情景题',
    }
    return labels[type] || type
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty?.toUpperCase()) {
      case 'JUNIOR': return 'green'
      case 'MIDDLE': return 'orange'
      case 'SENIOR': return 'red'
      default: return 'blue'
    }
  }

  const getDifficultyLabel = (difficulty: string) => {
    const labels: Record<string, string> = {
      JUNIOR: '初级',
      MIDDLE: '中级',
      SENIOR: '高级',
    }
    return labels[difficulty?.toUpperCase()] || difficulty
  }

  return (
    <div>
      <Title level={4}>生成面试题</Title>

      <Row gutter={24}>
        <Col xs={24} lg={8}>
          <Card title="生成设置">
            <Spin spinning={loading}>
              <Form form={form} layout="vertical" onFinish={handleGenerate} initialValues={{ mode: 'position' }}>
                <Form.Item name="mode" label="生成方式">
                  <Select onChange={(v) => setGenerateMode(v)}>
                    <Option value="position">按岗位生成</Option>
                    <Option value="skills">按技能生成</Option>
                  </Select>
                </Form.Item>

                {generateMode === 'position' ? (
                  <Form.Item name="positionId" label="选择岗位" rules={[{ required: true, message: '请选择岗位' }]}>
                    <Select placeholder="请选择岗位" showSearch optionFilterProp="children">
                      {positions.map((p) => (
                        <Option key={p.id} value={p.id}>
                          {p.title} - {p.company}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                ) : (
                  <Form.Item label="输入技能">
                    <div>
                      <Input.Group compact>
                        <Input
                          style={{ width: 'calc(100% - 80px)' }}
                          placeholder="输入技能名称"
                          value={skillInput}
                          onChange={(e) => setSkillInput(e.target.value)}
                          onPressEnter={handleAddSkill}
                        />
                        <Button icon={<PlusOutlined />} onClick={handleAddSkill}>添加</Button>
                      </Input.Group>
                      <div style={{ marginTop: 8 }}>
                        {customSkills.map(skill => (
                          <Tag key={skill} closable onClose={() => handleRemoveSkill(skill)} style={{ marginBottom: 4 }}>
                            {skill}
                          </Tag>
                        ))}
                      </div>
                    </div>
                  </Form.Item>
                )}

                <Form.Item name="difficulty" label="难度级别" initialValue="MIDDLE">
                  <Select>
                    <Option value="JUNIOR">初级</Option>
                    <Option value="MIDDLE">中级</Option>
                    <Option value="SENIOR">高级</Option>
                  </Select>
                </Form.Item>

                <Form.Item name="count" label="题目数量" initialValue={5}>
                  <InputNumber min={1} max={20} style={{ width: '100%' }} />
                </Form.Item>

                <Form.Item name="questionType" label="题目类型" initialValue="MIXED">
                  <Select>
                    <Option value="MIXED">混合题型</Option>
                    <Option value="TECHNICAL">技术题</Option>
                    <Option value="BEHAVIORAL">行为题</Option>
                    <Option value="SCENARIO">情景题</Option>
                  </Select>
                </Form.Item>

                <Form.Item name="businessDomain" label="业务域" initialValue="企业金融/支付">
                  <Select>
                    <Option value="企业金融/支付">企业金融/支付</Option>
                    <Option value="通用">通用</Option>
                  </Select>
                </Form.Item>

                <Form.Item>
                  <Button type="primary" htmlType="submit" loading={generating} icon={<RobotOutlined />} block>
                    {generating ? '生成中...' : '生成面试题'}
                  </Button>
                </Form.Item>
              </Form>
            </Spin>
          </Card>
        </Col>

        <Col xs={24} lg={16}>
          <Card
            title="生成结果"
            extra={
              questions.length > 0 && (
                <Button icon={<CopyOutlined />} onClick={handleCopy}>
                  复制全部
                </Button>
              )
            }
          >
            {generating ? (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <Spin size="large" />
                <Paragraph style={{ marginTop: 16 }}>AI 正在生成面试题，请稍候...</Paragraph>
              </div>
            ) : questions.length > 0 ? (
              <List
                dataSource={questions}
                renderItem={(item, index) => (
                  <List.Item>
                    <List.Item.Meta
                      title={
                        <div>
                          <Text strong>第 {index + 1} 题</Text>
                          <Tag color="blue" style={{ marginLeft: 8 }}>
                            {getTypeLabel(item.type)}
                          </Tag>
                          <Tag color={getDifficultyColor(item.difficulty)}>
                            {getDifficultyLabel(item.difficulty)}
                          </Tag>
                          {item.skill && <Tag>{item.skill}</Tag>}
                        </div>
                      }
                      description={
                        <div style={{ marginTop: 8 }}>
                          <Paragraph style={{ whiteSpace: 'pre-wrap' }}>{item.question}</Paragraph>
                          {item.answerPoints && (
                            <Paragraph type="secondary">
                              <Text strong>参考答案: </Text>
                              {item.answerPoints}
                            </Paragraph>
                          )}
                          {item.evaluationDimension && (
                            <Paragraph type="secondary">
                              <Text strong>评估维度: </Text>
                              {item.evaluationDimension}
                            </Paragraph>
                          )}
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            ) : (
              <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                选择岗位和参数后，点击生成按钮获取面试题
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default GenerateQuestions
