/**
 * HZYX-HR 前端入口文件
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: '#f26b38',
          colorTextBase: '#1f2d3d',
          colorBgBase: '#f7f6f3',
          colorBorder: '#e5e6eb',
          colorBgContainer: '#ffffff',
          borderRadius: 12,
          fontFamily: `'Inter Tight', 'Space Grotesk', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif`,
        },
        components: {
          Layout: {
            headerBg: 'transparent',
            bodyBg: 'transparent',
            siderBg: 'transparent',
          },
          Menu: {
            itemHoverColor: '#f26b38',
            itemSelectedColor: '#f26b38',
            itemSelectedBg: 'rgba(242, 107, 56, 0.12)',
            itemBg: 'transparent',
          },
        },
      }}
    >
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ConfigProvider>
  </React.StrictMode>,
)
