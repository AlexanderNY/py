import { useState, FormEvent, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Alert } from '@/components/ui/alert'
import { twitterService } from '@/services/twitter-service'

function generateId(): string {
  return Math.random().toString(36).substring(2, 9)
}

export function TwitterPage() {
  const [activeTab, setActiveTab] = useState<'create' | 'posts' | 'profile'>('create')

  const [publishEnabled, setPublishEnabled] = useState(false)
  const [collectEnabled, setCollectEnabled] = useState(false)
  const [publishScheduleType, setPublishScheduleType] = useState<'on_new_messages' | 'by_intervals'>('on_new_messages')
  const [timeIntervals, setTimeIntervals] = useState<Array<{ id: string; start: string; end: string }>>([
    { id: generateId(), start: '', end: '' }
  ])
  const [useProxy, setUseProxy] = useState(false)
  const [proxyUser, setProxyUser] = useState('')
  const [proxyPass, setProxyPass] = useState('')
  const [proxyHost, setProxyHost] = useState('')
  const [proxyPort, setProxyPort] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const [postText, setPostText] = useState('')

  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingProfile, setIsLoadingProfile] = useState(true)
  const [isCreatingPost, setIsCreatingPost] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    loadProfile()
  }, [])

  async function loadProfile() {
    setIsLoadingProfile(true)
    try {
      const profile = await twitterService.getProfile()
      if (profile) {
        setPublishEnabled(profile.publish_enabled)
        setCollectEnabled(profile.collect_enabled)
        setPublishScheduleType(profile.publish_schedule_type)
        if (profile.time_intervals && profile.time_intervals.length > 0) {
          setTimeIntervals(profile.time_intervals.map(interval => ({
            id: generateId(),
            start: interval.start,
            end: interval.end
          })))
        }
        setUseProxy(profile.use_proxy || false)
        setProxyUser(profile.proxy_user || '')
        setProxyPass(profile.proxy_pass || '')
        setProxyHost(profile.proxy_host || '')
        setProxyPort(profile.proxy_port?.toString() || '')
        setUsername(profile.username || '')
        setPassword(profile.password || '')
      }
    } catch (err) {
      console.error('Failed to load profile:', err)
    } finally {
      setIsLoadingProfile(false)
    }
  }

  function addTimeInterval() {
    if (timeIntervals.length < 3) {
      setTimeIntervals([...timeIntervals, { id: generateId(), start: '', end: '' }])
    }
  }

  function removeTimeInterval(id: string) {
    if (timeIntervals.length > 1) {
      setTimeIntervals(timeIntervals.filter(interval => interval.id !== id))
    }
  }

  function updateTimeInterval(id: string, field: 'start' | 'end', value: string) {
    setTimeIntervals(timeIntervals.map(interval =>
      interval.id === id ? { ...interval, [field]: value } : interval
    ))
  }

  async function handleSaveProfile(e: FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsLoading(true)

    const profile = {
      publish_enabled: publishEnabled,
      collect_enabled: collectEnabled,
      publish_schedule_type: publishScheduleType,
      time_intervals: publishScheduleType === 'by_intervals'
        ? timeIntervals.filter(interval => interval.start && interval.end).map(interval => ({
            start: interval.start,
            end: interval.end
          }))
        : undefined,
      use_proxy: useProxy,
      proxy_user: useProxy ? proxyUser : undefined,
      proxy_pass: useProxy ? proxyPass : undefined,
      proxy_host: useProxy ? proxyHost : undefined,
      proxy_port: useProxy ? (proxyPort ? Number(proxyPort) : undefined) : undefined,
      username: username || undefined,
      password: password || undefined,
    }

    try {
      await twitterService.saveProfile(profile)
      setSuccess('Profile settings saved successfully')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save profile settings')
    } finally {
      setIsLoading(false)
    }
  }

  async function handleCreatePost(e: FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsCreatingPost(true)

    if (postText.length > 280) {
      setError('Post text cannot exceed 280 characters')
      setIsCreatingPost(false)
      return
    }

    try {
      await twitterService.createPost({ text: postText })
      setSuccess('Post created successfully')
      setPostText('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create post')
    } finally {
      setIsCreatingPost(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-[var(--text-primary)]">Twitter Integration</h1>
        <p className="text-[var(--text-secondary)] mt-1">Manage your Twitter posts and settings</p>
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

      {/* Tabs */}
      <div className="flex border-b border-[var(--border-color)]">
        <button
          className={`px-6 py-3 text-sm font-medium transition-all relative ${
            activeTab === 'create'
              ? 'text-primary-400'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
          onClick={() => setActiveTab('create')}
        >
          Create Post
          {activeTab === 'create' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500" />
          )}
        </button>
        <button
          className={`px-6 py-3 text-sm font-medium transition-all relative ${
            activeTab === 'posts'
              ? 'text-primary-400'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
          onClick={() => setActiveTab('posts')}
        >
          Posts
          {activeTab === 'posts' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500" />
          )}
        </button>
        <button
          className={`px-6 py-3 text-sm font-medium transition-all relative ${
            activeTab === 'profile'
              ? 'text-primary-400'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
          onClick={() => setActiveTab('profile')}
        >
          Profile Settings
          {activeTab === 'profile' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500" />
          )}
        </button>
      </div>

      {/* Create Post tab */}
      {activeTab === 'create' && (
        <Card className="animate-slide-up">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Create Twitter Post
            </CardTitle>
            <CardDescription>Create a new Twitter post (max 280 characters)</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreatePost} className="space-y-6">
              <div>
                <label className="text-sm font-medium text-[var(--text-secondary)] block mb-2">
                  Post Text
                </label>
                <textarea
                  value={postText}
                  onChange={(e) => setPostText(e.target.value)}
                  maxLength={280}
                  rows={6}
                  className="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
                  placeholder="Enter your tweet..."
                  required
                />
                <p className="text-xs text-[var(--text-muted)] mt-2">
                  {postText.length} / 280 characters
                </p>
              </div>
              <CardFooter className="px-0">
                <Button type="submit" isLoading={isCreatingPost} className="w-full sm:w-auto">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                  Create Post
                </Button>
              </CardFooter>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Posts tab */}
      {activeTab === 'posts' && (
        <Card className="animate-slide-up">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6 text-primary-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 10h16M4 14h10"
                />
              </svg>
              Posts
            </CardTitle>
            <CardDescription>All posts from your Twitter account</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-[var(--text-muted)]">
              Listing posts is not supported yet. When the API is available, your posts will appear here.
            </div>
          </CardContent>
        </Card>
      )}

      {/* Profile Settings tab */}
      {activeTab === 'profile' && (
        <Card className="animate-slide-up">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Profile Settings
            </CardTitle>
            <CardDescription>Configure Twitter connection, publishing and collection settings</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingProfile ? (
              <div className="text-center py-8 text-[var(--text-muted)]">Loading profile...</div>
            ) : (
              <form onSubmit={handleSaveProfile} className="space-y-8">
                <div className="space-y-4">
                  <h3 className="text-sm font-semibold text-[var(--text-primary)] flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                    Publishing
                  </h3>
                  <label className="flex items-center gap-3 cursor-pointer group">
                    <div className="relative">
                      <input
                        type="checkbox"
                        checked={publishEnabled}
                        onChange={(e) => setPublishEnabled(e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                      <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                    </div>
                    <span className="text-[var(--text-primary)] group-hover:text-primary-400 transition-colors">
                      Enable publishing
                    </span>
                  </label>

                  <label className="flex items-center gap-3 cursor-pointer group">
                    <div className="relative">
                      <input
                        type="checkbox"
                        checked={collectEnabled}
                        onChange={(e) => setCollectEnabled(e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                      <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                    </div>
                    <span className="text-[var(--text-primary)] group-hover:text-primary-400 transition-colors">
                      Enable collection
                    </span>
                  </label>
                </div>

                <div className="space-y-4 pt-4 border-t border-[var(--border-color)]">
                  <label className="text-sm font-medium text-[var(--text-secondary)] block">Publish Schedule</label>
                  <div className="space-y-3">
                    <label className="flex items-center gap-3 cursor-pointer">
                      <input
                        type="radio"
                        name="publishSchedule"
                        value="on_new_messages"
                        checked={publishScheduleType === 'on_new_messages'}
                        onChange={() => setPublishScheduleType('on_new_messages')}
                        className="w-4 h-4 text-primary-500"
                      />
                      <span className="text-[var(--text-primary)]">Immediately when a new post is detected</span>
                    </label>
                    <label className="flex items-center gap-3 cursor-pointer">
                      <input
                        type="radio"
                        name="publishSchedule"
                        value="by_intervals"
                        checked={publishScheduleType === 'by_intervals'}
                        onChange={() => setPublishScheduleType('by_intervals')}
                        className="w-4 h-4 text-primary-500"
                      />
                      <span className="text-[var(--text-primary)]">By time intervals</span>
                    </label>
                  </div>

                  {publishScheduleType === 'by_intervals' && (
                    <div className="space-y-3 mt-4 animate-slide-down">
                      {timeIntervals.map((interval, index) => (
                        <div key={interval.id} className="flex gap-3 items-end">
                          <Input
                            label={`Interval ${index + 1}`}
                            type="time"
                            value={interval.start}
                            onChange={(e) => updateTimeInterval(interval.id, 'start', e.target.value)}
                            className="flex-1"
                          />
                          {timeIntervals.length > 1 && (
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => removeTimeInterval(interval.id)}
                              className="px-3 text-red-400 hover:text-red-300"
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </Button>
                          )}
                        </div>
                      ))}
                      {timeIntervals.length < 3 && (
                        <Button
                          type="button"
                          variant="secondary"
                          size="sm"
                          onClick={addTimeInterval}
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                          </svg>
                          Add Interval
                        </Button>
                      )}
                    </div>
                  )}
                </div>

                <div className="space-y-4 pt-4 border-t border-[var(--border-color)]">
                  <h3 className="text-sm font-semibold text-[var(--text-primary)]">Proxy</h3>
                  <label className="flex items-center gap-3 cursor-pointer group">
                    <div className="relative">
                      <input
                        type="checkbox"
                        checked={useProxy}
                        onChange={(e) => setUseProxy(e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                      <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                    </div>
                    <span className="text-[var(--text-primary)] group-hover:text-primary-400 transition-colors">
                      Use proxy
                    </span>
                  </label>

                  {useProxy && (
                    <div className="grid gap-4 md:grid-cols-2 animate-slide-down p-4 bg-[var(--bg-secondary)] rounded-xl">
                      <Input
                        label="Proxy User"
                        type="text"
                        value={proxyUser}
                        onChange={(e) => setProxyUser(e.target.value)}
                        placeholder="Proxy username"
                      />
                      <Input
                        label="Proxy Password"
                        type="password"
                        value={proxyPass}
                        onChange={(e) => setProxyPass(e.target.value)}
                        placeholder="Proxy password"
                      />
                      <Input
                        label="Proxy Host"
                        type="text"
                        value={proxyHost}
                        onChange={(e) => setProxyHost(e.target.value)}
                        placeholder="Proxy host"
                      />
                      <Input
                        label="Proxy Port"
                        type="number"
                        value={proxyPort}
                        onChange={(e) => setProxyPort(e.target.value)}
                        placeholder="Proxy port"
                      />
                    </div>
                  )}
                </div>

                <div className="space-y-4 pt-4 border-t border-[var(--border-color)]">
                  <h3 className="text-sm font-semibold text-[var(--text-primary)]">Twitter Connection</h3>
                  <div className="grid gap-4 md:grid-cols-2">
                    <Input
                      label="Twitter Username"
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder="Twitter username"
                    />
                    <Input
                      label="Twitter Password"
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Twitter password"
                    />
                  </div>
                </div>

                <CardFooter className="px-0">
                  <Button type="submit" isLoading={isLoading} className="w-full sm:w-auto">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Save Profile Settings
                  </Button>
                </CardFooter>
              </form>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
