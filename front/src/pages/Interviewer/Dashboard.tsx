/**
 * 面试官工作台
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import { useEffect, useState } from 'react'
import { Card, Row, Col, Statistic, Button, Typography, message } from 'antd'
import { QuestionCircleOutlined, HistoryOutlined, TeamOutlined, RobotOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import dayjs from 'dayjs'
import { positionApi } from '../../api/position'
import { interviewApi } from '../../api/interview'

const { Title, Paragraph } = Typography

const InterviewerDashboard = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState({
    positions: 0,
    generatedTotal: 0,
    todayGenerated: 0,
  })

  useEffect(() => {
    const loadStats = async () => {
      try {
        setLoading(true)
        const [positionRes, recordRes] = await Promise.all([
          positionApi.getList({ page: 0, size: 1 }),
          interviewApi.getRecords({ page: 0, size: 100 }),
        ])

        const todayCount =
          recordRes.content?.filter((item) => dayjs(item.createdAt).isSame(dayjs(), 'day')).length ?? 0

        setStats({
          positions: positionRes.totalElements ?? 0,
          generatedTotal: recordRes.totalElements ?? 0,
          todayGenerated: todayCount,
        })
      } catch (error) {
        message.error('加载统计数据失败')
      } finally {
        setLoading(false)
      }
    }

    loadStats()
  }, [])

  return (
    <div>
      <Title level={4}>欢迎使用 HZYX-HR 面试题生成助手</Title>
      <Paragraph type="secondary">
        选择岗位，一键生成专业的面试题目，助力高效面试
      </Paragraph>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="可用岗位"
              value={stats.positions}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#1890ff' }}
              loading={loading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已生成题目"
              value={stats.generatedTotal}
              prefix={<QuestionCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
              loading={loading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="今日生成"
              value={stats.todayGenerated}
              prefix={<HistoryOutlined />}
              valueStyle={{ color: '#722ed1' }}
              loading={loading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="AI 模型"
              value="已就绪"
              prefix={<RobotOutlined />}
              valueStyle={{ color: '#faad14', fontSize: 20 }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={12}>
          <Card
            title="快速开始"
            extra={
              <Button type="primary" icon={<QuestionCircleOutlined />} onClick={() => navigate('/interviewer/generate')}>
                生成面试题
              </Button>
            }
          >
            <Paragraph>
              <ol>
                <li>选择目标岗位</li>
                <li>设置难度级别和题目数量</li>
                <li>点击生成，AI 自动生成面试题</li>
                <li>查看并导出面试题目</li>
              </ol>
            </Paragraph>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="题目类型说明">
            <Paragraph>
              系统支持多种类型的面试题生成：
            </Paragraph>
            <ul>
              <li><strong>技术基础题</strong>：考察基础知识掌握程度</li>
              <li><strong>场景设计题</strong>：考察实际问题解决能力</li>
              <li><strong>代码实现题</strong>：考察编码能力</li>
              <li><strong>系统设计题</strong>：考察架构设计能力</li>
              <li><strong>行为面试题</strong>：考察软技能和团队协作</li>
            </ul>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default InterviewerDashboard

