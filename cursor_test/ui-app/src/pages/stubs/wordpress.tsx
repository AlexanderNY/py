import { useState, useEffect, FormEvent } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Alert } from '@/components/ui/alert'
import { TipTapEditor } from '@/components/ui/tiptap-editor'
import { wordpressService } from '@/services/wordpress-service'
import type { WordPressPost, WordPressPostListItem, PostStatus, PublishScheduleType } from '@/types/wordpress'

function generateId(): string {
  return Math.random().toString(36).substring(2, 9)
}

const SCHEDULE_MINUTES = [0, 15, 30, 45] as const
type ScheduleMinute = (typeof SCHEDULE_MINUTES)[number]

type CollectSiteItem = {
  id: string
  siteUrl: string
  scheduleType: PublishScheduleType
  scheduleHour: number
  scheduleMinute: ScheduleMinute
}

export function WordPressPage() {
  // Tab state
  const [activeTab, setActiveTab] = useState<'create' | 'posts' | 'postProfile' | 'parserProfile'>('create')

  // Profile state
  const [siteUrl, setSiteUrl] = useState('')
  const [username, setUsername] = useState('')
  const [appPassword, setAppPassword] = useState('')
  const [publishEnabled, setPublishEnabled] = useState(false)
  const [collectEnabled, setCollectEnabled] = useState(false)
  const [publishScheduleType, setPublishScheduleType] = useState<'on_new_messages' | 'by_intervals'>('on_new_messages')
  const [publishScheduleHour, setPublishScheduleHour] = useState(9)
  const [publishScheduleMinute, setPublishScheduleMinute] = useState<ScheduleMinute>(0)
  const [collectSites, setCollectSites] = useState<CollectSiteItem[]>([
    { id: generateId(), siteUrl: '', scheduleType: 'on_new_messages', scheduleHour: 9, scheduleMinute: 0 }
  ])
  
  // Post state
  const [postTitle, setPostTitle] = useState('')
  const [postContent, setPostContent] = useState('')
  const [postStatus, setPostStatus] = useState<PostStatus>('draft')
  const [postCategories, setPostCategories] = useState<string[]>([''])
  const [postTags, setPostTags] = useState<string[]>([''])
  const [postExcerpt, setPostExcerpt] = useState('')
  const [postSlug, setPostSlug] = useState('')
  const [featuredMedia, setFeaturedMedia] = useState('')
  const [postMeta, setPostMeta] = useState('')

  // Posts list state
  const [posts, setPosts] = useState<WordPressPostListItem[]>([])
  const [isLoadingPosts, setIsLoadingPosts] = useState(false)
  const [hasLoadedPosts, setHasLoadedPosts] = useState(false)
  
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
      const [publishProfile, collectProfile] = await Promise.all([
        wordpressService.getPublishProfile(),
        wordpressService.getCollectProfile(),
      ])
      setSiteUrl(publishProfile.site_url || '')
      setUsername(publishProfile.username || '')
      setAppPassword(publishProfile.app_password || '')
      setPublishEnabled(publishProfile.publish_enabled ?? false)
      setCollectEnabled(collectProfile.collect_enabled ?? false)
      setPublishScheduleType((publishProfile.schedule_type as PublishScheduleType) || 'on_new_messages')
      const ti = publishProfile.time_intervals
      if (typeof ti === 'string' && ti && ti.includes(':')) {
        const [h, m] = ti.split(':').map(Number)
        const hour = Number.isFinite(h) ? Math.max(0, Math.min(23, h)) : 9
        const rawMin = Number.isFinite(m) ? m : 0
        const minute = SCHEDULE_MINUTES.reduce((prev, curr) =>
          Math.abs(curr - rawMin) < Math.abs(prev - rawMin) ? curr : prev
        ) as ScheduleMinute
        setPublishScheduleHour(hour)
        setPublishScheduleMinute(minute)
      } else if (Array.isArray(ti) && ti.length > 0 && ti[0]?.start) {
        const [h, m] = ti[0].start.split(':').map(Number)
        const hour = Number.isFinite(h) ? Math.max(0, Math.min(23, h)) : 9
        const rawMin = Number.isFinite(m) ? m : 0
        const minute = SCHEDULE_MINUTES.reduce((prev, curr) =>
          Math.abs(curr - rawMin) < Math.abs(prev - rawMin) ? curr : prev
        ) as ScheduleMinute
        setPublishScheduleHour(hour)
        setPublishScheduleMinute(minute)
      }
      if (collectProfile.collect_sites && collectProfile.collect_sites.length > 0) {
        setCollectSites(collectProfile.collect_sites.map((s) => {
          let scheduleHour = 9
          let scheduleMinute: ScheduleMinute = 0
          const ti = s.time_intervals
          if (typeof ti === 'string' && ti && ti.includes(':')) {
            const [h, m] = ti.split(':').map(Number)
            scheduleHour = Number.isFinite(h) ? Math.max(0, Math.min(23, h)) : 9
            const rawMin = Number.isFinite(m) ? m : 0
            scheduleMinute = SCHEDULE_MINUTES.reduce((prev, curr) =>
              Math.abs(curr - rawMin) < Math.abs(prev - rawMin) ? curr : prev
            ) as ScheduleMinute
          }
          return {
            id: generateId(),
            siteUrl: s.site_url || '',
            scheduleType: (s.schedule_type as PublishScheduleType) || 'on_new_messages',
            scheduleHour,
            scheduleMinute,
          }
        }))
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
      const data = await wordpressService.getPosts()
      setPosts(data)
      setHasLoadedPosts(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load posts')
    } finally {
      setIsLoadingPosts(false)
    }
  }

  async function handleSavePostProfile(e: FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsSavingProfile(true)
    const timeIntervals = publishScheduleType === 'by_intervals'
      ? `${String(publishScheduleHour).padStart(2, '0')}:${String(publishScheduleMinute).padStart(2, '0')}`
      : undefined
    try {
      await wordpressService.savePublishProfile({
        publish_enabled: publishEnabled,
        schedule_type: publishScheduleType,
        time_intervals: timeIntervals,
        site_url: siteUrl || undefined,
        username: username || undefined,
        app_password: appPassword || undefined,
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
    const collect_sites = collectSites.map((s) => ({
      site_url: s.siteUrl || undefined,
      schedule_type: s.scheduleType,
      time_intervals: `${String(s.scheduleHour).padStart(2, '0')}:${String(s.scheduleMinute).padStart(2, '0')}`,
    }))
    try {
      await wordpressService.saveCollectProfile({
        collect_enabled: collectEnabled,
        collect_sites,
      })
      setSuccess('Parser profile settings saved successfully')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save parser profile settings')
    } finally {
      setIsSavingProfile(false)
    }
  }

  async function handleCreatePost(e: FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsCreatingPost(true)

    let metaObj: Record<string, any> = {}
    if (postMeta.trim()) {
      try {
        metaObj = JSON.parse(postMeta)
      } catch {
        setError('Invalid JSON format for post.meta')
        setIsCreatingPost(false)
        return
      }
    }

    const post: WordPressPost = {
      post: {
        title: postTitle,
        content: postContent,
        status: postStatus,
        categories: postCategories.filter(c => c.trim()).length > 0 ? postCategories.filter(c => c.trim()) : undefined,
        tags: postTags.filter(t => t.trim()).length > 0 ? postTags.filter(t => t.trim()) : undefined,
        excerpt: postExcerpt || undefined,
        slug: postSlug || undefined,
        featured_media: featuredMedia ? Number(featuredMedia) : undefined,
        meta: Object.keys(metaObj).length > 0 ? metaObj : undefined,
      }
    }

    try {
      await wordpressService.createPost(post)
      setSuccess('Post created successfully')
      // Reset form
      setPostTitle('')
      setPostContent('')
      setPostStatus('draft')
      setPostCategories([''])
      setPostTags([''])
      setPostExcerpt('')
      setPostSlug('')
      setFeaturedMedia('')
      setPostMeta('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create post')
    } finally {
      setIsCreatingPost(false)
    }
  }


  function addCollectSite() {
    if (collectSites.length >= 5) return
    setCollectSites(prev => [...prev, {
      id: generateId(),
      siteUrl: '',
      scheduleType: 'on_new_messages',
      scheduleHour: 9,
      scheduleMinute: 0
    }])
  }

  function removeCollectSite(siteId: string) {
    if (collectSites.length <= 1) return
    setCollectSites(prev => prev.filter(s => s.id !== siteId))
  }

  function updateCollectSiteUrl(siteId: string, value: string) {
    setCollectSites(prev => prev.map(s => s.id === siteId ? { ...s, siteUrl: value } : s))
  }

  function updateCollectSiteScheduleType(siteId: string, value: PublishScheduleType) {
    setCollectSites(prev => prev.map(s => s.id === siteId ? { ...s, scheduleType: value } : s))
  }

  function updateCollectSiteScheduleTime(siteId: string, hour?: number, minute?: ScheduleMinute) {
    setCollectSites(prev => prev.map(s => {
      if (s.id !== siteId) return s
      return {
        ...s,
        ...(hour !== undefined && { scheduleHour: hour }),
        ...(minute !== undefined && { scheduleMinute: minute })
      }
    }))
  }

  function updateStringArray(setter: (arr: string[]) => void, index: number, value: string) {
    setter((prev) => {
      const newArr = [...prev]
      newArr[index] = value
      return newArr
    })
  }

  function addStringArrayField(setter: (arr: string[]) => void) {
    setter(prev => [...prev, ''])
  }

  function removeStringArrayField(setter: (arr: string[]) => void, index: number) {
    setter(prev => prev.filter((_, i) => i !== index))
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-[var(--text-primary)]">WordPress Integration</h1>
        <p className="text-[var(--text-secondary)] mt-1">Manage your WordPress sites and content</p>
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
              Create WordPress Post
            </CardTitle>
            <CardDescription>Create a new post for your WordPress site</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreatePost} className="space-y-6">
              {/* Title */}
              <Input
                label="Title"
                type="text"
                value={postTitle}
                onChange={(e) => setPostTitle(e.target.value)}
                required
                placeholder="Enter post title"
              />

              {/* Content */}
              <div>
                <label className="text-sm font-medium text-[var(--text-secondary)] block mb-2">
                  Content (HTML)
                </label>
                <TipTapEditor
                  content={postContent}
                  onChange={setPostContent}
                  placeholder="Enter post content (HTML supported)"
                  toolbarButtons={['bold', 'italic', 'underline', 'strike', 'heading', 'bulletList', 'orderedList', 'blockquote', 'code', 'codeBlock', 'horizontalRule', 'undo', 'redo']}
                />
              </div>

              {/* Status */}
              <div>
                <label className="text-sm font-medium text-[var(--text-secondary)] block mb-2">
                  Status
                </label>
                <select
                  value={postStatus}
                  onChange={(e) => setPostStatus(e.target.value as PostStatus)}
                  className="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
                >
                  <option value="draft">Draft</option>
                  <option value="publish">Publish</option>
                  <option value="pending">Pending Review</option>
                  <option value="private">Private</option>
                </select>
              </div>

              {/* Categories */}
              <div>
                <label className="text-sm font-medium text-[var(--text-secondary)] block mb-2">
                  Categories (IDs)
                </label>
                {postCategories.map((category, index) => (
                  <div key={index} className="flex gap-3 mb-2">
                    <Input
                      value={category}
                      onChange={(e) => updateStringArray(setPostCategories, index, e.target.value)}
                      placeholder="Enter category ID"
                      className="flex-1"
                    />
                    {postCategories.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeStringArrayField(setPostCategories, index)}
                        className="px-3 text-red-400 hover:text-red-300"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </Button>
                    )}
                  </div>
                ))}
                <Button type="button" variant="secondary" size="sm" onClick={() => addStringArrayField(setPostCategories)}>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Add Category
                </Button>
              </div>

              {/* Tags */}
              <div>
                <label className="text-sm font-medium text-[var(--text-secondary)] block mb-2">
                  Tags (IDs)
                </label>
                {postTags.map((tag, index) => (
                  <div key={index} className="flex gap-3 mb-2">
                    <Input
                      value={tag}
                      onChange={(e) => updateStringArray(setPostTags, index, e.target.value)}
                      placeholder="Enter tag ID"
                      className="flex-1"
                    />
                    {postTags.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeStringArrayField(setPostTags, index)}
                        className="px-3 text-red-400 hover:text-red-300"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </Button>
                    )}
                  </div>
                ))}
                <Button type="button" variant="secondary" size="sm" onClick={() => addStringArrayField(setPostTags)}>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Add Tag
                </Button>
              </div>

              {/* Excerpt */}
              <Input
                label="Excerpt"
                type="text"
                value={postExcerpt}
                onChange={(e) => setPostExcerpt(e.target.value)}
                placeholder="Brief description of the post"
              />

              {/* Slug */}
              <Input
                label="Slug"
                type="text"
                value={postSlug}
                onChange={(e) => setPostSlug(e.target.value)}
                placeholder="URL slug (e.g., my-post-title)"
              />

              {/* Featured Media */}
              <Input
                label="Featured Media ID"
                type="number"
                value={featuredMedia}
                onChange={(e) => setFeaturedMedia(e.target.value)}
                placeholder="ID of the featured image"
              />

              {/* Meta */}
              <div>
                <label className="text-sm font-medium text-[var(--text-secondary)] block mb-2">
                  Meta (JSON)
                </label>
                <textarea
                  value={postMeta}
                  onChange={(e) => setPostMeta(e.target.value)}
                  rows={4}
                  className="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl font-mono text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
                  placeholder='{"key": "value"}'
                />
                <p className="text-xs text-[var(--text-muted)] mt-1">
                  Enter JSON object for additional post metadata
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
              <CardDescription>All posts from your connected WordPress account</CardDescription>
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
                      <th className="py-2 pr-4 font-medium">Title</th>
                      <th className="py-2 pr-4 font-medium">Status</th>
                      <th className="py-2 pr-4 font-medium">Excerpt</th>
                    </tr>
                  </thead>
                  <tbody>
                    {posts.map((post, index) => (
                      <tr
                        key={post.id ?? index}
                        className="border-b border-[var(--border-color)] last:border-0"
                      >
                        <td className="py-2 pr-4 text-[var(--text-primary)]">{post.title}</td>
                        <td className="py-2 pr-4">
                          <span className="inline-flex items-center rounded-full bg-[var(--bg-secondary)] px-2 py-0.5 text-xs font-medium text-[var(--text-secondary)]">
                            {post.status}
                          </span>
                        </td>
                        <td className="py-2 pr-4 text-[var(--text-secondary)]">
                          {post.excerpt || '—'}
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

      {/* Post Profile Settings — publishing only */}
      {activeTab === 'postProfile' && (
        <Card className="animate-slide-up">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              Post Profile Settings
            </CardTitle>
            <CardDescription>Configure WordPress connection and publishing settings</CardDescription>
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
                      WordPress Connection
                    </h3>
                    
                    <Input
                      label="Site URL"
                      type="url"
                      value={siteUrl}
                      onChange={(e) => setSiteUrl(e.target.value)}
                      placeholder="https://example.com"
                    />
                    
                    <Input
                      label="Username"
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder="WordPress username"
                    />
                    
                    <Input
                      label="Application Password"
                      type="password"
                      value={appPassword}
                      onChange={(e) => setAppPassword(e.target.value)}
                      placeholder="Application password (not regular password)"
                    />
                    <p className="text-xs text-[var(--text-muted)]">
                      Generate an Application Password in WordPress: Users → Profile → Application Passwords
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

      {/* Parser Profile Settings — collection only */}
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
                    <h3 className="text-sm font-semibold text-[var(--text-primary)]">Collection sites</h3>
                    {collectSites.map((site, index) => (
                      <div key={site.id} className="p-4 bg-[var(--bg-secondary)] rounded-xl space-y-4 border border-[var(--border-color)]">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-[var(--text-secondary)]">Site {index + 1}</span>
                          {collectSites.length > 1 && (
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => removeCollectSite(site.id)}
                              className="text-red-400 hover:text-red-300"
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                              Remove
                            </Button>
                          )}
                        </div>
                        <Input
                          label="Site URL"
                          type="url"
                          value={site.siteUrl}
                          onChange={(e) => updateCollectSiteUrl(site.id, e.target.value)}
                          placeholder="https://example.com"
                        />
                        <div className="space-y-4">
                          <label className="text-sm font-medium text-[var(--text-secondary)] block">Publish Schedule</label>
                          <div className="space-y-3">
                            <label className="flex items-center gap-3 cursor-pointer">
                              <input
                                type="radio"
                                name={`collectSchedule-${site.id}`}
                                value="on_new_messages"
                                checked={site.scheduleType === 'on_new_messages'}
                                onChange={() => updateCollectSiteScheduleType(site.id, 'on_new_messages')}
                                className="w-4 h-4 text-primary-500"
                              />
                              <span className="text-[var(--text-primary)]">When new messages are checked</span>
                            </label>
                            <label className="flex items-center gap-3 cursor-pointer">
                              <input
                                type="radio"
                                name={`collectSchedule-${site.id}`}
                                value="by_intervals"
                                checked={site.scheduleType === 'by_intervals'}
                                onChange={() => updateCollectSiteScheduleType(site.id, 'by_intervals')}
                                className="w-4 h-4 text-primary-500"
                              />
                              <span className="text-[var(--text-primary)]">By time intervals</span>
                            </label>
                          </div>
                          {site.scheduleType === 'by_intervals' && (
                            <div className="space-y-3 mt-4 flex flex-wrap gap-4 items-end">
                              <div className="space-y-2 min-w-[6rem]">
                                <label className="text-sm font-medium text-[var(--text-secondary)] block">Hour</label>
                                <select
                                  value={site.scheduleHour}
                                  onChange={(e) => updateCollectSiteScheduleTime(site.id, Number(e.target.value))}
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
                                  value={site.scheduleMinute}
                                  onChange={(e) => updateCollectSiteScheduleTime(site.id, undefined, Number(e.target.value) as ScheduleMinute)}
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
                      </div>
                    ))}
                    {collectSites.length < 5 && (
                      <Button type="button" variant="secondary" size="sm" onClick={addCollectSite}>
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        Add collection site
                      </Button>
                    )}
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
