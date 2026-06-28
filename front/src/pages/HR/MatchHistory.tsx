/**
 * 匹配历史页面
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import { useEffect, useState } from 'react'
import { Card, Table, Tag, Button, Space, Progress, message } from 'antd'
import { EyeOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import type { ColumnsType } from 'antd/es/table'
import { matchApi, MatchResult, MatchRecordListResponse } from '../../api/match'

const MatchHistory = () => {
  const [loading, setLoading] = useState(false)
  const [records, setRecords] = useState<MatchResult[]>([])
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 })
  const navigate = useNavigate()

  useEffect(() => {
    fetchRecords(pagination.current, pagination.pageSize)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const fetchRecords = async (page: number, pageSize: number) => {
    try {
      setLoading(true)
      const res: MatchRecordListResponse = await matchApi.getRecords({
        page: page - 1,
        size: pageSize,
      })
      setRecords(res.content)
      setPagination({ current: page, pageSize, total: res.totalElements })
    } catch (e) {
      message.error('获取匹配历史失败')
    } finally {
      setLoading(false)
    }
  }

  const getMatchLevelColor = (level?: string) => {
    switch (level) {
      case 'A':
        return 'green'
      case 'B':
        return 'cyan'
      case 'C':
        return 'blue'
      default:
        return 'red'
    }
  }

  const columns: ColumnsType<MatchResult> = [
    {
      title: '简历名称',
      dataIndex: 'resumeName',
      key: 'resumeName',
    },
    {
      title: '匹配岗位',
      dataIndex: 'positionTitle',
      key: 'positionTitle',
    },
    {
      title: '综合得分',
      dataIndex: 'finalScore',
      key: 'finalScore',
      render: (score: number) => (
        <Progress
          percent={Number(score?.toFixed(1) || 0)}
          size="small"
          strokeColor={score >= 80 ? '#52c41a' : score >= 60 ? '#faad14' : '#ff4d4f'}
        />
      ),
    },
    {
      title: '匹配等级',
      dataIndex: 'matchGrade',
      key: 'matchGrade',
      render: (grade?: string) => <Tag color={getMatchLevelColor(grade)}>{grade || '-'}</Tag>,
    },
    {
      title: '分析时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => navigate(`/hr/match-result/${record.id}`)}
        >
          查看详情
        </Button>
      ),
    },
  ]

  return (
    <Card title="匹配历史">
      <Table
        columns={columns}
        dataSource={records}
        rowKey="id"
        loading={loading}
        pagination={{
          ...pagination,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, pageSize) => fetchRecords(page, pageSize),
        }}
      />
    </Card>
  )
}

export default MatchHistory

