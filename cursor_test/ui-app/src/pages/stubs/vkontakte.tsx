import { useState, FormEvent, useEffect, useCallback } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Alert } from '@/components/ui/alert'
import { PageHeader, PageContainer } from '@/components/ui'
import { vkontakteService } from '@/services/vkontakte-service'
import type { VKontakteProfile, VKontaktePostListItem, ScheduleType } from '@/types/vkontakte'

function generateId(): string {
  return Math.random().toString(36).substring(2, 9)
}

interface DynamicField {
  id: string
  value: string
}

const VK_MAX_LENGTH = 15985

export function VKontaktePage() {
  const [activeTab, setActiveTab] = useState<'create' | 'posts' | 'profile' | 'processing'>('create')

  // Profile state
  const [publishEnabled, setPublishEnabled] = useState(false)
  const [collectEnabled, setCollectEnabled] = useState(false)
  const [scheduleType, setScheduleType] = useState<ScheduleType>('immediate')
  const [timeIntervals, setTimeIntervals] = useState<Array<{ id: string; start: string; end: string }>>([
    { id: generateId(), start: '', end: '' },
  ])
  const [ownerId, setOwnerId] = useState('')
  const [friendsOnly, setFriendsOnly] = useState(false)
  const [fromGroup, setFromGroup] = useState(true)
  const [message, setMessage] = useState('')
  const [attachments, setAttachments] = useState('')
  const [signed, setSigned] = useState(false)
  const [markAsAds, setMarkAsAds] = useState(false)
  const [accessToken, setAccessToken] = useState('')
  const [groupsToRead, setGroupsToRead] = useState<DynamicField[]>([{ id: generateId(), value: '' }])
  const [groupToPost, setGroupToPost] = useState('')
  const [processEnabled, setProcessEnabled] = useState(false)
  const [processingDescription, setProcessingDescription] = useState('')
  const [removeEmojis, setRemoveEmojis] = useState(false)
  const [removeImages, setRemoveImages] = useState(false)
  const [cleanHtml, setCleanHtml] = useState(false)
  const [processServiceWordpress, setProcessServiceWordpress] = useState(false)
  const [processServiceTelegram, setProcessServiceTelegram] = useState(false)
  const [processServiceTwitter, setProcessServiceTwitter] = useState(false)
  const [processServiceVkontakte, setProcessServiceVkontakte] = useState(false)
  const [statusReviewAfterProcess, setStatusReviewAfterProcess] = useState(false)
  const [addStaticHtml, setAddStaticHtml] = useState(false)
  const [staticHtmlContent, setStaticHtmlContent] = useState('')

  // Create post state
  const [postText, setPostText] = useState('')
  const [toTg, setToTg] = useState(false)
  const [toTw, setToTw] = useState(false)
  const [toWp, setToWp] = useState(false)
  const [toVk, setToVk] = useState(true)
  const [editingPostId, setEditingPostId] = useState<number | null>(null)

  // Posts list
  const [posts, setPosts] = useState<VKontaktePostListItem[]>([])
  const [isLoadingPosts, setIsLoadingPosts] = useState(false)
  const [hasLoadedPosts, setHasLoadedPosts] = useState(false)
  const [deletingPostId, setDeletingPostId] = useState<number | null>(null)

  const [isLoadingProfile, setIsLoadingProfile] = useState(true)
  const [isSavingProfile, setIsSavingProfile] = useState(false)
  const [isCreatingPost, setIsCreatingPost] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const loadProfile = useCallback(async () => {
    setIsLoadingProfile(true)
    setError('')
    try {
      const profile = await vkontakteService.getProfile()
      if (profile) {
        setPublishEnabled(profile.publish_enabled ?? false)
        setCollectEnabled(profile.collect_enabled ?? false)
        setScheduleType((profile.schedule_type as ScheduleType) ?? 'immediate')
        const ti = profile.time_intervals
        if (Array.isArray(ti) && ti.length > 0 && ti[0]?.start) {
          setTimeIntervals(
            ti.map((interval) => ({
              id: generateId(),
              start: interval.start ?? '',
              end: interval.end ?? '',
            }))
          )
        }
        setOwnerId(profile.owner_id ?? '')
        setFriendsOnly(profile.friends_only ?? false)
        setFromGroup(profile.from_group ?? true)
        setMessage(profile.message ?? '')
        setAttachments(profile.attachments ?? '')
        setSigned(profile.signed ?? false)
        setMarkAsAds(profile.mark_as_ads ?? false)
        setAccessToken(profile.access_token ?? '')
        const gr = profile.groups_to_read
        if (Array.isArray(gr) && gr.length > 0) {
          setGroupsToRead(gr.map((g) => ({ id: generateId(), value: String(g) })))
        }
        setGroupToPost(profile.group_to_post ?? '')
        setProcessEnabled(profile.process_enabled ?? false)
        setProcessingDescription(profile.processing_description ?? '')
        setRemoveEmojis(profile.remove_emojis ?? false)
        setRemoveImages(profile.remove_images ?? false)
        setCleanHtml(profile.clean_html ?? false)
        const ps = profile.process_services
        if (Array.isArray(ps)) {
          setProcessServiceWordpress(ps.includes('wordpress'))
          setProcessServiceTelegram(ps.includes('telegram'))
          setProcessServiceTwitter(ps.includes('twitter'))
          setProcessServiceVkontakte(ps.includes('vkontakte'))
        }
        setStatusReviewAfterProcess(profile.status_review_after_process ?? false)
        setAddStaticHtml(profile.add_static_html ?? false)
        setStaticHtmlContent((profile.static_html_content ?? '').slice(0, 1000))
      }
    } catch (err) {
      console.error('Failed to load profile:', err)
    } finally {
      setIsLoadingProfile(false)
    }
  }, [])

  useEffect(() => {
    loadProfile()
  }, [loadProfile])

  useEffect(() => {
    if (activeTab === 'posts' && !hasLoadedPosts) {
      loadPosts()
    }
  }, [activeTab, hasLoadedPosts])

  async function loadPosts() {
    setIsLoadingPosts(true)
    setError('')
    try {
      const data = await vkontakteService.getPosts()
      setPosts(data)
      setHasLoadedPosts(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load posts')
    } finally {
      setIsLoadingPosts(false)
    }
  }

  async function handleCreatePost(e: FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsCreatingPost(true)
    if (postText.length > VK_MAX_LENGTH) {
      setError(`Post text cannot exceed ${VK_MAX_LENGTH} characters`)
      setIsCreatingPost(false)
      return
    }
    try {
      if (editingPostId !== null) {
        await vkontakteService.updatePost(editingPostId, { text: postText })
        setSuccess('Post updated successfully')
        setEditingPostId(null)
        setPostText('')
        if (hasLoadedPosts) loadPosts()
      } else {
        await vkontakteService.createPost({
          text: postText,
          to_tg: toTg,
          to_tw: toTw,
          to_wp: toWp,
          to_vk: toVk,
        })
        setSuccess('Post created successfully')
        setPostText('')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save post')
    } finally {
      setIsCreatingPost(false)
    }
  }

  async function handleEditPost(id: number) {
    setError('')
    try {
      const post = await vkontakteService.getPost(id)
      setPostText(post.post_text ?? '')
      setEditingPostId(id)
      setActiveTab('create')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load post')
    }
  }

  async function handleDeletePost(id: number) {
    setError('')
    setDeletingPostId(id)
    try {
      await vkontakteService.deletePost(id)
      setSuccess('Post deleted')
      if (hasLoadedPosts) loadPosts()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete post')
    } finally {
      setDeletingPostId(null)
    }
  }

  function buildProfilePayload(): Partial<VKontakteProfile> {
    const timeIntervalsPayload =
      scheduleType === 'intervals'
        ? timeIntervals.filter((i) => i.start && i.end).map(({ start, end }) => ({ start, end }))
        : []
    const groupsToReadPayload = groupsToRead
      .map((f) => f.value.trim())
      .filter(Boolean)
      .map((v) => (v.startsWith('-') ? parseInt(v, 10) : parseInt(v, 10)))
      .filter((n) => !Number.isNaN(n))
    return {
      publish_enabled: publishEnabled,
      collect_enabled: collectEnabled,
      schedule_type: scheduleType,
      time_intervals: timeIntervalsPayload,
      owner_id: ownerId || undefined,
      friends_only: friendsOnly,
      from_group: fromGroup,
      message: message || undefined,
      attachments: attachments || undefined,
      signed: signed,
      mark_as_ads: markAsAds,
      access_token: accessToken && accessToken !== '***' ? accessToken : undefined,
      groups_to_read: groupsToReadPayload,
      group_to_post: groupToPost || undefined,
      process_enabled: processEnabled,
      processing_description: processEnabled ? processingDescription || undefined : undefined,
      remove_emojis: removeEmojis,
      remove_images: removeImages,
      clean_html: cleanHtml,
      process_services: [
        ...(processServiceWordpress ? ['wordpress'] : []),
        ...(processServiceTelegram ? ['telegram'] : []),
        ...(processServiceTwitter ? ['twitter'] : []),
        ...(processServiceVkontakte ? ['vkontakte'] : []),
      ],
      status_review_after_process: statusReviewAfterProcess,
      add_static_html: addStaticHtml,
      static_html_content: addStaticHtml ? staticHtmlContent?.slice(0, 1000) : undefined,
    }
  }

  async function handleSaveProcessing(e: FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsSavingProfile(true)
    try {
      await vkontakteService.saveProfile(buildProfilePayload())
      setSuccess('Processing settings saved successfully')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save processing settings')
    } finally {
      setIsSavingProfile(false)
    }
  }

  async function handleSaveProfile(e: FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsSavingProfile(true)
    try {
      await vkontakteService.saveProfile(buildProfilePayload())
      setSuccess('Profile settings saved successfully')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save profile settings')
    } finally {
      setIsSavingProfile(false)
    }
  }

  function addGroupToRead() {
    setGroupsToRead((prev) => [...prev, { id: generateId(), value: '' }])
  }
  function removeGroupToRead(id: string) {
    if (groupsToRead.length > 1) setGroupsToRead((prev) => prev.filter((f) => f.id !== id))
  }
  function updateGroupToRead(id: string, value: string) {
    setGroupsToRead((prev) => prev.map((f) => (f.id === id ? { ...f, value } : f)))
  }

  function addTimeInterval() {
    if (timeIntervals.length < 5) {
      setTimeIntervals((prev) => [...prev, { id: generateId(), start: '', end: '' }])
    }
  }
  function removeTimeInterval(id: string) {
    if (timeIntervals.length > 1) {
      setTimeIntervals((prev) => prev.filter((i) => i.id !== id))
    }
  }
  function updateTimeInterval(id: string, field: 'start' | 'end', value: string) {
    setTimeIntervals((prev) =>
      prev.map((i) => (i.id === id ? { ...i, [field]: value } : i))
    )
  }

  return (
    <PageContainer maxWidth="wide">
      <PageHeader title="VKontakte Integration" description="Configure your VKontakte account settings and post management" />

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
        {(
          [
            { key: 'create' as const, label: 'Create Post' },
            { key: 'posts' as const, label: 'Posts' },
            { key: 'profile' as const, label: 'Profile Settings' },
            { key: 'processing' as const, label: 'Обработка' },
          ] as const
        ).map(({ key, label }) => (
          <button
            key={key}
            className={`px-6 py-3 text-sm font-medium transition-all relative ${
              activeTab === key ? 'text-primary-400' : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`}
            onClick={() => {
              if (key === 'create') {
                setEditingPostId(null)
                setPostText('')
              }
              setActiveTab(key)
            }}
          >
            {label}
            {activeTab === key && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500" />}
          </button>
        ))}
      </div>

      {/* Create Post */}
      {activeTab === 'create' && (
        <Card className="animate-slide-up">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {editingPostId !== null ? 'Edit VKontakte Post' : 'Create VKontakte Post'}
            </CardTitle>
            <CardDescription>Create or edit a post (max {VK_MAX_LENGTH} characters)</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreatePost} className="space-y-6">
              <div>
                <label className="text-sm font-medium text-[var(--text-secondary)] block mb-2">Post Text</label>
                <textarea
                  value={postText}
                  onChange={(e) => setPostText(e.target.value)}
                  maxLength={VK_MAX_LENGTH}
                  rows={10}
                  className="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
                  placeholder="Enter your post text..."
                />
                <p className="text-xs text-[var(--text-muted)] mt-2">
                  {postText.length} / {VK_MAX_LENGTH} characters
                </p>
              </div>
              {!editingPostId && (
                <div className="space-y-2">
                  <span className="text-sm font-medium text-[var(--text-secondary)] block">Publish to</span>
                  <div className="flex flex-wrap gap-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" checked={toTg} onChange={(e) => setToTg(e.target.checked)} className="w-4 h-4 text-primary-500 rounded" />
                      <span className="text-[var(--text-primary)]">Telegram</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" checked={toTw} onChange={(e) => setToTw(e.target.checked)} className="w-4 h-4 text-primary-500 rounded" />
                      <span className="text-[var(--text-primary)]">Twitter</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" checked={toWp} onChange={(e) => setToWp(e.target.checked)} className="w-4 h-4 text-primary-500 rounded" />
                      <span className="text-[var(--text-primary)]">WordPress</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" checked={toVk} onChange={(e) => setToVk(e.target.checked)} className="w-4 h-4 text-primary-500 rounded" />
                      <span className="text-[var(--text-primary)]">VKontakte</span>
                    </label>
                  </div>
                </div>
              )}
              <CardFooter className="px-0">
                <Button type="submit" isLoading={isCreatingPost} className="w-full sm:w-auto">
                  {editingPostId !== null ? 'Update Post' : 'Create Post'}
                </Button>
              </CardFooter>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Posts */}
      {activeTab === 'posts' && (
        <Card className="animate-slide-up">
          <CardHeader className="flex flex-row items-center justify-between gap-2">
            <div>
              <CardTitle>Posts</CardTitle>
              <CardDescription>Collected and manual VKontakte posts</CardDescription>
            </div>
            <Button type="button" variant="secondary" size="sm" onClick={loadPosts} disabled={isLoadingPosts}>
              Refresh
            </Button>
          </CardHeader>
          <CardContent>
            {isLoadingPosts && posts.length === 0 && (
              <div className="text-center py-8 text-[var(--text-muted)]">Loading posts...</div>
            )}
            {!isLoadingPosts && posts.length === 0 && hasLoadedPosts && (
              <div className="text-center py-8 text-[var(--text-muted)]">No posts found.</div>
            )}
            {!isLoadingPosts && posts.length > 0 && (
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="border-b border-[var(--border-color)] text-left text-[var(--text-secondary)]">
                      <th className="py-2 pr-4 font-medium">Text</th>
                      <th className="py-2 pr-4 font-medium">Status</th>
                      <th className="py-2 pr-4 font-medium">Created</th>
                      <th className="py-2 pr-4 font-medium w-24 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {posts.map((post, index) => (
                      <tr key={post.id ?? index} className="border-b border-[var(--border-color)] last:border-0">
                        <td className="py-2 pr-4 text-[var(--text-primary)] max-w-md truncate">{post.post_text}</td>
                        <td className="py-2 pr-4">
                          <span className="inline-flex items-center rounded-full bg-[var(--bg-secondary)] px-2 py-0.5 text-xs font-medium text-[var(--text-secondary)]">
                            {post.status}
                          </span>
                        </td>
                        <td className="py-2 pr-4 text-[var(--text-secondary)]">
                          {new Date(post.created_at).toLocaleDateString()}
                        </td>
                        <td className="py-2 pr-4 text-right">
                          <div className="flex items-center justify-end gap-1">
                            <button
                              type="button"
                              onClick={() => post.id != null && handleEditPost(post.id)}
                              disabled={post.id == null}
                              className="p-2 rounded-lg text-[var(--text-secondary)] hover:text-primary-400 hover:bg-[var(--bg-secondary)] transition-colors disabled:opacity-50"
                              title="Edit"
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                              </svg>
                            </button>
                            <button
                              type="button"
                              onClick={() => post.id != null && handleDeletePost(post.id)}
                              disabled={post.id == null || deletingPostId === post.id}
                              className="p-2 rounded-lg text-[var(--text-secondary)] hover:text-red-400 hover:bg-[var(--bg-secondary)] transition-colors disabled:opacity-50"
                              title="Delete"
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Profile Settings (Publishing + Collection) */}
      {activeTab === 'profile' && (
        <Card className="animate-slide-up">
          <CardHeader>
            <CardTitle>Profile Settings</CardTitle>
            <CardDescription>Publishing, connection and collection settings</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingProfile ? (
              <div className="text-center py-8 text-[var(--text-muted)]">Loading profile...</div>
            ) : (
              <form onSubmit={handleSaveProfile} className="space-y-8">
                <div className="space-y-4">
                  <h3 className="text-sm font-semibold text-[var(--text-primary)]">Publishing</h3>
                  <label className="flex items-center gap-3 cursor-pointer group">
                    <div className="relative">
                      <input type="checkbox" checked={publishEnabled} onChange={(e) => setPublishEnabled(e.target.checked)} className="sr-only peer" />
                      <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors" />
                      <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5" />
                    </div>
                    <span className="text-[var(--text-primary)]">Enable publishing</span>
                  </label>
                  <label className="flex items-center gap-3 cursor-pointer group">
                    <div className="relative">
                      <input type="checkbox" checked={fromGroup} onChange={(e) => setFromGroup(e.target.checked)} className="sr-only peer" />
                      <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors" />
                      <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5" />
                    </div>
                    <span className="text-[var(--text-primary)]">From group</span>
                  </label>
                  <Input label="Access token (VK)" type="password" value={accessToken} onChange={(e) => setAccessToken(e.target.value)} placeholder="Leave empty to keep current" />
                  <Input label="Group to post (ID or short name)" value={groupToPost} onChange={(e) => setGroupToPost(e.target.value)} placeholder="e.g. 123456 or club123456" />
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-[var(--text-secondary)] block">Publish schedule</label>
                    <div className="space-y-3">
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input type="radio" name="schedule" checked={scheduleType === 'immediate'} onChange={() => setScheduleType('immediate')} className="w-4 h-4 text-primary-500" />
                        <span className="text-[var(--text-primary)]">Immediate</span>
                      </label>
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input type="radio" name="schedule" checked={scheduleType === 'intervals'} onChange={() => setScheduleType('intervals')} className="w-4 h-4 text-primary-500" />
                        <span className="text-[var(--text-primary)]">By time intervals</span>
                      </label>
                    </div>
                    {scheduleType === 'intervals' && (
                      <div className="space-y-3 mt-4">
                        {timeIntervals.map((interval, idx) => (
                          <div key={interval.id} className="flex gap-3 items-end">
                            <Input label={`Interval ${idx + 1} start`} type="time" value={interval.start} onChange={(e) => updateTimeInterval(interval.id, 'start', e.target.value)} className="flex-1" />
                            <Input label="End" type="time" value={interval.end} onChange={(e) => updateTimeInterval(interval.id, 'end', e.target.value)} className="flex-1" />
                            {timeIntervals.length > 1 && (
                              <Button type="button" variant="ghost" size="sm" onClick={() => removeTimeInterval(interval.id)} className="text-red-400 hover:text-red-300">
                                Remove
                              </Button>
                            )}
                          </div>
                        ))}
                        {timeIntervals.length < 5 && (
                          <Button type="button" variant="secondary" size="sm" onClick={addTimeInterval}>
                            Add interval
                          </Button>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                <div className="space-y-4 pt-4 border-t border-[var(--border-color)]">
                  <h3 className="text-sm font-semibold text-[var(--text-primary)]">Collection (Parser)</h3>
                  <label className="flex items-center gap-3 cursor-pointer group">
                    <div className="relative">
                      <input type="checkbox" checked={collectEnabled} onChange={(e) => setCollectEnabled(e.target.checked)} className="sr-only peer" />
                      <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors" />
                      <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5" />
                    </div>
                    <span className="text-[var(--text-primary)]">Enable collection</span>
                  </label>
                  {collectEnabled && (
                    <div className="space-y-4 animate-slide-down">
                      <p className="text-sm text-[var(--text-muted)]">Access token is set in Publishing section above. Here you configure which groups to read from.</p>
                      <div className="p-4 bg-[var(--bg-secondary)] rounded-xl space-y-4 border border-[var(--border-color)]">
                        <h4 className="text-sm font-semibold text-[var(--text-primary)]">Groups to read (wall.get)</h4>
                        <p className="text-xs text-[var(--text-muted)]">Enter VK group IDs (e.g. 123456 or -123456). One per field.</p>
                        {groupsToRead.map((field) => (
                          <div key={field.id} className="flex gap-3">
                            <Input
                              placeholder="e.g. 123456"
                              value={field.value}
                              onChange={(e) => updateGroupToRead(field.id, e.target.value)}
                              className="flex-1"
                            />
                            {groupsToRead.length > 1 && (
                              <Button type="button" variant="ghost" size="sm" onClick={() => removeGroupToRead(field.id)} className="px-3 text-red-400 hover:text-red-300">
                                Remove
                              </Button>
                            )}
                          </div>
                        ))}
                        <Button type="button" variant="secondary" size="sm" onClick={addGroupToRead}>
                          Add group
                        </Button>
                      </div>
                    </div>
                  )}
                </div>

                <CardFooter className="px-0">
                  <Button type="submit" isLoading={isSavingProfile}>Save Profile Settings</Button>
                </CardFooter>
              </form>
            )}
          </CardContent>
        </Card>
      )}

      {/* Обработка */}
      {activeTab === 'processing' && (
        <Card className="animate-slide-up">
          <CardHeader>
            <CardTitle>Обработка</CardTitle>
            <CardDescription>Настройки обработки постов перед публикацией</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingProfile ? (
              <div className="text-center py-8 text-[var(--text-muted)]">Loading profile...</div>
            ) : (
              <form onSubmit={handleSaveProcessing} className="space-y-6">
                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className="relative">
                    <input type="checkbox" checked={processEnabled} onChange={(e) => setProcessEnabled(e.target.checked)} className="sr-only peer" />
                    <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors" />
                    <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5" />
                  </div>
                  <span className="text-[var(--text-primary)]">Обрабатывать перед публикацией</span>
                </label>
                {processEnabled && (
                  <div>
                    <label className="text-sm font-medium text-[var(--text-secondary)] block mb-2">Описание обработки</label>
                    <textarea
                      value={processingDescription}
                      onChange={(e) => setProcessingDescription(e.target.value)}
                      rows={4}
                      className="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-primary-500/50"
                      placeholder="Опишите, как должны обрабатываться посты..."
                    />
                  </div>
                )}
                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className="relative">
                    <input type="checkbox" checked={removeEmojis} onChange={(e) => setRemoveEmojis(e.target.checked)} className="sr-only peer" />
                    <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors" />
                    <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5" />
                  </div>
                  <span className="text-[var(--text-primary)]">Удалить смайлики/эмодзи</span>
                </label>
                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className="relative">
                    <input type="checkbox" checked={removeImages} onChange={(e) => setRemoveImages(e.target.checked)} className="sr-only peer" />
                    <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors" />
                    <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5" />
                  </div>
                  <span className="text-[var(--text-primary)]">Удалить картинки</span>
                </label>
                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className="relative">
                    <input type="checkbox" checked={cleanHtml} onChange={(e) => setCleanHtml(e.target.checked)} className="sr-only peer" />
                    <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors" />
                    <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5" />
                  </div>
                  <span className="text-[var(--text-primary)]">Очистить HTML</span>
                </label>
                <div className="space-y-3">
                  <span className="text-sm font-medium text-[var(--text-secondary)] block">Для каких сервисов подготовить обработку</span>
                  <div className="flex flex-wrap gap-4">
                    {(['wordpress', 'telegram', 'twitter', 'vkontakte'] as const).map((name) => (
                      <label key={name} className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={
                            name === 'wordpress' ? processServiceWordpress : name === 'telegram' ? processServiceTelegram : name === 'twitter' ? processServiceTwitter : processServiceVkontakte
                          }
                          onChange={(e) => {
                            if (name === 'wordpress') setProcessServiceWordpress(e.target.checked)
                            else if (name === 'telegram') setProcessServiceTelegram(e.target.checked)
                            else if (name === 'twitter') setProcessServiceTwitter(e.target.checked)
                            else setProcessServiceVkontakte(e.target.checked)
                          }}
                          className="w-4 h-4 text-primary-500 rounded"
                        />
                        <span className="text-[var(--text-primary)]">{name === 'vkontakte' ? 'VKontakte' : name.charAt(0).toUpperCase() + name.slice(1)}</span>
                      </label>
                    ))}
                  </div>
                </div>
                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className="relative">
                    <input type="checkbox" checked={statusReviewAfterProcess} onChange={(e) => setStatusReviewAfterProcess(e.target.checked)} className="sr-only peer" />
                    <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors" />
                    <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5" />
                  </div>
                  <span className="text-[var(--text-primary)]">Перевести пост в статус review после обработки</span>
                </label>
                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className="relative">
                    <input type="checkbox" checked={addStaticHtml} onChange={(e) => setAddStaticHtml(e.target.checked)} className="sr-only peer" />
                    <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors" />
                    <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5" />
                  </div>
                  <span className="text-[var(--text-primary)]">Добавлять в посты статичный HTML</span>
                </label>
                {addStaticHtml && (
                  <div>
                    <label className="text-sm font-medium text-[var(--text-secondary)] block mb-2">Статичный HTML (до 1000 символов)</label>
                    <textarea
                      value={staticHtmlContent}
                      onChange={(e) => setStaticHtmlContent(e.target.value.slice(0, 1000))}
                      rows={4}
                      maxLength={1000}
                      className="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-primary-500/50"
                    />
                    <p className="text-xs text-[var(--text-muted)]">{staticHtmlContent.length} / 1000</p>
                  </div>
                )}
                <CardFooter className="px-0">
                  <Button type="submit" isLoading={isSavingProfile}>Сохранить настройки обработки</Button>
                </CardFooter>
              </form>
            )}
          </CardContent>
        </Card>
      )}

    </PageContainer>
  )
}
