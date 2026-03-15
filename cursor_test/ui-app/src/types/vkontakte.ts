export type ScheduleType = 'immediate' | 'intervals'

export interface TimeInterval {
  start: string // HH:MM
  end?: string
}

export interface VKontakteProfile {
  publish_enabled: boolean
  collect_enabled: boolean
  schedule_type?: ScheduleType
  time_intervals?: TimeInterval[]
  owner_id?: string
  friends_only?: boolean
  from_group?: boolean
  message?: string
  attachments?: string
  signed?: boolean
  mark_as_ads?: boolean
  /** Токен доступа VK (в ответах маскируется как "***") */
  access_token?: string | null
  /** ID групп для чтения стены (например [123456]) */
  groups_to_read?: number[]
  /** ID или short_name группы для публикации */
  group_to_post?: string | null
  process_enabled?: boolean
  processing_description?: string | null
  remove_emojis?: boolean
  remove_images?: boolean
  clean_html?: boolean
  process_services?: string[]
  status_review_after_process?: boolean
  add_static_html?: boolean
  static_html_content?: string | null
}

export interface VKontaktePost {
  text: string
  to_tg?: boolean
  to_tw?: boolean
  to_wp?: boolean
  to_vk?: boolean
  /** URLs or paths of images to attach */
  images?: string[]
}

export interface VKontaktePostListItem {
  id: number
  post_text: string
  images?: string[]
  status: string
  created_at: string
  updated_at: string
  domain?: string
  author?: string
}

export interface VKontakteAttachmentItem {
  type?: string
  path?: string
  url?: string
}

export interface VKontaktePostFull {
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
  attachments?: VKontakteAttachmentItem[]
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
  created_at: string
  updated_at: string
}
