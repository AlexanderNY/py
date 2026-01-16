import { useState, FormEvent, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Alert } from '@/components/ui/alert'
import { customURLService } from '@/services/custom-url-service'
import type { URLConfig } from '@/types/custom-url'

function generateId(): string {
  return Math.random().toString(36).substring(2, 9)
}

export function CustomURLPage() {
  const [collectEnabled, setCollectEnabled] = useState(false)
  const [scrapingScheduleType, setScrapingScheduleType] = useState<'standard' | 'by_intervals'>('standard')
  const [timeIntervals, setTimeIntervals] = useState<Array<{ id: string; start: string; end: string }>>([
    { id: generateId(), start: '', end: '' }
  ])
  const [urlConfigs, setUrlConfigs] = useState<Array<URLConfig & { id: string }>>([
    {
      id: generateId(),
      url: '',
      xpath: '',
      take_screenshot: false,
      target_social_networks: {
        tg: false,
        tw: false,
        vk: false,
        wp: false,
      }
    }
  ])
  
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingSettings, setIsLoadingSettings] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    async function loadSettings() {
      setIsLoadingSettings(true)
      try {
        const settings = await customURLService.getSettings()
        if (settings) {
          setCollectEnabled(settings.collect_enabled)
          setScrapingScheduleType(settings.scraping_schedule_type)
          if (settings.time_intervals && settings.time_intervals.length > 0) {
            setTimeIntervals(settings.time_intervals.map(interval => ({
              id: generateId(),
              start: interval.start,
              end: interval.end
            })))
          }
          if (settings.urls && settings.urls.length > 0) {
            setUrlConfigs(settings.urls.map(url => ({
              id: generateId(),
              ...url
            })))
          }
        }
      } catch (err) {
        // Игнорируем ошибки загрузки настроек
        console.error('Failed to load settings:', err)
      } finally {
        setIsLoadingSettings(false)
      }
    }
    loadSettings()
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

  function addUrlConfig() {
    setUrlConfigs([...urlConfigs, {
      id: generateId(),
      url: '',
      xpath: '',
      take_screenshot: false,
      target_social_networks: {
        tg: false,
        tw: false,
        vk: false,
        wp: false,
      }
    }])
  }

  function removeUrlConfig(id: string) {
    if (urlConfigs.length > 1) {
      setUrlConfigs(urlConfigs.filter(config => config.id !== id))
    }
  }

  function updateUrlConfig(id: string, field: keyof URLConfig, value: any) {
    setUrlConfigs(urlConfigs.map(config => {
      if (config.id === id) {
        if (field === 'target_social_networks') {
          return {
            ...config,
            target_social_networks: {
              ...config.target_social_networks,
              ...value
            }
          }
        }
        return { ...config, [field]: value }
      }
      return config
    }))
  }

  async function handleSaveSettings(e: FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsLoading(true)

    const settings = {
      collect_enabled: collectEnabled,
      scraping_schedule_type: scrapingScheduleType,
      time_intervals: scrapingScheduleType === 'by_intervals' 
        ? timeIntervals.filter(interval => interval.start && interval.end).map(interval => ({
            start: interval.start,
            end: interval.end
          }))
        : undefined,
      urls: urlConfigs.filter(config => config.url && config.xpath).map(config => ({
        url: config.url,
        xpath: config.xpath,
        take_screenshot: config.take_screenshot,
        target_social_networks: config.target_social_networks
      }))
    }

    try {
      await customURLService.saveSettings(settings)
      setSuccess('Settings saved successfully')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save settings')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-[var(--text-primary)]">Custom URL Integration</h1>
        <p className="text-[var(--text-secondary)] mt-1">Configure custom URL scraping and content collection</p>
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

      <form onSubmit={handleSaveSettings}>
        <Card className="animate-slide-up">
          <CardHeader>
            <CardTitle>Custom URL Settings</CardTitle>
            <CardDescription>Configure URL scraping and target social networks</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Collection Checkbox */}
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

            {/* Scraping Schedule */}
            <div className="space-y-4">
              <label className="text-sm font-medium text-[var(--text-secondary)] block">
                Scraping Schedule
              </label>
              <div className="space-y-3">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="radio"
                    name="scrapingSchedule"
                    value="standard"
                    checked={scrapingScheduleType === 'standard'}
                    onChange={(e) => setScrapingScheduleType('standard')}
                    className="w-4 h-4 text-primary-500"
                  />
                  <span className="text-[var(--text-primary)]">Standard periodicity</span>
                </label>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="radio"
                    name="scrapingSchedule"
                    value="by_intervals"
                    checked={scrapingScheduleType === 'by_intervals'}
                    onChange={(e) => setScrapingScheduleType('by_intervals')}
                    className="w-4 h-4 text-primary-500"
                  />
                  <span className="text-[var(--text-primary)]">By time intervals</span>
                </label>
              </div>

              {scrapingScheduleType === 'by_intervals' && (
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

            {/* URL Configs */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-[var(--text-primary)]">URL Configurations</h3>
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={addUrlConfig}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Add URL
                </Button>
              </div>

              {urlConfigs.map((config, index) => (
                <Card key={config.id} className="bg-[var(--bg-secondary)]">
                  <CardContent className="pt-6 space-y-4">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-sm font-medium text-[var(--text-primary)]">URL Configuration {index + 1}</h4>
                      {urlConfigs.length > 1 && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removeUrlConfig(config.id)}
                          className="px-3 text-red-400 hover:text-red-300"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </Button>
                      )}
                    </div>
                    <Input
                      label="URL"
                      type="url"
                      value={config.url}
                      onChange={(e) => updateUrlConfig(config.id, 'url', e.target.value)}
                      placeholder="https://example.com"
                    />
                    <Input
                      label="XPath"
                      type="text"
                      value={config.xpath}
                      onChange={(e) => updateUrlConfig(config.id, 'xpath', e.target.value)}
                      placeholder="//div[@class='content']"
                    />
                    <label className="flex items-center gap-3 cursor-pointer group">
                      <div className="relative">
                        <input
                          type="checkbox"
                          checked={config.take_screenshot}
                          onChange={(e) => updateUrlConfig(config.id, 'take_screenshot', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                        <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                      </div>
                      <span className="text-[var(--text-primary)] group-hover:text-primary-400 transition-colors">
                        Take screenshot
                      </span>
                    </label>
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-[var(--text-secondary)] block">
                        Target Social Networks
                      </label>
                      <div className="grid grid-cols-2 gap-3">
                        {(['tg', 'tw', 'vk', 'wp'] as const).map((network) => (
                          <label key={network} className="flex items-center gap-3 cursor-pointer group">
                            <div className="relative">
                              <input
                                type="checkbox"
                                checked={config.target_social_networks[network] || false}
                                onChange={(e) => updateUrlConfig(config.id, 'target_social_networks', {
                                  [network]: e.target.checked
                                })}
                                className="sr-only peer"
                              />
                              <div className="w-11 h-6 bg-[var(--bg-tertiary)] rounded-full peer-checked:bg-primary-500 transition-colors"></div>
                              <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                            </div>
                            <span className="text-[var(--text-primary)] group-hover:text-primary-400 transition-colors uppercase">
                              {network}
                            </span>
                          </label>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
          <CardFooter>
            <Button type="submit" isLoading={isLoading} className="w-full">
              Save Settings
            </Button>
          </CardFooter>
        </Card>
      </form>
    </div>
  )
}
