/**
 * HZYX-HR 主应用组件
 *
 * @author QinFeng Luo
 * @date 2026/01/09
 */
import { Routes, Route, Navigate } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import { Spin } from 'antd'
import MainLayout from './components/Layout/MainLayout'
import { useAuthStore } from './store/authStore'

// 懒加载页面组件
const Login = lazy(() => import('./pages/Login'))
const Register = lazy(() => import('./pages/Register'))
const HRDashboard = lazy(() => import('./pages/HR/Dashboard'))
const ResumeUpload = lazy(() => import('./pages/HR/ResumeUpload'))
const PositionManage = lazy(() => import('./pages/HR/PositionManage'))
const MatchResult = lazy(() => import('./pages/HR/MatchResult'))
const MatchHistory = lazy(() => import('./pages/HR/MatchHistory'))
const InterviewerDashboard = lazy(() => import('./pages/Interviewer/Dashboard'))
const GenerateQuestions = lazy(() => import('./pages/Interviewer/GenerateQuestions'))
const QuestionHistory = lazy(() => import('./pages/Interviewer/QuestionHistory'))

// 加载中组件
const LoadingFallback = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
    <Spin size="large" tip="加载中..." />
  </div>
)

// 受保护的路由组件
const ProtectedRoute = ({ children, allowedRoles }: { children: React.ReactNode; allowedRoles?: string[] }) => {
  const { isAuthenticated, user } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}

function App() {
  const { isAuthenticated, user } = useAuthStore()

  return (
    <Suspense fallback={<LoadingFallback />}>
      <Routes>
        {/* 公开路由 */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* 受保护的路由 */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          {/* 根据用户角色重定向 */}
          <Route
            index
            element={
              isAuthenticated && user ? (
                user.role === 'HR' ? (
                  <Navigate to="/hr/dashboard" replace />
                ) : (
                  <Navigate to="/interviewer/dashboard" replace />
                )
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />

          {/* HR 路由 */}
          <Route path="hr">
            <Route
              path="dashboard"
              element={
                <ProtectedRoute allowedRoles={['HR']}>
                  <HRDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="resume-upload"
              element={
                <ProtectedRoute allowedRoles={['HR']}>
                  <ResumeUpload />
                </ProtectedRoute>
              }
            />
            <Route
              path="positions"
              element={
                <ProtectedRoute allowedRoles={['HR']}>
                  <PositionManage />
                </ProtectedRoute>
              }
            />
            <Route
              path="match-result/:id"
              element={
                <ProtectedRoute allowedRoles={['HR']}>
                  <MatchResult />
                </ProtectedRoute>
              }
            />
            <Route
              path="match-history"
              element={
                <ProtectedRoute allowedRoles={['HR']}>
                  <MatchHistory />
                </ProtectedRoute>
              }
            />
          </Route>

          {/* 面试官路由 */}
          <Route path="interviewer">
            <Route
              path="dashboard"
              element={
                <ProtectedRoute allowedRoles={['INTERVIEWER']}>
                  <InterviewerDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="generate"
              element={
                <ProtectedRoute allowedRoles={['INTERVIEWER']}>
                  <GenerateQuestions />
                </ProtectedRoute>
              }
            />
            <Route
              path="history"
              element={
                <ProtectedRoute allowedRoles={['INTERVIEWER']}>
                  <QuestionHistory />
                </ProtectedRoute>
              }
            />
          </Route>
        </Route>

        {/* 404 页面 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  )
}

export default App


