/**
 * 主布局组件
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import { useState, useEffect } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Dropdown, Avatar, Space, message } from 'antd'
import {
  UserOutlined,
  FileTextOutlined,
  TeamOutlined,
  HistoryOutlined,
  LogoutOutlined,
  DashboardOutlined,
 QuestionCircleOutlined,
  SettingOutlined,
} from '@ant-design/icons'
import { useAuthStore } from '../../store/authStore'
import ModelSelector from '../ModelSelector'
import type { MenuProps } from 'antd'

const { Header, Sider, Content, Footer } = Layout

const MainLayout = () => {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()

  // HR 菜单
  const hrMenuItems: MenuProps['items'] = [
    {
      key: '/hr/dashboard',
      icon: <DashboardOutlined />,
      label: '工作台',
    },
    {
      key: '/hr/resume-upload',
      icon: <FileTextOutlined />,
      label: '简历上传',
    },
    {
      key: '/hr/positions',
      icon: <TeamOutlined />,
      label: '岗位管理',
    },
    {
      key: '/hr/match-history',
      icon: <HistoryOutlined />,
      label: '匹配历史',
    },
  ]

  // 面试官菜单
  const interviewerMenuItems: MenuProps['items'] = [
    {
      key: '/interviewer/dashboard',
      icon: <DashboardOutlined />,
      label: '工作台',
    },
    {
      key: '/interviewer/generate',
      icon: <QuestionCircleOutlined />,
      label: '生成面试题',
    },
    {
      key: '/interviewer/history',
      icon: <HistoryOutlined />,
      label: '生成历史',
    },
  ]

  const menuItems = user?.role === 'HR' ? hrMenuItems : interviewerMenuItems

  const handleMenuClick: MenuProps['onClick'] = (e) => {
    navigate(e.key)
  }

  const handleLogout = () => {
    logout()
    message.success('已退出登录')
    navigate('/login')
  }

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '个人设置',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ]

  // 获取当前选中的菜单项
  const selectedKeys = [location.pathname]

  return (
    <Layout className="app-shell" style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        theme="light"
        className="app-sider"
        width={230}
      >
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderBottom: '1px solid var(--border)',
          }}
        >
          <h1
            className="logo-mark"
            style={{ margin: 0, fontSize: collapsed ? 16 : 20, color: 'var(--text)' }}
          >
            {collapsed ? 'HX' : 'HZYX-HR'}
          </h1>
        </div>
        <Menu
          mode="inline"
          selectedKeys={selectedKeys}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ borderRight: 0, background: 'transparent', color: 'var(--text)' }}
        />
      </Sider>

      <Layout>
        <Header
          className="app-header"
          style={{
            padding: '0 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)',
          }}
        >
          <div style={{ fontSize: 16, fontWeight: 500 }}>
            {user?.role === 'HR' ? 'HR 工作台' : '面试官工作台'}
          </div>

          <Space size="large">
            <ModelSelector />

            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <Space style={{ cursor: 'pointer' }}>
                <Avatar icon={<UserOutlined />} />
                <span>{user?.username}</span>
              </Space>
            </Dropdown>
          </Space>
        </Header>

        <Content
          className="app-content"
          style={{
            minHeight: 280,
          }}
        >
          <Outlet />
        </Content>

        <Footer className="app-footer">
          <div className="footer-inner">
            <span className="footer-brand">HZYX-HR</span>
            <span className="footer-copy">© {new Date().getFullYear()} HZYX-HR. All rights reserved.</span>
          </div>
        </Footer>
      </Layout>
    </Layout>
  )
}

export default MainLayout
