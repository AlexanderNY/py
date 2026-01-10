import { useState, useEffect, FormEvent } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Alert } from '@/components/ui/alert'
import { wordpressService } from '@/services/wordpress-service'
import type { WordPressProfile, WordPressPost, TimeInterval } from '@/types/wordpress'

function generateId(): string {
  return Math.random().toString(36).substring(2, 9)
}

export function WordPressPage() {
  // Profile state
  const [publishEnabled, setPublishEnabled] = useState(false)
  const [collectEnabled, setCollectEnabled] = useState(false)
  const [publishScheduleType, setPublishScheduleType] = useState<'on_new_messages' | 'by_intervals'>('on_new_messages')
  const [timeIntervals, setTimeIntervals] = useState<Array<{ id: string; start: string; end: string }>>([
    { id: generateId(), start: '', end: '' }
  ])
  
  // Post state
  const [pageID, setPageID] = useState('')
  const [tagIdList, setTagIdList] = useState<number[]>([])
  const [categoriesIdList, setCategoriesIdList] = useState<number[]>([])
  const [postTitle, setPostTitle] = useState('')
  const [postContent, setPostContent] = useState('')
  const [postDescription, setPostDescription] = useState('')
  const [postTags, setPostTags] = useState<string[]>([''])
  const [postCategories, setPostCategories] = useState<string[]>([''])
  const [postMeta, setPostMeta] = useState('')
  const [postSlug, setPostSlug] = useState('')
  
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

  async function loadProfile() {
    setIsLoadingProfile(true)
    setError('')
    try {
      const profile = await wordpressService.getProfile()
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

  async function handleSaveProfile(e: FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsSavingProfile(true)

    const profile: WordPressProfile = {
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
      pageID: pageID || undefined,
      tagIdList: tagIdList.length > 0 ? tagIdList : undefined,
      categoriesIdList: categoriesIdList.length > 0 ? categoriesIdList : undefined,
      post: {
        title: postTitle,
        content: postContent,
        description: postDescription || undefined,
        tags: postTags.filter(t => t.trim()).length > 0 ? postTags.filter(t => t.trim()) : undefined,
        categories: postCategories.filter(c => c.trim()).length > 0 ? postCategories.filter(c => c.trim()) : undefined,
        meta: Object.keys(metaObj).length > 0 ? metaObj : undefined,
        slug: postSlug || undefined
      }
    }

    try {
      await wordpressService.createPost(post)
      setSuccess('Post created successfully')
      // Reset form
      setPageID('')
      setTagIdList([])
      setCategoriesIdList([])
      setPostTitle('')
      setPostContent('')
      setPostDescription('')
      setPostTags([''])
      setPostCategories([''])
      setPostMeta('')
      setPostSlug('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create post')
    } finally {
      setIsCreatingPost(false)
    }
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

  function addTagId() {
    const input = prompt('Enter tag ID (number):')
    if (input && !isNaN(Number(input))) {
      setTagIdList([...tagIdList, Number(input)])
    }
  }

  function removeTagId(index: number) {
    setTagIdList(tagIdList.filter((_, i) => i !== index))
  }

  function addCategoryId() {
    const input = prompt('Enter category ID (number):')
    if (input && !isNaN(Number(input))) {
      setCategoriesIdList([...categoriesIdList, Number(input)])
    }
  }

  function removeCategoryId(index: number) {
    setCategoriesIdList(categoriesIdList.filter((_, i) => i !== index))
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

      {/* Profile Settings */}
      <Card className="animate-slide-up">
        <CardHeader>
          <CardTitle>WordPress Profile Settings</CardTitle>
          <CardDescription>Configure general WordPress settings</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoadingProfile ? (
            <div className="text-center py-8 text-[var(--text-muted)]">Loading profile...</div>
          ) : (
            <form onSubmit={handleSaveProfile} className="space-y-6">
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
                    <span className="text-[var(--text-primary)]">When new messages are checked</span>
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
                  Save Profile Settings
                </Button>
              </CardFooter>
            </form>
          )}
        </CardContent>
      </Card>

      {/* Create Post */}
      <Card className="animate-slide-up animate-stagger-2">
        <CardHeader>
          <CardTitle>Create WordPress Post</CardTitle>
          <CardDescription>Create a new post for your WordPress site</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCreatePost} className="space-y-6">
            {/* Basic Fields */}
            <div className="grid gap-4 md:grid-cols-2">
              <Input
                label="Page ID"
                type="text"
                value={pageID}
                onChange={(e) => setPageID(e.target.value)}
                placeholder="Optional page ID"
              />
              <Input
                label="Post Slug"
                type="text"
                value={postSlug}
                onChange={(e) => setPostSlug(e.target.value)}
                placeholder="Optional URL slug"
              />
            </div>

            {/* Tag IDs */}
            <div>
              <label className="text-sm font-medium text-[var(--text-secondary)] block mb-2">
                Tag IDs
              </label>
              <div className="flex flex-wrap gap-2 mb-2">
                {tagIdList.map((tagId, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-2 px-3 py-1 bg-primary-500/20 text-primary-400 rounded-full text-sm"
                  >
                    {tagId}
                    <button
                      type="button"
                      onClick={() => removeTagId(index)}
                      className="hover:text-red-400"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
              <Button type="button" variant="secondary" size="sm" onClick={addTagId}>
                Add Tag ID
              </Button>
            </div>

            {/* Category IDs */}
            <div>
              <label className="text-sm font-medium text-[var(--text-secondary)] block mb-2">
                Category IDs
              </label>
              <div className="flex flex-wrap gap-2 mb-2">
                {categoriesIdList.map((catId, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-2 px-3 py-1 bg-accent-500/20 text-accent-400 rounded-full text-sm"
                  >
                    {catId}
                    <button
                      type="button"
                      onClick={() => removeCategoryId(index)}
                      className="hover:text-red-400"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
              <Button type="button" variant="secondary" size="sm" onClick={addCategoryId}>
                Add Category ID
              </Button>
            </div>

            {/* Post Content */}
            <Input
              label="Post Title"
              type="text"
              value={postTitle}
              onChange={(e) => setPostTitle(e.target.value)}
              required
              placeholder="Enter post title"
            />

            <div>
              <label className="text-sm font-medium text-[var(--text-secondary)] block mb-2">
                Post Content
              </label>
              <textarea
                value={postContent}
                onChange={(e) => setPostContent(e.target.value)}
                required
                rows={6}
                className="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
                placeholder="Enter post content"
              />
            </div>

            <Input
              label="Post Description"
              type="text"
              value={postDescription}
              onChange={(e) => setPostDescription(e.target.value)}
              placeholder="Optional description"
            />

            {/* Tags */}
            <div>
              <label className="text-sm font-medium text-[var(--text-secondary)] block mb-2">
                Tags
              </label>
              {postTags.map((tag, index) => (
                <div key={index} className="flex gap-3 mb-2">
                  <Input
                    value={tag}
                    onChange={(e) => updateStringArray(setPostTags, index, e.target.value)}
                    placeholder="Enter tag"
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
                      ×
                    </Button>
                  )}
                </div>
              ))}
              <Button type="button" variant="secondary" size="sm" onClick={() => addStringArrayField(setPostTags)}>
                Add Tag
              </Button>
            </div>

            {/* Categories */}
            <div>
              <label className="text-sm font-medium text-[var(--text-secondary)] block mb-2">
                Categories
              </label>
              {postCategories.map((category, index) => (
                <div key={index} className="flex gap-3 mb-2">
                  <Input
                    value={category}
                    onChange={(e) => updateStringArray(setPostCategories, index, e.target.value)}
                    placeholder="Enter category"
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
                      ×
                    </Button>
                  )}
                </div>
              ))}
              <Button type="button" variant="secondary" size="sm" onClick={() => addStringArrayField(setPostCategories)}>
                Add Category
              </Button>
            </div>

            {/* Meta */}
            <div>
              <label className="text-sm font-medium text-[var(--text-secondary)] block mb-2">
                Post Meta (JSON)
              </label>
              <textarea
                value={postMeta}
                onChange={(e) => setPostMeta(e.target.value)}
                rows={4}
                className="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl font-mono text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
                placeholder='{"key": "value"}'
              />
              <p className="text-xs text-[var(--text-muted)] mt-1">
                Enter JSON object for post metadata
              </p>
            </div>

            <CardFooter className="px-0">
              <Button type="submit" isLoading={isCreatingPost} className="w-full sm:w-auto">
                Create Post
              </Button>
            </CardFooter>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
