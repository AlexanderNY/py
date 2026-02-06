import { useState, useEffect, FormEvent } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Alert } from '@/components/ui/alert'
import { telegramService } from '@/services/telegram-service'
import type { TelegramConfig, TelegramPostListItem, TimeInterval, PublishScheduleType } from '@/types/telegram'

function generateId(): string {
  return Math.random().toString(36).substring(2, 9)
}

const SCHEDULE_MINUTES = [0, 15, 30, 45] as const
type ScheduleMinute = (typeof SCHEDULE_MINUTES)[number]

interface DynamicField {
  id: string
  value: string
}

export function TelegramPage() {
  // Tab state
  const [activeTab, setActiveTab] = useState<'create' | 'posts' | 'postProfile' | 'processing' | 'parserProfile'>('create')

  // Profile state
  const [publishEnabled, setPublishEnabled] = useState(false)
  const [collectEnabled, setCollectEnabled] = useState(false)
  const [publishScheduleType, setPublishScheduleType] = useState<PublishScheduleType>('on_new_messages')
  const [publishScheduleHour, setPublishScheduleHour] = useState(9)
  const [publishScheduleMinute, setPublishScheduleMinute] = useState<ScheduleMinute>(0)
  const [apiId, setApiId] = useState('')
  const [apiHash, setApiHash] = useState('')
  const [telegramUsername, setTelegramUsername] = useState('')
  const [channelToPost, setChannelToPost] = useState('')
  const [chatsToRead, setChatsToRead] = useState<DynamicField[]>([{ id: generateId(), value: '' }])
  const [saveConditions, setSaveConditions] = useState<DynamicField[]>([{ id: generateId(), value: '' }])
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

  // Post state
  const [postText, setPostText] = useState('')
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)

  // Posts list state
  const [posts, setPosts] = useState<TelegramPostListItem[]>([])
  const [isLoadingPosts, setIsLoadingPosts] = useState(false)
  const [hasLoadedPosts, setHasLoadedPosts] = useState(false)
  
  // Editing post
  const [editingPostId, setEditingPostId] = useState<number | null>(null)
  const [deletingPostId, setDeletingPostId] = useState<number | null>(null)
  
  // Loading and error states
  const [isLoadingProfile, setIsLoadingProfile] = useState(true)
  const [isSavingProfile, setIsSavingProfile] = useState(false)
  const [isCreatingPost, setIsCreatingPost] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Load profile on mount
  useEffect(() => {
    loadProfile()
  }, [])

  // Load posts when Posts tab is opened first time
  useEffect(() => {
    if (activeTab === 'posts' && !hasLoadedPosts) {
      loadPosts()
    }
  }, [activeTab, hasLoadedPosts])

  async function loadProfile() {
    setIsLoadingProfile(true)
    setError('')
    try {
      const profile = await telegramService.getProfile()
      if (profile) {
        setPublishEnabled(profile.publish_enabled ?? false)
        setCollectEnabled(profile.collect_enabled ?? false)
        setPublishScheduleType((profile.schedule_type as PublishScheduleType) || 'on_new_messages')
        const ti = profile.time_intervals
        if (Array.isArray(ti) && ti.length > 0 && ti[0]?.start) {
          const [h, m] = ti[0].start.split(':').map(Number)
          const hour = Number.isFinite(h) ? Math.max(0, Math.min(23, h)) : 9
          const rawMin = Number.isFinite(m) ? m : 0
          const minute = SCHEDULE_MINUTES.reduce((prev, curr) =>
            Math.abs(curr - rawMin) < Math.abs(prev - rawMin) ? curr : prev
          ) as ScheduleMinute
          setPublishScheduleHour(hour)
          setPublishScheduleMinute(minute)
        }
        setApiId(profile.api_id || '')
        setApiHash(profile.api_hash || '')
        setTelegramUsername(profile.telegram_username || '')
        setChannelToPost(profile.channel_to_post || '')
        if (profile.chats_to_read && profile.chats_to_read.length > 0) {
          setChatsToRead(profile.chats_to_read.map(chat => ({ id: generateId(), value: chat })))
        }
        if (profile.save_conditions && profile.save_conditions.length > 0) {
          setSaveConditions(profile.save_conditions.map(condition => ({ id: generateId(), value: condition })))
        }
        setProcessEnabled(profile.process_enabled ?? false)
        setProcessingDescription(profile.processing_description || '')
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
      console.log('Profile not found, using defaults', err)
    } finally {
      setIsLoadingProfile(false)
    }
  }

  async function loadPosts() {
    setIsLoadingPosts(true)
    setError('')
    try {
      const data = await telegramService.getPosts()
      setPosts(data)
      setHasLoadedPosts(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load posts')
    } finally {
      setIsLoadingPosts(false)
    }
  }

  async function handleDeletePost(postId: number) {
    if (deletingPostId !== null) return
    setDeletingPostId(postId)
    setError('')
    try {
      await telegramService.deletePost(postId)
      setPosts((prev) => prev.filter((p) => p.id !== postId))
      setSuccess('Post deleted successfully')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete post')
    } finally {
      setDeletingPostId(null)
    }
  }

  async function handleEditPost(postId: number) {
    setError('')
    try {
      const post = await telegramService.getPost(postId)
      setPostText(post.post_text ?? '')
      setEditingPostId(postId)
      setImagePreview(post.images && post.images.length > 0 ? post.images[0] : null)
      setImageFile(null)
      setActiveTab('create')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load post for editing')
    }
  }

  async function handleCreatePost(e: FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsCreatingPost(true)

    if (postText.length > 4096) {
      setError('Post text cannot exceed 4096 characters')
      setIsCreatingPost(false)
      return
    }

    try {
      if (editingPostId !== null) {
        await telegramService.updatePost(editingPostId, postText, imageFile || undefined)
        setSuccess('Post updated successfully')
        setEditingPostId(null)
        setPostText('')
        setImageFile(null)
        setImagePreview(null)
        loadPosts()
      } else {
        await telegramService.createPost(postText, imageFile || undefined)
        setSuccess('Post created successfully')
        setPostText('')
        setImageFile(null)
        setImagePreview(null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : (editingPostId !== null ? 'Failed to update post' : 'Failed to create post'))
    } finally {
      setIsCreatingPost(false)
    }
  }

  async function handleSavePostProfile(e: FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsSavingProfile(true)
    const timeIntervals = publishScheduleType === 'by_intervals'
      ? [{ start: `${String(publishScheduleHour).padStart(2, '0')}:${String(publishScheduleMinute).padStart(2, '0')}` }]
      : []
    try {
      await telegramService.saveConfig({
        publish_enabled: publishEnabled,
        collect_enabled: collectEnabled,
        schedule_type: publishScheduleType,
        time_intervals: timeIntervals,
        api_id: apiId || undefined,
        api_hash: apiHash || undefined,
        telegram_username: telegramUsername || undefined,
        chats_to_read: chatsToRead.map(f => f.value).filter(Boolean),
        save_conditions: saveConditions.map(f => f.value).filter(Boolean),
        channel_to_post: channelToPost || undefined,
        process_enabled: processEnabled,
        processing_description: processEnabled ? processingDescription || undefined : undefined,
      })
      setSuccess('Post profile settings saved successfully')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save post profile settings')
    } finally {
      setIsSavingProfile(false)
    }
  }

  async function handleSaveParserProfile(e: FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsSavingProfile(true)
    const timeIntervals = publishScheduleType === 'by_intervals'
      ? [{ start: `${String(publishScheduleHour).padStart(2, '0')}:${String(publishScheduleMinute).padStart(2, '0')}` }]
      : []
    try {
      await telegramService.saveConfig({
        publish_enabled: publishEnabled,
        collect_enabled: collectEnabled,
        schedule_type: publishScheduleType,
        time_intervals: timeIntervals,
        api_id: apiId || undefined,
        api_hash: apiHash || undefined,
        telegram_username: telegramUsername || undefined,
        chats_to_read: chatsToRead.map(f => f.value).filter(Boolean),
        save_conditions: saveConditions.map(f => f.value).filter(Boolean),
        channel_to_post: channelToPost || undefined,
        process_enabled: processEnabled,
        processing_description: processEnabled ? processingDescription || undefined : undefined,
      })
      setSuccess('Parser profile settings saved successfully')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save parser profile settings')
    } finally {
      setIsSavingProfile(false)
    }
  }

  async function handleSaveProcessing(e: FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsSavingProfile(true)
    const timeIntervals = publishScheduleType === 'by_intervals'
      ? [{ start: `${String(publishScheduleHour).padStart(2, '0')}:${String(publishScheduleMinute).padStart(2, '0')}` }]
      : []
    try {
      await telegramService.saveConfig({
        publish_enabled: publishEnabled,
        collect_enabled: collectEnabled,
        schedule_type: publishScheduleType,
        time_intervals: timeIntervals,
        api_id: apiId || undefined,
        api_hash: apiHash || undefined,
        telegram_username: telegramUsername || undefined,
        chats_to_read: chatsToRead.map(f => f.value).filter(Boolean),
        save_conditions: saveConditions.map(f => f.value).filter(Boolean),
        channel_to_post: channelToPost || undefined,
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
        static_html_content: addStaticHtml ? (staticHtmlContent || undefined)?.slice(0, 1000) : undefined,
      })
      setSuccess('Processing settings saved successfully')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save processing settings')
    } finally {
      setIsSavingProfile(false)
    }
  }

  function addField(setter: React.Dispatch<React.SetStateAction<DynamicField[]>>) {
    setter(prev => [...prev, { id: generateId(), value: '' }])
  }

  function removeField(setter: React.Dispatch<React.SetStateAction<DynamicField[]>>, id: string) {
    setter(prev => prev.filter(field => field.id !== id))
  }

  function updateField(
    setter: React.Dispatch<React.SetStateAction<DynamicField[]>>, 
    id: string, 
    value: string
  ) {
    setter(prev => prev.map(field => 
      field.id === id ? { ...field, value } : field
    ))
  }

  function handleImageChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) {
      setImageFile(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  function removeImage() {
    setImageFile(null)
    setImagePreview(null)
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-[var(--text-primary)]">Telegram Integration</h1>
        <p className="text-[var(--text-secondary)] mt-1">Manage your Telegram posts and settings</p>
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
          onClick={() => {
            setEditingPostId(null)
            setPostText('')
            setImageFile(null)
            setImagePreview(null)
            setActiveTab('create')
          }}
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
            activeTab === 'postProfile'
              ? 'text-primary-400'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
          onClick={() => setActiveTab('postProfile')}
        >
          Post Profile Settings
          {activeTab === 'postProfile' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500" />
          )}
        </button>
        <button
          className={`px-6 py-3 text-sm font-medium transition-all relative ${
            activeTab === 'processing'
              ? 'text-primary-400'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
          onClick={() => setActiveTab('processing')}
        >
          Обработка
          {activeTab === 'processing' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500" />
          )}
        </button>
        <button
          className={`px-6 py-3 text-sm font-medium transition-all relative ${
            activeTab === 'parserProfile'
              ? 'text-primary-400'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
          onClick={() => setActiveTab('parserProfile')}
        >
          Parser Profile Settings
          {activeTab === 'parserProfile' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500" />
          )}
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'create' && (
        <Card className="animate-slide-up">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              {editingPostId !== null ? 'Edit Telegram Post' : 'Create Telegram Post'}
            </CardTitle>
            <CardDescription>Create a new Telegram post (max 4096 characters)</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreatePost} className="space-y-6">
              {/* Post Text */}
              <div>
                <label className="text-sm font-medium text-[var(--text-secondary)] block mb-2">
                  Post Text
                </label>
                <textarea
                  value={postText}
                  onChange={(e) => setPostText(e.target.value)}
                  maxLength={4096}
                  rows={8}
                  className="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
                  placeholder="Enter your post text..."
                  required
                />
                <p className="text-xs text-[var(--text-muted)] mt-2">
                  {postText.length} / 4096 characters
                </p>
              </div>

              {/* Image Upload */}
              <div>
                <label className="text-sm font-medium text-[var(--text-secondary)] block mb-2">
                  Image (optional)
                </label>
                {imagePreview ? (
                  <div className="relative">
                    <img src={imagePreview} alt="Preview" className="max-w-full h-auto rounded-xl border border-[var(--border-color)]" />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={removeImage}
                      className="absolute top-2 right-2 text-red-400 hover:text-red-300"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </Button>
                  </div>
                ) : (
                  <div className="border-2 border-dashed border-[var(--border-color)] rounded-xl p-6 text-center">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleImageChange}
                      className="hidden"
                      id="image-upload"
                    />
                    <label htmlFor="image-upload" className="cursor-pointer">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-[var(--text-muted)] mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <p className="text-sm text-[var(--text-secondary)]">Click to upload image</p>
                    </label>
                  </div>
                )}
              </div>

              <CardFooter className="px-0">
                {editingPostId !== null ? (
                  <Button type="submit" isLoading={isCreatingPost} className="w-full sm:w-auto">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Update Post
                  </Button>
                ) : (
                  <Button type="submit" isLoading={isCreatingPost} className="w-full sm:w-auto">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                    Create Post
                  </Button>
                )}
              </CardFooter>
            </form>
          </CardContent>
        </Card>
      )}

      {activeTab === 'posts' && (
        <Card className="animate-slide-up">
          <CardHeader className="flex flex-row items-center justify-between gap-2">
            <div>
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
              <CardDescription>All posts from your Telegram account</CardDescription>
            </div>
            <Button type="button" variant="secondary" size="sm" onClick={loadPosts} isLoading={isLoadingPosts}>
              Refresh
            </Button>
          </CardHeader>
          <CardContent>
            {isLoadingPosts && posts.length === 0 && (
              <div className="text-center py-8 text-[var(--text-muted)]">Loading posts...</div>
            )}

            {!isLoadingPosts && posts.length === 0 && hasLoadedPosts && (
              <div className="text-center py-8 text-[var(--text-muted)]">
                No posts found for this account.
              </div>
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
                      <tr
                        key={post.id ?? index}
                        className="border-b border-[var(--border-color)] last:border-0"
                      >
                        <td className="py-2 pr-4 text-[var(--text-primary)]">
                          <div className="max-w-md truncate">{post.post_text}</div>
                        </td>
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
                              title="Edit post"
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
                              title="Delete post"
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

      {/* Post Profile Settings */}
      {activeTab === 'postProfile' && (
        <Card className="animate-slide-up">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              Post Profile Settings
            </CardTitle>
            <CardDescription>Configure Telegram connection and publishing settings</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingProfile ? (
              <div className="text-center py-8 text-[var(--text-muted)]">Loading profile...</div>
            ) : (
              <form onSubmit={handleSavePostProfile} className="space-y-6">
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

                {publishEnabled && (
                  <div className="p-4 bg-[var(--bg-secondary)] rounded-xl space-y-4 animate-slide-down">
                    <h3 className="text-sm font-semibold text-[var(--text-primary)] flex items-center gap-2">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                      </svg>
                      Telegram Connection
                    </h3>
                    
                    <Input
                      label="API ID"
                      type="text"
                      value={apiId}
                      onChange={(e) => setApiId(e.target.value)}
                      placeholder="e.g., 0157230167"
                    />
                    
                    <Input
                      label="API Hash"
                      type="text"
                      value={apiHash}
                      onChange={(e) => setApiHash(e.target.value)}
                      placeholder="e.g., afd10c198eaa94bc4fe3f82415eb46ee67"
                    />
                    
                    <Input
                      label="Логин в Telegram"
                      type="text"
                      value={telegramUsername}
                      onChange={(e) => setTelegramUsername(e.target.value)}
                      placeholder="e.g., @username"
                    />
                    
                    <p className="text-xs text-[var(--text-muted)]">
                      Get your API credentials from my.telegram.org
                    </p>

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
                          <span className="text-[var(--text-primary)]">When new messages are checked</span>
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
                        <div className="space-y-3 mt-4 animate-slide-down flex flex-wrap gap-4 items-end">
                          <div className="space-y-2 min-w-[6rem]">
                            <label className="text-sm font-medium text-[var(--text-secondary)] block">Hour</label>
                            <select
                              value={publishScheduleHour}
                              onChange={(e) => setPublishScheduleHour(Number(e.target.value))}
                              className="w-full px-4 py-2.5 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-primary-500/50"
                            >
                              {Array.from({ length: 24 }, (_, i) => (
                                <option key={i} value={i}>{String(i).padStart(2, '0')}</option>
                              ))}
                            </select>
                          </div>
                          <div className="space-y-2 min-w-[6rem]">
                            <label className="text-sm font-medium text-[var(--text-secondary)] block">Minutes</label>
                            <select
                              value={publishScheduleMinute}
                              onChange={(e) => setPublishScheduleMinute(Number(e.target.value) as ScheduleMinute)}
                              className="w-full px-4 py-2.5 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-primary-500/50"
                            >
                              {SCHEDULE_MINUTES.map((m) => (
                                <option key={m} value={m}>{String(m).padStart(2, '0')}</option>
                              ))}
                            </select>
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="space-y-4 pt-4 border-t border-[var(--border-color)]">
                      <Input
                        label="Channel to Post"
                        type="text"
                        value={channelToPost}
                        onChange={(e) => setChannelToPost(e.target.value)}
                        placeholder="e.g., -1002009872429"
                      />
                    </div>
                  </div>
                )}

                <CardFooter className="px-0">
                  <Button type="submit" isLoading={isSavingProfile} className="w-full sm:w-auto">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Save Post Profile Settings
                  </Button>
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
            <CardTitle className="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Обработка
            </CardTitle>
            <CardDescription>Настройки обработки постов перед публикацией</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingProfile ? (
              <div className="text-center py-8 text-[var(--text-muted)]">Loading profile...</div>
            ) : (
              <form onSubmit={handleSaveProcessing} className="space-y-6">
                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={processEnabled}
                      onChange={(e) => setProcessEnabled(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                    <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                  </div>
                  <span className="text-[var(--text-primary)] group-hover:text-primary-400 transition-colors">
                    Обрабатывать перед публикацией
                  </span>
                </label>

                {processEnabled && (
                  <div className="space-y-2 animate-slide-down">
                    <label className="text-sm font-medium text-[var(--text-secondary)] block">
                      Описание обработки
                    </label>
                    <textarea
                      value={processingDescription}
                      onChange={(e) => setProcessingDescription(e.target.value)}
                      rows={4}
                      className="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
                      placeholder="Опишите, как должны обрабатываться посты перед публикацией..."
                    />
                  </div>
                )}

                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={removeEmojis}
                      onChange={(e) => setRemoveEmojis(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                    <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                  </div>
                  <span className="text-[var(--text-primary)] group-hover:text-primary-400 transition-colors">
                    Удалить смайлики/эмодзи
                  </span>
                </label>

                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={removeImages}
                      onChange={(e) => setRemoveImages(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                    <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                  </div>
                  <span className="text-[var(--text-primary)] group-hover:text-primary-400 transition-colors">
                    Удалить картинки
                  </span>
                </label>

                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={cleanHtml}
                      onChange={(e) => setCleanHtml(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                    <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                  </div>
                  <span className="text-[var(--text-primary)] group-hover:text-primary-400 transition-colors">
                    Очистить HTML
                  </span>
                </label>

                <div className="space-y-3">
                  <span className="text-sm font-medium text-[var(--text-secondary)] block">Для каких сервисов подготовить обработку</span>
                  <div className="flex flex-wrap gap-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={processServiceWordpress}
                        onChange={(e) => setProcessServiceWordpress(e.target.checked)}
                        className="w-4 h-4 text-primary-500 rounded"
                      />
                      <span className="text-[var(--text-primary)]">WordPress</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={processServiceTelegram}
                        onChange={(e) => setProcessServiceTelegram(e.target.checked)}
                        className="w-4 h-4 text-primary-500 rounded"
                      />
                      <span className="text-[var(--text-primary)]">Telegram</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={processServiceTwitter}
                        onChange={(e) => setProcessServiceTwitter(e.target.checked)}
                        className="w-4 h-4 text-primary-500 rounded"
                      />
                      <span className="text-[var(--text-primary)]">Twitter</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={processServiceVkontakte}
                        onChange={(e) => setProcessServiceVkontakte(e.target.checked)}
                        className="w-4 h-4 text-primary-500 rounded"
                      />
                      <span className="text-[var(--text-primary)]">VKontakte</span>
                    </label>
                  </div>
                </div>

                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={statusReviewAfterProcess}
                      onChange={(e) => setStatusReviewAfterProcess(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                    <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                  </div>
                  <span className="text-[var(--text-primary)] group-hover:text-primary-400 transition-colors">
                    Перевести пост в статус review после обработки
                  </span>
                </label>

                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={addStaticHtml}
                      onChange={(e) => setAddStaticHtml(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                    <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                  </div>
                  <span className="text-[var(--text-primary)] group-hover:text-primary-400 transition-colors">
                    Добавлять в посты статичный HTML
                  </span>
                </label>

                {addStaticHtml && (
                  <div className="space-y-2 animate-slide-down">
                    <label className="text-sm font-medium text-[var(--text-secondary)] block">
                      Статичный HTML (до 1000 символов)
                    </label>
                    <textarea
                      value={staticHtmlContent}
                      onChange={(e) => setStaticHtmlContent(e.target.value.slice(0, 1000))}
                      rows={4}
                      maxLength={1000}
                      className="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
                      placeholder="Введите статичный HTML для добавления в посты..."
                    />
                    <p className="text-xs text-[var(--text-muted)]">{staticHtmlContent.length} / 1000</p>
                  </div>
                )}

                <CardFooter className="px-0">
                  <Button type="submit" isLoading={isSavingProfile} className="w-full sm:w-auto">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Сохранить настройки обработки
                  </Button>
                </CardFooter>
              </form>
            )}
          </CardContent>
        </Card>
      )}

      {/* Parser Profile Settings */}
      {activeTab === 'parserProfile' && (
        <Card className="animate-slide-up">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
              </svg>
              Parser Profile Settings
            </CardTitle>
            <CardDescription>Configure collection (parser) settings</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingProfile ? (
              <div className="text-center py-8 text-[var(--text-muted)]">Loading profile...</div>
            ) : (
              <form onSubmit={handleSaveParserProfile} className="space-y-6">
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

                {collectEnabled && (
                  <div className="space-y-6 animate-slide-down">
                    <div className="p-4 bg-[var(--bg-secondary)] rounded-xl space-y-4 border border-[var(--border-color)]">
                      <h3 className="text-sm font-semibold text-[var(--text-primary)]">Chats to Read</h3>
                      {chatsToRead.map((field, index) => (
                        <div key={field.id} className="flex gap-3">
                          <Input
                            placeholder="e.g., -01001677806302"
                            value={field.value}
                            onChange={(e) => updateField(setChatsToRead, field.id, e.target.value)}
                            className="flex-1"
                          />
                          {chatsToRead.length > 1 && (
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => removeField(setChatsToRead, field.id)}
                              className="px-3 text-red-400 hover:text-red-300"
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </Button>
                          )}
                        </div>
                      ))}
                      <Button type="button" variant="secondary" size="sm" onClick={() => addField(setChatsToRead)}>
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        Add Chat
                      </Button>
                    </div>

                    <div className="p-4 bg-[var(--bg-secondary)] rounded-xl space-y-4 border border-[var(--border-color)]">
                      <h3 className="text-sm font-semibold text-[var(--text-primary)]">Save Conditions</h3>
                      {saveConditions.map((field) => (
                        <div key={field.id} className="flex gap-3">
                          <Input
                            placeholder="Enter condition (e.g., contains keyword)"
                            value={field.value}
                            onChange={(e) => updateField(setSaveConditions, field.id, e.target.value)}
                            className="flex-1"
                          />
                          {saveConditions.length > 1 && (
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => removeField(setSaveConditions, field.id)}
                              className="px-3 text-red-400 hover:text-red-300"
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </Button>
                          )}
                        </div>
                      ))}
                      <Button type="button" variant="secondary" size="sm" onClick={() => addField(setSaveConditions)}>
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        Add Condition
                      </Button>
                    </div>
                  </div>
                )}

                <CardFooter className="px-0">
                  <Button type="submit" isLoading={isSavingProfile} className="w-full sm:w-auto">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Save Parser Profile Settings
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
