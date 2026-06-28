/**
 * 岗位管理页面
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import { useState, useEffect } from 'react'
import { Card, Table, Button, Space, Input, Tag, Modal, Form, message, Upload } from 'antd'
import { PlusOutlined, SearchOutlined, UploadOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { positionApi, Position, CreatePositionRequest } from '../../api/position'

const { Search } = Input
const { TextArea } = Input

const PositionManage = () => {
  const [positions, setPositions] = useState<Position[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingPosition, setEditingPosition] = useState<Position | null>(null)
  const [form] = Form.useForm()
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 })

  useEffect(() => {
    fetchPositions()
  }, [pagination.current])

  const fetchPositions = async (keyword?: string) => {
    try {
      setLoading(true)
      const response = await positionApi.getList({
        page: pagination.current - 1,
        size: pagination.pageSize,
        keyword,
      })
      setPositions(response.content)
      setPagination((prev) => ({ ...prev, total: response.totalElements }))
    } catch (error) {
      message.error('获取岗位列表失败')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (value: string) => {
    setPagination((prev) => ({ ...prev, current: 1 }))
    fetchPositions(value)
  }

  const handleAdd = () => {
    setEditingPosition(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (record: Position) => {
    setEditingPosition(record)
    form.setFieldsValue({
      ...record,
      skills: record.skills?.join(', '),
    })
    setModalVisible(true)
  }

  const handleDelete = async (id: number) => {
    try {
      await positionApi.delete(id)
      message.success('删除成功')
      fetchPositions()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleSubmit = async (values: CreatePositionRequest & { skills: string }) => {
    try {
      const data = {
        ...values,
        skills: values.skills?.split(',').map((s) => s.trim()).filter(Boolean) || [],
      }

      if (editingPosition) {
        await positionApi.update(editingPosition.id, data)
        message.success('更新成功')
      } else {
        await positionApi.create(data)
        message.success('创建成功')
      }

      setModalVisible(false)
      fetchPositions()
    } catch (error) {
      message.error('操作失败')
    }
  }

  const columns: ColumnsType<Position> = [
    {
      title: '岗位名称',
      dataIndex: 'title',
      key: 'title',
      width: 200,
    },
    {
      title: '公司',
      dataIndex: 'company',
      key: 'company',
      width: 150,
    },
    {
      title: '薪资',
      dataIndex: 'salaryRange',
      key: 'salaryRange',
      width: 120,
    },
    {
      title: '经验要求',
      dataIndex: 'experience',
      key: 'experience',
      width: 100,
    },
    {
      title: '技能标签',
      dataIndex: 'skills',
      key: 'skills',
      render: (skills: string[]) => (
        <Space wrap>
          {skills?.slice(0, 3).map((skill) => (
            <Tag key={skill} color="blue">
              {skill}
            </Tag>
          ))}
          {skills?.length > 3 && <Tag>+{skills.length - 3}</Tag>}
        </Space>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Button type="link" danger icon={<DeleteOutlined />} onClick={() => handleDelete(record.id)}>
            删除
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Card
        title="岗位管理"
        extra={
          <Space>
            <Search placeholder="搜索岗位" onSearch={handleSearch} style={{ width: 200 }} />
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新建岗位
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={positions}
          rowKey="id"
          loading={loading}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => setPagination({ current: page, pageSize, total: pagination.total }),
          }}
        />
      </Card>

      <Modal
        title={editingPosition ? '编辑岗位' : '新建岗位'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={700}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="title" label="岗位名称" rules={[{ required: true, whitespace: true, message: '请输入岗位名称' }]}>
            <Input placeholder="请输入岗位名称" />
          </Form.Item>
          <Form.Item name="company" label="公司名称">
            <Input placeholder="请输入公司名称" />
          </Form.Item>
          <Space style={{ width: '100%' }} size="large">
            <Form.Item name="salaryRange" label="薪资范围">
              <Input placeholder="如：15K-25K" />
            </Form.Item>
            <Form.Item name="experience" label="经验要求">
              <Input placeholder="如：3-5年" />
            </Form.Item>
            <Form.Item name="education" label="学历要求">
              <Input placeholder="如：本科及以上" />
            </Form.Item>
            <Form.Item name="location" label="工作地点">
              <Input placeholder="如：北京" />
            </Form.Item>
          </Space>
          <Form.Item
            name="responsibilities"
            label="岗位职责"
            rules={[{ required: true, whitespace: true, message: '请输入岗位职责' }]}
          >
            <TextArea rows={4} placeholder="请输入岗位职责" />
          </Form.Item>
          <Form.Item
            name="requirements"
            label="任职要求"
            rules={[{ required: true, whitespace: true, message: '请输入任职要求' }]}
          >
            <TextArea rows={4} placeholder="请输入任职要求" />
          </Form.Item>
          <Form.Item name="skills" label="技能标签">
            <Input placeholder="多个技能用逗号分隔，如：Java, Spring Boot, MySQL" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default PositionManage
