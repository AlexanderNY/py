import { useState, FormEvent, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Alert } from '@/components/ui/alert'
import { vkontakteService } from '@/services/vkontakte-service'

function generateId(): string {
  return Math.random().toString(36).substring(2, 9)
}

export function VKontaktePage() {
  const [publishEnabled, setPublishEnabled] = useState(false)
  const [collectEnabled, setCollectEnabled] = useState(false)
  const [publishScheduleType, setPublishScheduleType] = useState<'on_new_messages' | 'by_intervals'>('on_new_messages')
  const [timeIntervals, setTimeIntervals] = useState<Array<{ id: string; start: string; end: string }>>([
    { id: generateId(), start: '', end: '' }
  ])
  const [ownerId, setOwnerId] = useState('')
  const [friendsOnly, setFriendsOnly] = useState(false)
  const [fromGroup, setFromGroup] = useState(false)
  const [message, setMessage] = useState('')
  const [attachments, setAttachments] = useState('')
  const [signed, setSigned] = useState(false)
  const [markAsAds, setMarkAsAds] = useState(false)
  
  const [postText, setPostText] = useState('')
  
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingProfile, setIsLoadingProfile] = useState(true)
  const [isCreatingPost, setIsCreatingPost] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    async function loadProfile() {
      setIsLoadingProfile(true)
      try {
        const profile = await vkontakteService.getProfile()
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
          setOwnerId(profile.owner_id || '')
          setFriendsOnly(profile.friends_only || false)
          setFromGroup(profile.from_group || false)
          setMessage(profile.message || '')
          setAttachments(profile.attachments || '')
          setSigned(profile.signed || false)
          setMarkAsAds(profile.mark_as_ads || false)
        }
      } catch (err) {
        // Игнорируем ошибки загрузки профиля
        console.error('Failed to load profile:', err)
      } finally {
        setIsLoadingProfile(false)
      }
    }
    loadProfile()
  }, [])

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
      owner_id: ownerId || undefined,
      friends_only: friendsOnly,
      from_group: fromGroup,
      message: message || undefined,
      attachments: attachments || undefined,
      signed: signed,
      mark_as_ads: markAsAds,
    }

    try {
      await vkontakteService.saveProfile(profile)
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

    if (postText.length > 15985) {
      setError('Post text cannot exceed 15985 characters')
      setIsCreatingPost(false)
      return
    }

    try {
      await vkontakteService.createPost({ text: postText })
      setSuccess('Post created successfully')
      setPostText('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create post')
    } finally {
      setIsCreatingPost(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-[var(--text-primary)]">VKontakte Integration</h1>
        <p className="text-[var(--text-secondary)] mt-1">Configure your VKontakte account settings and post management</p>
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

      {/* Profile Settings */}
      <form onSubmit={handleSaveProfile}>
        <Card className="animate-slide-up">
          <CardHeader>
            <CardTitle>VKontakte Profile Settings</CardTitle>
            <CardDescription>Configure your VKontakte integration settings</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Checkboxes */}
            <div className="space-y-4">
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

            {/* Publish Schedule */}
            <div className="space-y-4">
              <label className="text-sm font-medium text-[var(--text-secondary)] block">
                Publish Schedule
              </label>
              <div className="space-y-3">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="radio"
                    name="publishSchedule"
                    value="on_new_messages"
                    checked={publishScheduleType === 'on_new_messages'}
                    onChange={(e) => setPublishScheduleType('on_new_messages')}
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
                    onChange={(e) => setPublishScheduleType('by_intervals')}
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

            {/* VKontakte Publishing Data */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-[var(--text-primary)]">Publishing Data</h3>
              <Input
                label="Owner ID"
                type="text"
                value={ownerId}
                onChange={(e) => setOwnerId(e.target.value)}
                placeholder="Owner ID"
              />
              <Input
                label="Message"
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Message"
              />
              <Input
                label="Attachments"
                type="text"
                value={attachments}
                onChange={(e) => setAttachments(e.target.value)}
                placeholder="Attachments"
              />
              <div className="space-y-3">
                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={friendsOnly}
                      onChange={(e) => setFriendsOnly(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                    <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                  </div>
                  <span className="text-[var(--text-primary)] group-hover:text-primary-400 transition-colors">
                    Friends only
                  </span>
                </label>
                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={fromGroup}
                      onChange={(e) => setFromGroup(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                    <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                  </div>
                  <span className="text-[var(--text-primary)] group-hover:text-primary-400 transition-colors">
                    From group
                  </span>
                </label>
                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={signed}
                      onChange={(e) => setSigned(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                    <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                  </div>
                  <span className="text-[var(--text-primary)] group-hover:text-primary-400 transition-colors">
                    Signed
                  </span>
                </label>
                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={markAsAds}
                      onChange={(e) => setMarkAsAds(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                    <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                  </div>
                  <span className="text-[var(--text-primary)] group-hover:text-primary-400 transition-colors">
                    Mark as ads
                  </span>
                </label>
              </div>
            </div>
          </CardContent>
          <CardFooter>
            <Button type="submit" isLoading={isLoading} className="w-full">
              Save Profile Settings
            </Button>
          </CardFooter>
        </Card>
      </form>

      {/* Post Creation */}
      <Card className="animate-slide-up animate-stagger-2">
        <CardHeader>
          <CardTitle>VKontakte Post</CardTitle>
          <CardDescription>Create a new VKontakte post (max 15985 characters)</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCreatePost} className="space-y-4">
            <div>
              <label className="text-sm font-medium text-[var(--text-secondary)] block mb-2">
                Post Text
              </label>
              <textarea
                value={postText}
                onChange={(e) => setPostText(e.target.value)}
                maxLength={15985}
                rows={12}
                className="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
                placeholder="Enter your post text..."
              />
              <p className="text-xs text-[var(--text-muted)] mt-2">
                {postText.length} / 15985 characters
              </p>
            </div>
            <Button type="submit" isLoading={isCreatingPost} className="w-full">
              Create Post
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
