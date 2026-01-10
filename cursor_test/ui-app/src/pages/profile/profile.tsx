import { useState, FormEvent } from 'react'
import { useAuth } from '@/contexts/auth-context'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Alert } from '@/components/ui/alert'

export function ProfilePage() {
  const { user, accessToken, refreshToken, updateProfile, logout, logoutAll, refreshUserData } = useAuth()
  
  const [isEditing, setIsEditing] = useState(false)
  const [email, setEmail] = useState(user?.email || '')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  
  const [verificationCode, setVerificationCode] = useState('')
  const [isVerifying, setIsVerifying] = useState(false)

  async function handleUpdateProfile(e: FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsLoading(true)
    
    try {
      await updateProfile({ email })
      setSuccess('Profile updated successfully')
      setIsEditing(false)
      await refreshUserData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile')
    } finally {
      setIsLoading(false)
    }
  }

  async function handleVerifyEmail(e: FormEvent) {
    e.preventDefault()
    setIsVerifying(true)
    setError('')
    
    // Placeholder for email verification
    try {
      // TODO: Implement email verification endpoint call
      console.log('Verification code:', verificationCode)
      setSuccess('Email verification submitted')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Verification failed')
    } finally {
      setIsVerifying(false)
    }
  }

  async function handleLogoutAll() {
    if (confirm('Are you sure you want to logout from all devices?')) {
      await logoutAll()
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-[var(--text-primary)]">Profile</h1>
        <p className="text-[var(--text-secondary)] mt-1">Manage your account settings and preferences</p>
      </div>

      {error && (
        <Alert variant="error" className="animate-slide-down">
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert variant="success" className="animate-slide-down">
          {success}
        </Alert>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        {/* User Info Card */}
        <Card className="animate-slide-up animate-stagger-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white text-xl font-bold">
                {user?.username?.charAt(0).toUpperCase()}
              </div>
              <div>
                <span className="block">{user?.username}</span>
                <span className="text-sm font-normal text-[var(--text-secondary)]">
                  {user?.is_email_verified ? (
                    <span className="text-emerald-400 flex items-center gap-1">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Verified
                    </span>
                  ) : (
                    <span className="text-amber-400 flex items-center gap-1">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      Unverified
                    </span>
                  )}
                </span>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center py-3 border-b border-[var(--border-color)]">
              <span className="text-[var(--text-secondary)]">Username</span>
              <span className="font-medium">{user?.username}</span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-[var(--border-color)]">
              <span className="text-[var(--text-secondary)]">Email</span>
              <span className="font-medium">{user?.email}</span>
            </div>
            <div className="flex justify-between items-center py-3">
              <span className="text-[var(--text-secondary)]">Member since</span>
              <span className="font-medium">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Tokens Card */}
        <Card className="animate-slide-up animate-stagger-2">
          <CardHeader>
            <CardTitle>Session Tokens</CardTitle>
            <CardDescription>Your current authentication tokens</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm text-[var(--text-secondary)] block mb-2">Access Token</label>
              <div className="p-3 bg-[var(--bg-tertiary)] rounded-xl font-mono text-xs break-all text-[var(--text-muted)] max-h-20 overflow-y-auto">
                {(user?.access_token || accessToken) ? `${(user?.access_token || accessToken || '').substring(0, 50)}...` : 'No token'}
              </div>
            </div>
            <div>
              <label className="text-sm text-[var(--text-secondary)] block mb-2">Refresh Token</label>
              <div className="p-3 bg-[var(--bg-tertiary)] rounded-xl font-mono text-xs break-all text-[var(--text-muted)] max-h-20 overflow-y-auto">
                {(user?.refresh_token || refreshToken) ? `${(user?.refresh_token || refreshToken || '').substring(0, 50)}...` : 'No token'}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Edit Profile Card */}
        <Card className="animate-slide-up animate-stagger-3">
          <CardHeader>
            <CardTitle>Edit Profile</CardTitle>
            <CardDescription>Update your profile information</CardDescription>
          </CardHeader>
          <CardContent>
            {isEditing ? (
              <form onSubmit={handleUpdateProfile} className="space-y-4">
                <Input
                  label="Email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter new email"
                />
                <div className="flex gap-3">
                  <Button type="submit" isLoading={isLoading}>
                    Save Changes
                  </Button>
                  <Button 
                    type="button" 
                    variant="secondary" 
                    onClick={() => {
                      setIsEditing(false)
                      setEmail(user?.email || '')
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            ) : (
              <Button onClick={() => setIsEditing(true)}>
                Edit Profile
              </Button>
            )}
          </CardContent>
        </Card>

        {/* Email Verification Card */}
        {!user?.is_email_verified && (
          <Card className="animate-slide-up animate-stagger-4">
            <CardHeader>
              <CardTitle>Email Verification</CardTitle>
              <CardDescription>Verify your email address to unlock all features</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleVerifyEmail} className="space-y-4">
                <Input
                  label="Verification Code"
                  type="text"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value)}
                  placeholder="Enter the code sent to your email"
                />
                <Button type="submit" isLoading={isVerifying}>
                  Verify Email
                </Button>
              </form>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Session Management Card */}
      <Card className="animate-slide-up animate-stagger-5">
        <CardHeader>
          <CardTitle>Session Management</CardTitle>
          <CardDescription>Manage your active sessions across devices</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <Button variant="secondary" onClick={logout}>
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Logout (This Device)
            </Button>
            <Button variant="danger" onClick={handleLogoutAll}>
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
              </svg>
              Logout All Devices
            </Button>
          </div>
        </CardContent>
        <CardFooter>
          <p className="text-sm text-[var(--text-muted)]">
            Logging out from all devices will invalidate all active sessions and require re-authentication.
          </p>
        </CardFooter>
      </Card>
    </div>
  )
}


