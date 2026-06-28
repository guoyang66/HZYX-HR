/**
 * 匹配结果页面（数据来自后端）
 */
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Card, Typography, Progress, Tag, List, Row, Col, Descriptions, Divider, message, Spin, Space } from 'antd'
import { CheckCircleOutlined, WarningOutlined } from '@ant-design/icons'
import { matchApi, MatchResult as MatchResultData } from '../../api/match'

const { Title, Paragraph, Text } = Typography

const MatchResultPage = () => {
  const { id } = useParams()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<MatchResultData | null>(null)

  useEffect(() => {
    if (id) {
      fetchResult(Number(id))
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  const fetchResult = async (matchId: number) => {
    try {
      setLoading(true)
      const res = await matchApi.getRecordById(matchId)
      setResult(res)
    } catch (e) {
      message.error('获取匹配结果失败')
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#52c41a'
    if (score >= 60) return '#faad14'
    return '#ff4d4f'
  }

  const renderStars = (count?: number) => '⭐'.repeat(Math.max(0, Math.min(5, count || 0)))

  if (!id) {
    return <Paragraph>无效的匹配记录</Paragraph>
  }

  if (loading || !result) {
    return <Spin />
  }

  return (
    <div>
      <Title level={4}>匹配分析结果</Title>

      {/* 综合得分 */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={24} align="middle">
          <Col span={8} style={{ textAlign: 'center' }}>
            <Progress
              type="circle"
              percent={Number(result.finalScore?.toFixed(1) || 0)}
              strokeColor={getScoreColor(result.finalScore || 0)}
              format={(percent) => (
                <div>
                  <div style={{ fontSize: 32, fontWeight: 'bold' }}>{percent}</div>
                  <div style={{ fontSize: 14, color: '#666' }}>综合得分</div>
                </div>
              )}
            />
            <div style={{ marginTop: 8 }}>
              <Space>
                <Tag color={getScoreColor(result.finalScore || 0)}>{result.matchGrade || '未评级'}</Tag>
                {result.recommendLevel ? <Tag color="blue">推荐指数: {renderStars(result.recommendLevel)}</Tag> : null}
              </Space>
            </div>
          </Col>
          <Col span={16}>
            <Descriptions title="匹配信息" column={2}>
              <Descriptions.Item label="岗位">{result.positionTitle}</Descriptions.Item>
              <Descriptions.Item label="简历">{result.resumeName}</Descriptions.Item>
              <Descriptions.Item label="分析时间">{result.createdAt}</Descriptions.Item>
            </Descriptions>
          </Col>
        </Row>
      </Card>

      {/* 评分维度（RAG 已禁用，知识图谱 + LLM 50:50） */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card title="技能匹配度 (50%)">
            <Progress
              percent={Number(result.graphScore?.toFixed(1) || 0)}
              strokeColor="#52c41a"
              format={(percent) => `${percent}分`}
            />
            <Text type="secondary">知识图谱技能匹配得分（50%权重）</Text>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="LLM 综合评估 (50%)">
            <Progress
              percent={Number(result.llmScore?.toFixed(1) || 0)}
              strokeColor="#722ed1"
              format={(percent) => `${percent}分`}
            />
            <Text type="secondary">AI 综合评估得分（50%权重）</Text>
          </Card>
        </Col>
      </Row>

      {/* 技能分析 */}
      <Card title="技能分析" style={{ marginBottom: 16 }}>
        <Row gutter={24}>
          <Col span={8}>
            <Title level={5}>
              <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
              已匹配技能
            </Title>
            {result.matchedSkills?.length ? (
              result.matchedSkills.map((skill) => (
                <Tag key={skill} color="green" style={{ marginBottom: 8 }}>
                  {skill}
                </Tag>
              ))
            ) : (
              <Text type="secondary">暂无</Text>
            )}
          </Col>
          <Col span={8}>
            <Title level={5}>
              <WarningOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />
              缺失技能
            </Title>
            {result.missingSkills?.length ? (
              result.missingSkills.map((skill) => (
                <Tag key={skill} color="red" style={{ marginBottom: 8 }}>
                  {skill}
                </Tag>
              ))
            ) : (
              <Text type="secondary">暂无</Text>
            )}
          </Col>
          <Col span={8}>
            <Title level={5}>
              <WarningOutlined style={{ color: '#faad14', marginRight: 8 }} />
              额外技能
            </Title>
            {result.extraSkills?.length ? (
              result.extraSkills.map((skill) => (
                <Tag key={skill} color="orange" style={{ marginBottom: 8 }}>
                  {skill}
                </Tag>
              ))
            ) : (
              <Text type="secondary">暂无</Text>
            )}
          </Col>
        </Row>
      </Card>

      {/* AI 分析 */}
      <Card title="AI 综合分析">
        <Paragraph>{result.llmReport || '暂无 AI 分析报告'}</Paragraph>
        <Divider />
        <Text type="secondary">匹配记录 ID：{result.id}</Text>
      </Card>
    </div>
  )
}

export default MatchResultPage
