import { useState, useEffect, FormEvent, useRef } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Alert } from '@/components/ui/alert'
import { wordpressService } from '@/services/wordpress-service'
import type { WordPressProfile, WordPressPost, WordPressPostListItem, PostStatus } from '@/types/wordpress'

function generateId(): string {
  return Math.random().toString(36).substring(2, 9)
}

export function WordPressPage() {
  // Tab state
  const [activeTab, setActiveTab] = useState<'create' | 'posts' | 'profile'>('create')

  // Profile state
  const [siteUrl, setSiteUrl] = useState('')
  const [username, setUsername] = useState('')
  const [appPassword, setAppPassword] = useState('')
  const [publishEnabled, setPublishEnabled] = useState(false)
  const [collectEnabled, setCollectEnabled] = useState(false)
  const [publishScheduleType, setPublishScheduleType] = useState<'on_new_messages' | 'by_intervals'>('on_new_messages')
  const [timeIntervals, setTimeIntervals] = useState<Array<{ id: string; start: string; end: string }>>([
    { id: generateId(), start: '', end: '' }
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

  // Refs
  const contentRef = useRef<HTMLTextAreaElement | null>(null)

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
      const profile = await wordpressService.getProfile()
      setSiteUrl(profile.site_url || '')
      setUsername(profile.username || '')
      setAppPassword(profile.app_password || '')
      setPublishEnabled(profile.publish_enabled)
      setCollectEnabled(profile.collect_enabled)
      setPublishScheduleType(profile.publish_schedule_type || 'on_new_messages')
      if (profile.time_intervals && profile.time_intervals.length > 0) {
        setTimeIntervals(profile.time_intervals.map(interval => ({
          id: generateId(),
          start: interval.start,
          end: interval.end
        })))
      }
    } catch (err) {
      // If profile doesn't exist, use defaults
      console.log('Profile not found, using defaults')
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

  async function handleSaveProfile(e: FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsSavingProfile(true)

    const profile: WordPressProfile = {
      site_url: siteUrl || undefined,
      username: username || undefined,
      app_password: appPassword || undefined,
      publish_enabled: publishEnabled,
      collect_enabled: collectEnabled,
      publish_schedule_type: publishScheduleType,
      time_intervals: publishScheduleType === 'by_intervals' 
        ? timeIntervals.filter(interval => interval.start && interval.end)
        : undefined
    }

    try {
      await wordpressService.saveProfile(profile)
      setSuccess('Profile settings saved successfully')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save profile settings')
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

  function applyFormatting(tag: 'b' | 'i' | 'u') {
    const textarea = contentRef.current
    if (!textarea) return

    const start = textarea.selectionStart
    const end = textarea.selectionEnd

    if (start === null || end === null || start === undefined || end === undefined) {
      return
    }

    const selectedText = postContent.slice(start, end)
    const openTag = `<${tag}>`
    const closeTag = `</${tag}>`

    let newContent: string
    let cursorPosition: number

    if (selectedText.length === 0) {
      // Insert empty tag and place cursor inside
      newContent = postContent.slice(0, start) + openTag + closeTag + postContent.slice(end)
      cursorPosition = start + openTag.length
    } else {
      // Wrap selected text
      newContent =
        postContent.slice(0, start) +
        openTag +
        selectedText +
        closeTag +
        postContent.slice(end)
      cursorPosition = start + openTag.length + selectedText.length + closeTag.length
    }

    setPostContent(newContent)

    // Restore focus and selection
    requestAnimationFrame(() => {
      textarea.focus()
      textarea.selectionStart = cursorPosition
      textarea.selectionEnd = cursorPosition
    })
  }

  function addTimeInterval() {
    if (timeIntervals.length < 4) {
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
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs text-[var(--text-muted)]">Formatting:</span>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => applyFormatting('b')}
                    className="text-xs font-semibold"
                  >
                    B
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => applyFormatting('i')}
                    className="text-xs italic"
                  >
                    I
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => applyFormatting('u')}
                    className="text-xs underline"
                  >
                    U
                  </Button>
                </div>
                <textarea
                  ref={contentRef}
                  value={postContent}
                  onChange={(e) => setPostContent(e.target.value)}
                  required
                  rows={8}
                  className="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
                  placeholder="Enter post content (HTML supported)"
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

      {activeTab === 'profile' && (
        <Card className="animate-slide-up">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              WordPress Profile Settings
            </CardTitle>
            <CardDescription>Configure your WordPress connection and publishing settings</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingProfile ? (
              <div className="text-center py-8 text-[var(--text-muted)]">Loading profile...</div>
            ) : (
              <form onSubmit={handleSaveProfile} className="space-y-6">
                {/* WordPress Connection */}
                <div className="p-4 bg-[var(--bg-secondary)] rounded-xl space-y-4">
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
                </div>

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
                    <div className="space-y-3 mt-4 animate-slide-down">
                      {timeIntervals.map((interval, index) => (
                        <div key={interval.id} className="flex gap-3 items-end">
                          <Input
                            label={`Interval ${index + 1} Start`}
                            type="time"
                            value={interval.start}
                            onChange={(e) => updateTimeInterval(interval.id, 'start', e.target.value)}
                            className="flex-1"
                          />
                          <Input
                            label={`Interval ${index + 1} End`}
                            type="time"
                            value={interval.end}
                            onChange={(e) => updateTimeInterval(interval.id, 'end', e.target.value)}
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
                      {timeIntervals.length < 4 && (
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

                <CardFooter className="px-0">
                  <Button type="submit" isLoading={isSavingProfile} className="w-full sm:w-auto">
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
