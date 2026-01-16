import { useState, FormEvent, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Alert } from '@/components/ui/alert'
import { telegramService } from '@/services/telegram-service'
import type { TimeInterval } from '@/types/telegram'

interface DynamicField {
  id: string
  value: string
}

function generateId(): string {
  return Math.random().toString(36).substring(2, 9)
}

export function TelegramPage() {
  const [collectMessages, setCollectMessages] = useState(false)
  const [sendMessages, setSendMessages] = useState(false)
  const [publishScheduleType, setPublishScheduleType] = useState<'on_new_messages' | 'by_intervals'>('on_new_messages')
  const [timeIntervals, setTimeIntervals] = useState<Array<{ id: string; start: string; end: string }>>([
    { id: generateId(), start: '', end: '' }
  ])
  const [apiId, setApiId] = useState('')
  const [apiHash, setApiHash] = useState('')
  const [chatsToRead, setChatsToRead] = useState<DynamicField[]>([{ id: generateId(), value: '' }])
  const [saveConditions, setSaveConditions] = useState<DynamicField[]>([{ id: generateId(), value: '' }])
  const [channelToPost, setChannelToPost] = useState('')
  const [shouldProcess, setShouldProcess] = useState(false)
  const [processingDescription, setProcessingDescription] = useState('')
  
  // Post creation state
  const [postText, setPostText] = useState('')
  const [isCreatingPost, setIsCreatingPost] = useState(false)
  
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingProfile, setIsLoadingProfile] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    async function loadProfile() {
      setIsLoadingProfile(true)
      try {
        const profile = await telegramService.getProfile()
        if (profile) {
          setCollectMessages(profile.collect_messages)
          setSendMessages(profile.send_messages)
          setPublishScheduleType(profile.publish_schedule_type || 'on_new_messages')
          if (profile.time_intervals && profile.time_intervals.length > 0) {
            setTimeIntervals(profile.time_intervals.map(interval => ({
              id: generateId(),
              start: interval.start,
              end: interval.end
            })))
          }
          setApiId(profile.api_id || '')
          setApiHash(profile.api_hash || '')
          if (profile.chats_to_read && profile.chats_to_read.length > 0) {
            setChatsToRead(profile.chats_to_read.map(chat => ({ id: generateId(), value: chat })))
          }
          if (profile.save_conditions && profile.save_conditions.length > 0) {
            setSaveConditions(profile.save_conditions.map(condition => ({ id: generateId(), value: condition })))
          }
          setChannelToPost(profile.channel_to_post || '')
          setShouldProcess(profile.should_process)
          setProcessingDescription(profile.processing_description || '')
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

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsLoading(true)

    const config = {
      collect_messages: collectMessages,
      send_messages: sendMessages,
      publish_schedule_type: publishScheduleType,
      time_intervals: publishScheduleType === 'by_intervals' 
        ? timeIntervals.filter(interval => interval.start && interval.end).map(interval => ({
            start: interval.start,
            end: interval.end
          }))
        : undefined,
      api_id: apiId,
      api_hash: apiHash,
      chats_to_read: chatsToRead.map(f => f.value).filter(Boolean),
      save_conditions: saveConditions.map(f => f.value).filter(Boolean),
      channel_to_post: channelToPost,
      should_process: shouldProcess,
      processing_description: shouldProcess ? processingDescription : undefined,
    }

    try {
      await telegramService.saveConfig(config)
      setSuccess('Configuration saved successfully')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save configuration')
    } finally {
      setIsLoading(false)
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
      await telegramService.createPost({ text: postText })
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
        <h1 className="text-3xl font-bold text-[var(--text-primary)]">Telegram Integration</h1>
        <p className="text-[var(--text-secondary)] mt-1">Configure your Telegram bot settings and channel monitoring</p>
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

      <form onSubmit={handleSubmit}>
        <div className="grid gap-6">
          {/* Message Collection Options */}
          <Card className="animate-slide-up animate-stagger-1">
            <CardHeader>
              <CardTitle>Message Options</CardTitle>
              <CardDescription>Configure message collection and sending</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <label className="flex items-center gap-3 cursor-pointer group">
                <div className="relative">
                  <input
                    type="checkbox"
                    checked={collectMessages}
                    onChange={(e) => setCollectMessages(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                  <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                </div>
                <span className="text-[var(--text-primary)] group-hover:text-primary-400 transition-colors">
                  Collect messages
                </span>
              </label>

              <label className="flex items-center gap-3 cursor-pointer group">
                <div className="relative">
                  <input
                    type="checkbox"
                    checked={sendMessages}
                    onChange={(e) => setSendMessages(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                  <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                </div>
                <span className="text-[var(--text-primary)] group-hover:text-primary-400 transition-colors">
                  Send messages
                </span>
              </label>
            </CardContent>
          </Card>

          {/* Publish Schedule */}
          <Card className="animate-slide-up animate-stagger-2">
            <CardHeader>
              <CardTitle>Publish Schedule</CardTitle>
              <CardDescription>Configure when messages should be published</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
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
            </CardContent>
          </Card>

          {/* API Credentials */}
          <Card className="animate-slide-up animate-stagger-3">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary-400" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
                </svg>
                API Credentials
              </CardTitle>
              <CardDescription>Enter your Telegram API credentials from my.telegram.org</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              <Input
                label="API ID"
                type="text"
                placeholder="e.g., 0157230167"
                value={apiId}
                onChange={(e) => setApiId(e.target.value)}
              />
              <Input
                label="API Hash"
                type="text"
                placeholder="e.g., afd10c198eaa94bc4fe3f82415eb46ee67"
                value={apiHash}
                onChange={(e) => setApiHash(e.target.value)}
              />
            </CardContent>
          </Card>

          {/* Chats to Read */}
          <Card className="animate-slide-up animate-stagger-3">
            <CardHeader>
              <CardTitle>Chats to Read</CardTitle>
              <CardDescription>Specify chat IDs to monitor for messages</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {chatsToRead.map((field, index) => (
                <div key={field.id} className="flex gap-3">
                  <Input
                    placeholder={`e.g., -01001677806302`}
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
              <Button
                type="button"
                variant="secondary"
                size="sm"
                onClick={() => addField(setChatsToRead)}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Add Chat
              </Button>
            </CardContent>
          </Card>

          {/* Save Conditions */}
          <Card className="animate-slide-up animate-stagger-4">
            <CardHeader>
              <CardTitle>Save Conditions</CardTitle>
              <CardDescription>Define conditions for saving messages</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
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
              <Button
                type="button"
                variant="secondary"
                size="sm"
                onClick={() => addField(setSaveConditions)}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Add Condition
              </Button>
            </CardContent>
          </Card>

          {/* Channel to Post */}
          <Card className="animate-slide-up animate-stagger-5">
            <CardHeader>
              <CardTitle>Channel to Post</CardTitle>
              <CardDescription>Specify channel ID where messages will be posted</CardDescription>
            </CardHeader>
            <CardContent>
              <Input
                label="Channel ID"
                placeholder="e.g., -1002009872429"
                value={channelToPost}
                onChange={(e) => setChannelToPost(e.target.value)}
              />
            </CardContent>
          </Card>

          {/* Message Processing */}
          <Card className="animate-slide-up animate-stagger-6">
            <CardHeader>
              <CardTitle>Message Processing</CardTitle>
              <CardDescription>Configure how messages should be processed before posting</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <label className="flex items-center gap-3 cursor-pointer group">
                <div className="relative">
                  <input
                    type="checkbox"
                    checked={shouldProcess}
                    onChange={(e) => setShouldProcess(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                  <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                </div>
                <span className="text-[var(--text-primary)] group-hover:text-primary-400 transition-colors">
                  Enable message processing
                </span>
              </label>
              
              {shouldProcess && (
                <div className="animate-slide-down">
                  <Input
                    label="Processing Description"
                    placeholder="Describe how messages should be processed..."
                    value={processingDescription}
                    onChange={(e) => setProcessingDescription(e.target.value)}
                  />
                  <p className="text-sm text-[var(--text-muted)] mt-2">
                    Describe any transformations, filters, or modifications to apply to messages before posting.
                  </p>
                </div>
              )}
            </CardContent>
            <CardFooter>
              <Button type="submit" isLoading={isLoading} className="w-full">
                Save Configuration
              </Button>
            </CardFooter>
          </Card>
        </div>
      </form>

      {/* Post Creation */}
      <Card className="animate-slide-up animate-stagger-7">
        <CardHeader>
          <CardTitle>Telegram Post</CardTitle>
          <CardDescription>Create a new Telegram post (max 4096 characters)</CardDescription>
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
                maxLength={4096}
                rows={8}
                className="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
                placeholder="Enter your post text..."
              />
              <p className="text-xs text-[var(--text-muted)] mt-2">
                {postText.length} / 4096 characters
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


