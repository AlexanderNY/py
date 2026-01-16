export interface CustomURLSettings {
  collect_enabled: boolean
  scraping_schedule_type: 'standard' | 'by_intervals'
  time_intervals?: TimeInterval[]
  urls: URLConfig[]
}

export interface URLConfig {
  url: string
  xpath: string
  take_screenshot: boolean
  target_social_networks: {
    tg?: boolean
    tw?: boolean
    vk?: boolean
    wp?: boolean
  }
}

export interface TimeInterval {
  start: string // HH:MM format
  end: string // HH:MM format
}
