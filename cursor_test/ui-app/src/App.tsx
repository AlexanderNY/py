import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@/contexts/auth-context'
import { Layout } from '@/components/layout/layout'
import { SignInPage } from '@/pages/auth/sign-in'
import { SignUpPage } from '@/pages/auth/sign-up'
import { ResetPasswordPage } from '@/pages/auth/reset-password'
import { ProfilePage } from '@/pages/profile/profile'
import { TelegramPage } from '@/pages/telegram/telegram'
import { StatisticsPage } from '@/pages/stubs/statistics'
import { WordPressPage } from '@/pages/stubs/wordpress'
import { TwitterPage } from '@/pages/stubs/twitter'
import { VKontaktePage } from '@/pages/stubs/vkontakte'
import { CustomURLPage } from '@/pages/stubs/custom-url'
import { CreatePostPage } from '@/pages/create-post'

interface ProtectedRouteProps {
  children: React.ReactNode
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse-subtle text-primary-400">Loading...</div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/sign-in" replace />
  }

  return <>{children}</>
}

interface PublicRouteProps {
  children: React.ReactNode
}

function PublicRoute({ children }: PublicRouteProps) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse-subtle text-primary-400">Loading...</div>
      </div>
    )
  }

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
        <Route path="statistics" element={<StatisticsPage />} />
        <Route path="telegram" element={<TelegramPage />} />
        <Route path="wordpress" element={<WordPressPage />} />
        <Route path="twitter" element={<TwitterPage />} />
        <Route path="vkontakte" element={<VKontaktePage />} />
        <Route path="custom-url" element={<CustomURLPage />} />
        <Route path="create-post" element={<CreatePostPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App


