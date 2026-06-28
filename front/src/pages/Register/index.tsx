/**
 * 注册页面
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Form, Input, Button, Card, message, Typography, Radio } from 'antd'
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons'
import { useAuthStore } from '../../store/authStore'
import { authApi, RegisterRequest } from '../../api/auth'

const { Title, Text } = Typography

const Register = () => {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()

  const onFinish = async (values: RegisterRequest) => {
    setLoading(true)
    try {
      const { token, user } = await authApi.register(values)
      setAuth(token, user)
      message.success('注册成功')
      navigate(user.role === 'HR' ? '/hr/dashboard' : '/interviewer/dashboard')
    } catch (error) {
      // 错误已在 request.ts 中通过 message.error 显示
      // 这里不需要再显示
      console.error('Register failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Card
        style={{
          width: 400,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          borderRadius: 12,
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Title level={2} style={{ marginBottom: 8, color: '#1890ff' }}>
            HZYX-HR
          </Title>
          <Text type="secondary">创建新账号</Text>
        </div>

        <Form name="register" onFinish={onFinish} size="large" initialValues={{ role: 'HR' }}>
          <Form.Item
            name="username"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 3, message: '用户名至少3个字符' },
            ]}
          >
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>

          <Form.Item
            name="email"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' },
            ]}
          >
            <Input prefix={<MailOutlined />} placeholder="邮箱" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码至少6个字符' },
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            dependencies={['password']}
            rules={[
              { required: true, message: '请确认密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve()
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'))
                },
              }),
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="确认密码" />
          </Form.Item>

          <Form.Item name="role" label="角色" rules={[{ required: true }]}>
            <Radio.Group>
              <Radio value="HR">HR</Radio>
              <Radio value="INTERVIEWER">面试官</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              注册
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            <Text type="secondary">
              已有账号？ <Link to="/login">立即登录</Link>
            </Text>
          </div>
        </Form>
      </Card>
    </div>
  )
}

export default Register
