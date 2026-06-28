/**
 * HR 工作台
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import { Card, Row, Col, Statistic, Button, Typography, message } from 'antd'
import { FileTextOutlined, TeamOutlined, CheckCircleOutlined, UploadOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { resumeApi } from '../../api/resume'
import { positionApi } from '../../api/position'
import { matchApi } from '../../api/match'

const { Title, Paragraph } = Typography

const HRDashboard = () => {
  const navigate = useNavigate()
  const [resumeCount, setResumeCount] = useState<number>(0)
  const [positionCount, setPositionCount] = useState<number>(20)
  const [matchCount, setMatchCount] = useState<number>(0)
  const [highMatchCount, setHighMatchCount] = useState<number>(0)

  useEffect(() => {
    const fetchCounts = async () => {
      try {
        const resumePage = await resumeApi.getList({ page: 0, size: 1 })
        setResumeCount(resumePage.totalElements || 0)
      } catch (e) {
        message.warn('获取简历数量失败')
      }

      try {
        const positions = await positionApi.getAll()
        setPositionCount(positions.length || 0)
      } catch (e) {
        // 忽略，保持默认值
      }

      try {
        // 取匹配记录，使用较大分页来统计匹配数和高匹配数
        const matchPage = await matchApi.getRecords({ page: 0, size: 200 })
        const records = matchPage.content || []
        setMatchCount(matchPage.totalElements || records.length || 0)
        const highCount =
          records.filter((r) => (r.matchGrade || '').toUpperCase() === 'A' || (r.finalScore ?? 0) >= 80).length
        setHighMatchCount(highCount)
      } catch (e) {
        // 可忽略，不影响其他统计
      }
    }
    fetchCounts()
  }, [])

  return (
    <div>
      <Title level={4}>欢迎使用 HZYX-HR 智能招聘匹配助手</Title>
      <Paragraph type="secondary">
        上传简历，智能匹配岗位，获取详细的匹配分析报告和学习建议
      </Paragraph>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已上传简历"
              value={resumeCount}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="岗位数量"
              value={positionCount}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="匹配分析"
              value={matchCount}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="高度匹配"
              value={highMatchCount}
              suffix="个岗位"
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={12}>
          <Card
            title="快速开始"
            extra={<Button type="primary" icon={<UploadOutlined />} onClick={() => navigate('/hr/resume-upload')}>上传简历</Button>}
          >
            <Paragraph>
              <ol>
                <li>上传候选人简历（支持 PDF、Word、纯文本）</li>
                <li>系统自动解析简历，提取技能信息</li>
                <li>智能匹配岗位，生成综合评分</li>
                <li>查看详细匹配报告和学习建议</li>
              </ol>
            </Paragraph>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="匹配算法说明">
            <Paragraph>
              系统采用三维度混合检索评分：
            </Paragraph>
            <ul>
              <li><strong>语义相似度（40%）</strong>：基于向量检索的简历与岗位语义匹配</li>
              <li><strong>技能匹配度（40%）</strong>：基于知识图谱的技能覆盖、深度、前置依赖分析</li>
              <li><strong>LLM 综合评估（20%）</strong>：大模型对整体匹配度的智能评估</li>
            </ul>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default HRDashboard
