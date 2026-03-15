import { useState, FormEvent, useEffect, useCallback } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Alert } from '@/components/ui/alert'
import { PageHeader, PageContainer } from '@/components/ui'
import { instagramService } from '@/services/instagram-service'
import type { InstagramProfile, InstagramPostListItem, ScheduleType } from '@/types/instagram'

function generateId(): string {
  return Math.random().toString(36).substring(2, 9)
}

interface DynamicField {
  id: string
  value: string
}

const INSTAGRAM_CAPTION_MAX = 2200

export function InstagramPage() {
  const [activeTab, setActiveTab] = useState<'create' | 'posts' | 'profile'>('create')

  const [publishEnabled, setPublishEnabled] = useState(false)
  const [collectEnabled, setCollectEnabled] = useState(false)
  const [scheduleType, setScheduleType] = useState<ScheduleType>('immediate')
  const [timeIntervals, setTimeIntervals] = useState<Array<{ id: string; start: string; end: string }>>([
    { id: generateId(), start: '', end: '' },
  ])
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [usernamesToRead, setUsernamesToRead] = useState<DynamicField[]>([{ id: generateId(), value: '' }])

  const [postCaption, setPostCaption] = useState('')
  const [toTg, setToTg] = useState(false)
  const [toWp, setToWp] = useState(false)
  const [toVk, setToVk] = useState(false)
  const [toDzen, setToDzen] = useState(false)
  const [toInstagram, setToInstagram] = useState(true)
  const [imageFiles, setImageFiles] = useState<FileList | null>(null)
  const [editingPostId, setEditingPostId] = useState<number | null>(null)

  const [posts, setPosts] = useState<InstagramPostListItem[]>([])
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
      const profile = await instagramService.getProfile()
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
        setUsername(profile.username ?? '')
        setPassword('')
        const ur = profile.usernames_to_read
        if (Array.isArray(ur) && ur.length > 0) {
          setUsernamesToRead(ur.map((u) => ({ id: generateId(), value: String(u) })))
        }
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
      const data = await instagramService.getPosts()
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
    if (postCaption.length > INSTAGRAM_CAPTION_MAX) {
      setError(`Caption cannot exceed ${INSTAGRAM_CAPTION_MAX} characters`)
      setIsCreatingPost(false)
      return
    }
    try {
      if (editingPostId !== null) {
        await instagramService.updatePost(editingPostId, { caption: postCaption })
        setSuccess('Post updated successfully')
        setEditingPostId(null)
        setPostCaption('')
        if (hasLoadedPosts) loadPosts()
      } else {
        const hasFiles = imageFiles?.length
        if (hasFiles) {
          const formData = new FormData()
          formData.append('caption', postCaption)
          if (imageFiles) {
            for (let i = 0; i < imageFiles.length; i++) {
              formData.append('images', imageFiles[i])
            }
          }
          await instagramService.createPostWithFiles(formData)
        } else {
          await instagramService.createPost({
            caption: postCaption,
            to_tg: toTg,
            to_wp: toWp,
            to_vk: toVk,
            to_dzen: toDzen,
            to_instagram: toInstagram,
          })
        }
        setSuccess('Post created successfully')
        setPostCaption('')
        setImageFiles(null)
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
      const post = await instagramService.getPost(id)
      setPostCaption(post.post_text ?? '')
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
      await instagramService.deletePost(id)
      setSuccess('Post deleted')
      if (hasLoadedPosts) loadPosts()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete post')
    } finally {
      setDeletingPostId(null)
    }
  }

  function buildProfilePayload(): Partial<InstagramProfile> {
    const timeIntervalsPayload =
      scheduleType === 'intervals'
        ? timeIntervals.filter((i) => i.start && i.end).map(({ start, end }) => ({ start, end }))
        : []
    const usernamesPayload = usernamesToRead.map((f) => f.value.trim()).filter(Boolean)
    return {
      publish_enabled: publishEnabled,
      collect_enabled: collectEnabled,
      schedule_type: scheduleType,
      time_intervals: timeIntervalsPayload,
      username: username || undefined,
      password: password || undefined,
      usernames_to_read: usernamesPayload,
    }
  }

  async function handleSaveProfile(e: FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsSavingProfile(true)
    try {
      await instagramService.saveProfile(buildProfilePayload())
      setSuccess('Profile settings saved successfully')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save profile settings')
    } finally {
      setIsSavingProfile(false)
    }
  }

  function addUsernameToRead() {
    setUsernamesToRead((prev) => [...prev, { id: generateId(), value: '' }])
  }
  function removeUsernameToRead(id: string) {
    if (usernamesToRead.length > 1) setUsernamesToRead((prev) => prev.filter((f) => f.id !== id))
  }
  function updateUsernameToRead(id: string, value: string) {
    setUsernamesToRead((prev) => prev.map((f) => (f.id === id ? { ...f, value } : f)))
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
      <PageHeader
        title="Instagram"
        description="Профиль, сбор постов и публикация (caption до 2200 символов)"
      />

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

      <div className="flex border-b border-[var(--border-color)]">
        {[
          { id: 'create' as const, label: 'Create post' },
          { id: 'posts' as const, label: 'Posts' },
          { id: 'profile' as const, label: 'Profile' },
        ].map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 font-medium border-b-2 -mb-px ${
              activeTab === tab.id
                ? 'border-[var(--accent)] text-[var(--accent)]'
                : 'border-transparent hover:border-[var(--border-color)]'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'profile' && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Instagram profile</CardTitle>
            <CardDescription>Login and accounts to collect posts from</CardDescription>
          </CardHeader>
          <form onSubmit={handleSaveProfile}>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Username</label>
                <Input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="instagram_username"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Password</label>
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Leave blank to keep current"
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="publish_enabled"
                  checked={publishEnabled}
                  onChange={(e) => setPublishEnabled(e.target.checked)}
                />
                <label htmlFor="publish_enabled">Publish enabled</label>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="collect_enabled"
                  checked={collectEnabled}
                  onChange={(e) => setCollectEnabled(e.target.checked)}
                />
                <label htmlFor="collect_enabled">Collect enabled</label>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Usernames to read (one per line or add fields)</label>
                {usernamesToRead.map((f) => (
                  <div key={f.id} className="flex gap-2 mb-2">
                    <Input
                      value={f.value}
                      onChange={(e) => updateUsernameToRead(f.id, e.target.value)}
                      placeholder="@username"
                    />
                    <Button type="button" variant="outline" onClick={() => removeUsernameToRead(f.id)}>
                      Remove
                    </Button>
                  </div>
                ))}
                <Button type="button" variant="outline" onClick={addUsernameToRead}>
                  Add username
                </Button>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Schedule type</label>
                <select
                  value={scheduleType}
                  onChange={(e) => setScheduleType(e.target.value as ScheduleType)}
                  className="border rounded px-2 py-1"
                >
                  <option value="immediate">Immediate</option>
                  <option value="intervals">Intervals</option>
                </select>
              </div>
              {scheduleType === 'intervals' && (
                <div>
                  <label className="block text-sm font-medium mb-1">Time intervals</label>
                  {timeIntervals.map((i) => (
                    <div key={i.id} className="flex gap-2 mb-2">
                      <Input
                        type="time"
                        value={i.start}
                        onChange={(e) => updateTimeInterval(i.id, 'start', e.target.value)}
                      />
                      <Input
                        type="time"
                        value={i.end}
                        onChange={(e) => updateTimeInterval(i.id, 'end', e.target.value)}
                      />
                      <Button type="button" variant="outline" onClick={() => removeTimeInterval(i.id)}>
                        Remove
                      </Button>
                    </div>
                  ))}
                  <Button type="button" variant="outline" onClick={addTimeInterval}>
                    Add interval
                  </Button>
                </div>
              )}
            </CardContent>
            <CardFooter>
              <Button type="submit" disabled={isSavingProfile}>
                {isSavingProfile ? 'Saving...' : 'Save profile'}
              </Button>
            </CardFooter>
          </form>
        </Card>
      )}

      {activeTab === 'create' && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>{editingPostId ? 'Edit post' : 'Create Instagram post'}</CardTitle>
            <CardDescription>Caption max {INSTAGRAM_CAPTION_MAX} characters. Add images for photo/carousel.</CardDescription>
          </CardHeader>
          <form onSubmit={handleCreatePost}>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Caption</label>
                <textarea
                  className="w-full border rounded px-2 py-1 min-h-[120px]"
                  value={postCaption}
                  onChange={(e) => setPostCaption(e.target.value)}
                  maxLength={INSTAGRAM_CAPTION_MAX}
                  placeholder="Post caption..."
                />
                <span className="text-sm text-[var(--muted)]">
                  {postCaption.length} / {INSTAGRAM_CAPTION_MAX}
                </span>
              </div>
              {!editingPostId && (
                <div>
                  <label className="block text-sm font-medium mb-1">Images</label>
                  <Input
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={(e) => setImageFiles(e.target.files || null)}
                  />
                </div>
              )}
              {!editingPostId && (
                <div className="flex flex-wrap gap-4">
                  <label className="flex items-center gap-1">
                    <input type="checkbox" checked={toTg} onChange={(e) => setToTg(e.target.checked)} />
                    TG
                  </label>
                  <label className="flex items-center gap-1">
                    <input type="checkbox" checked={toWp} onChange={(e) => setToWp(e.target.checked)} />
                    WP
                  </label>
                  <label className="flex items-center gap-1">
                    <input type="checkbox" checked={toVk} onChange={(e) => setToVk(e.target.checked)} />
                    VK
                  </label>
                  <label className="flex items-center gap-1">
                    <input type="checkbox" checked={toDzen} onChange={(e) => setToDzen(e.target.checked)} />
                    Dzen
                  </label>
                  <label className="flex items-center gap-1">
                    <input type="checkbox" checked={toInstagram} onChange={(e) => setToInstagram(e.target.checked)} />
                    Instagram
                  </label>
                </div>
              )}
            </CardContent>
            <CardFooter>
              <Button type="submit" disabled={isCreatingPost}>
                {isCreatingPost ? 'Saving...' : editingPostId ? 'Update post' : 'Create post'}
              </Button>
              {editingPostId && (
                <Button type="button" variant="outline" onClick={() => setEditingPostId(null)}>
                  Cancel
                </Button>
              )}
            </CardFooter>
          </form>
        </Card>
      )}

      {activeTab === 'posts' && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Posts</CardTitle>
            <CardDescription>List of Instagram posts</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingPosts ? (
              <p>Loading...</p>
            ) : posts.length === 0 ? (
              <p>No posts yet.</p>
            ) : (
              <ul className="space-y-2">
                {posts.map((post) => (
                  <li
                    key={post.id}
                    className="flex items-center justify-between border rounded p-2"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="truncate">{post.post_text || '(no caption)'}</p>
                      <p className="text-sm text-[var(--muted)]">
                        #{post.id} · {post.status} · {post.created_at}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={() => handleEditPost(post.id)}>
                        Edit
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeletePost(post.id)}
                        disabled={deletingPostId === post.id}
                      >
                        {deletingPostId === post.id ? 'Deleting...' : 'Delete'}
                      </Button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      )}
    </PageContainer>
  )
}
