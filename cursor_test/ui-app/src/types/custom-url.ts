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
  /** Время запуска (HH:MM) */
  schedule_time: string
}

export interface CustomURLSettings {
  collect_enabled: boolean
  urls: URLConfig[]
  process_before_publish?: boolean
  process_description?: string
  remove_emojis?: boolean
  remove_images?: boolean
  clean_html?: boolean
  process_services?: string[]
  status_review_after_process?: boolean
  add_static_html?: boolean
  static_html_content?: string
}
