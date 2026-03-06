export type PublishScheduleType = 'on_new_messages' | 'by_intervals'

export interface TimeInterval {
  start: string
  end?: string
}

export interface ThreadsConfig {
  publish_enabled: boolean
  collect_enabled: boolean
  schedule_type?: 'immediate' | 'on_new_messages' | 'by_intervals'
  time_intervals?: TimeInterval[]
  process_enabled: boolean
  processing_description?: string
  remove_emojis?: boolean
  remove_images?: boolean
  clean_html?: boolean
  process_services?: string[]
  status_review_after_process?: boolean
  add_static_html?: boolean
  static_html_content?: string
  threads_connected?: boolean
  threads_user_id?: string
}

export interface ThreadsPostListItem {
  id: number
  post_text: string
  images?: string[]
  status: string
  created_at: string
  updated_at: string
}

export interface ThreadsPostFull {
  id: number
  user_id: number
  domain?: string
  url?: string
  title?: string
  author?: string
  avatar?: string
  post_date?: string
  post_text: string
  screenshot?: string
  images?: string[]
  image_over_text?: string
  comments: number
  reposts: number
  likes: number
  views: number
  is_ad: boolean
  status: string
  post_type?: string
  to_tg: boolean
  to_tw: boolean
  to_wp: boolean
  to_vk: boolean
  to_threads: boolean
  created_at: string
  updated_at: string
}

export interface ThreadsAuthStatus {
  user_id: number
  connected: boolean
  expires_at?: string | null
  message: string
}
