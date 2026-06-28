/**
 * 面试题生成历史页面
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import { useEffect, useState } from 'react'
import { Card, Table, Tag, Button, Modal, List, Typography, message } from 'antd'
import { EyeOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { interviewApi, InterviewRecord } from '../../api/interview'

const { Text, Paragraph } = Typography

const QuestionHistory = () => {
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [selectedRecord, setSelectedRecord] = useState<InterviewRecord | null>(null)
  const [records, setRecords] = useState<InterviewRecord[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)

  useEffect(() => {
    fetchRecords(page, pageSize)
  }, [page, pageSize])

  const fetchRecords = async (pageNum: number, size: number) => {
    try {
      setLoading(true)
      const res = await interviewApi.getRecords({ page: pageNum - 1, size })
      setRecords(res.content || [])
      setTotal(res.totalElements || 0)
    } catch (e) {
      message.error('获取生成历史失败')
    } finally {
      setLoading(false)
    }
  }

  const getDifficultyTag = (difficulty: string) => {
    switch (difficulty?.toUpperCase()) {
      case 'JUNIOR':
        return <Tag color="green">简单</Tag>
      case 'MIDDLE':
        return <Tag color="orange">中等</Tag>
      case 'SENIOR':
        return <Tag color="red">困难</Tag>
      default:
        return <Tag>{difficulty}</Tag>
    }
  }

  const handleView = (record: InterviewRecord) => {
    setSelectedRecord(record)
    setModalVisible(true)
  }

  const getDisplayTitle = (record: InterviewRecord) => {
    if (record.positionTitle) return record.positionTitle

    const skills =
      record.questions
        ?.map((q) => (q as any).skill as string | undefined)
        ?.filter((s) => !!s) || []

    if (skills.length) {
      const unique = Array.from(new Set(skills))
      const shown = unique.slice(0, 3).join(', ')
      return unique.length > 3 ? `按技能生成：${shown} 等` : `按技能生成：${shown}`
    }

    return '按技能生成'
  }

  const columns: ColumnsType<InterviewRecord> = [
    {
      title: '岗位',
      dataIndex: 'positionTitle',
      key: 'positionTitle',
      render: (_value, record) => getDisplayTitle(record),
    },
    {
      title: '难度',
      dataIndex: 'difficulty',
      key: 'difficulty',
      render: (difficulty) => getDifficultyTag(difficulty),
    },
    {
      title: '题目数量',
      dataIndex: 'questions',
      key: 'questionCount',
      render: (qs) => `${qs?.length || 0} 道`,
    },
    {
      title: '生成时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Button type="link" icon={<EyeOutlined />} onClick={() => handleView(record)}>
          查看详情
        </Button>
      ),
    },
  ]

  return (
    <div>
      <Card title="生成历史">
        <Table
          columns={columns}
          dataSource={records}
          rowKey="id"
          loading={loading}
          pagination={{
            current: page,
            pageSize,
            total,
            showSizeChanger: true,
            showTotal: (t) => `共 ${t} 条`,
            onChange: (p, size) => {
              setPage(p)
              setPageSize(size)
            },
          }}
        />
      </Card>

      <Modal
        title={`面试题详情 - ${selectedRecord ? getDisplayTitle(selectedRecord) : ''}`}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={700}
      >
        {selectedRecord && (
          <List
            dataSource={selectedRecord.questions}
            renderItem={(item, index) => (
              <List.Item>
                <List.Item.Meta
                  title={
                    <div>
                      <Text strong>第 {index + 1} 题</Text>
                      {item.type && (
                        <Tag color="blue" style={{ marginLeft: 8 }}>
                          {item.type}
                        </Tag>
                      )}
                      {item.difficulty && (
                        <Tag style={{ marginLeft: 8 }}>{item.difficulty}</Tag>
                      )}
                    </div>
                  }
                  description={
                    <div style={{ marginTop: 8 }}>
                      <Paragraph>{(item as any).question || (item as any).content}</Paragraph>
                      {('answerPoints' in item || 'answer' in item) && (
                        <Paragraph type="secondary">
                          <Text strong>参考答案: </Text>
                          {(item as any).answerPoints || (item as any).answer}
                        </Paragraph>
                      )}
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Modal>
    </div>
  )
}

export default QuestionHistory
