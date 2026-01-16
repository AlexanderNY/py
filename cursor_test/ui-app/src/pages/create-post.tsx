import { useState, FormEvent, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Alert } from '@/components/ui/alert'
import { createPostService } from '@/services/create-post-service'

export function CreatePostPage() {
  const [socialNetworks, setSocialNetworks] = useState({
    tg: false,
    tw: false,
    vk: false,
    wp: false,
  })
  const [postText, setPostText] = useState('')
  
  const [isCreating, setIsCreating] = useState(false)
  const [isLoadingProfile, setIsLoadingProfile] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    async function loadProfile() {
      setIsLoadingProfile(true)
      try {
        const profile = await createPostService.getProfile()
        if (profile) {
          setSocialNetworks({
            tg: profile.social_networks.tg || false,
            tw: profile.social_networks.tw || false,
            vk: profile.social_networks.vk || false,
            wp: profile.social_networks.wp || false,
          })
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

  function toggleSocialNetwork(network: keyof typeof socialNetworks) {
    setSocialNetworks(prev => ({
      ...prev,
      [network]: !prev[network]
    }))
  }

  async function handleSaveProfile(e: FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    
    try {
      await createPostService.saveProfile({
        social_networks: socialNetworks
      })
      setSuccess('Profile settings saved successfully')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save profile settings')
    }
  }

  async function handleCreatePost(e: FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsCreating(true)

    // Check if at least one social network is selected
    if (!Object.values(socialNetworks).some(Boolean)) {
      setError('Please select at least one social network')
      setIsCreating(false)
      return
    }

    if (postText.length > 15985) {
      setError('Post text cannot exceed 15985 characters')
      setIsCreating(false)
      return
    }

    if (!postText.trim()) {
      setError('Post text cannot be empty')
      setIsCreating(false)
      return
    }

    try {
      await createPostService.createPost({
        social_networks: socialNetworks,
        text: postText
      })
      setSuccess('Post created successfully')
      setPostText('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create post')
    } finally {
      setIsCreating(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-[var(--text-primary)]">Create Post</h1>
        <p className="text-[var(--text-secondary)] mt-1">Create a new post for selected social networks</p>
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
          <CardTitle>Profile Settings</CardTitle>
          <CardDescription>Select target social networks for posts</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSaveProfile} className="space-y-6">
            {/* Social Networks Selection */}
            <div className="space-y-4">
              <label className="text-sm font-medium text-[var(--text-secondary)] block">
                Target Social Networks
              </label>
              <div className="grid grid-cols-2 gap-4">
                {(['tg', 'tw', 'vk', 'wp'] as const).map((network) => (
                  <label key={network} className="flex items-center gap-3 cursor-pointer group p-4 rounded-xl border border-[var(--border-color)] hover:border-primary-500/50 transition-colors">
                    <div className="relative">
                      <input
                        type="checkbox"
                        checked={socialNetworks[network]}
                        onChange={() => toggleSocialNetwork(network)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                      <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                    </div>
                    <span className="text-[var(--text-primary)] group-hover:text-primary-400 transition-colors font-medium uppercase">
                      {network === 'tg' ? 'Telegram' : network === 'tw' ? 'Twitter' : network === 'vk' ? 'VKontakte' : 'WordPress'}
                    </span>
                  </label>
                ))}
              </div>
            </div>
            <CardFooter className="px-0">
              <Button type="submit" className="w-full">
                Save Profile Settings
              </Button>
            </CardFooter>
          </form>
        </CardContent>
      </Card>

      {/* Post Creation */}
      <Card className="animate-slide-up animate-stagger-2">
        <CardHeader>
          <CardTitle>New Post</CardTitle>
          <CardDescription>Enter your post content</CardDescription>
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
                maxLength={15985}
                rows={12}
                className="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
                placeholder="Enter your post text..."
                required
              />
              <p className="text-xs text-[var(--text-muted)] mt-2">
                {postText.length} / 15985 characters
              </p>
            </div>

            <CardFooter className="px-0">
              <Button type="submit" isLoading={isCreating} className="w-full">
                Create Post
              </Button>
            </CardFooter>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
