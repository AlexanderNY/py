import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@/contexts/auth-context'
import { Layout } from '@/components/layout/layout'
import { SignInPage } from '@/pages/auth/sign-in'
import { SignUpPage } from '@/pages/auth/sign-up'
import { ResetPasswordPage } from '@/pages/auth/reset-password'
import { ProfilePage } from '@/pages/profile/profile'
import { BillingPage } from '@/pages/billing/billing'
import { TelegramPage } from '@/pages/telegram/telegram'
import { ThreadsPage } from '@/pages/threads/threads'
import { StatisticsPage } from '@/pages/stubs/statistics'
import { WordPressPage } from '@/pages/stubs/wordpress'
import { TwitterPage } from '@/pages/twitter'
import { VKontaktePage } from '@/pages/stubs/vkontakte'
import { CustomURLPage } from '@/pages/stubs/custom-url'
import { CreatePostPage } from '@/pages/create-post'
import { TestPage } from '@/pages/test'
import { AdministrationPage } from '@/pages/administration'
import { GroupPage } from '@/pages/group'
import { FigmaPreviewPage } from '@/pages/figma-preview'
import { AboutPage } from '@/pages/about/about'
import { RouteLoader } from '@/components/route-loader'

interface ProtectedRouteProps {
  children: React.ReactNode
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) return <RouteLoader />

  if (!isAuthenticated) {
    return <Navigate to="/sign-in" replace />
  }

  return <>{children}</>
}

interface AdminRouteProps {
  children: React.ReactNode
}

function AdminRoute({ children }: AdminRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuth()

  if (isLoading) return <RouteLoader />

  if (!isAuthenticated) {
    return <Navigate to="/sign-in" replace />
  }

  if (user?.role !== 'admin') {
    return <Navigate to="/profile" replace />
  }

  return <>{children}</>
}

interface PublicRouteProps {
  children: React.ReactNode
}

function PublicRoute({ children }: PublicRouteProps) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) return <RouteLoader />

  if (isAuthenticated) {
    return <Navigate to="/profile" replace />
  }

  return <>{children}</>
}

function App() {
  return (
    <Routes>
      <Route path="/sign-in" element={<PublicRoute><SignInPage /></PublicRoute>} />
      <Route path="/sign-up" element={<PublicRoute><SignUpPage /></PublicRoute>} />
      <Route path="/reset-password" element={<PublicRoute><ResetPasswordPage /></PublicRoute>} />
      
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<Navigate to="/profile" replace />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="billing" element={<BillingPage />} />
        <Route path="statistics" element={<StatisticsPage />} />
        <Route path="telegram" element={<TelegramPage />} />
        <Route path="threads" element={<ThreadsPage />} />
        <Route path="wordpress" element={<WordPressPage />} />
        <Route path="twitter" element={<TwitterPage />} />
        <Route path="vkontakte" element={<VKontaktePage />} />
        <Route path="custom-url" element={<CustomURLPage />} />
        <Route path="posts" element={<CreatePostPage />} />
        <Route path="create-post" element={<Navigate to="/posts" replace />} />
        <Route path="test" element={<TestPage />} />
        <Route path="group" element={<GroupPage />} />
        <Route path="administration" element={<AdminRoute><AdministrationPage /></AdminRoute>} />
        <Route path="about" element={<AboutPage />} />
      </Route>

      <Route path="figma-preview" element={<FigmaPreviewPage />} />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App


