export type ScheduleType = 'immediate' | 'intervals'

export interface TimeInterval {
  start: string
  end?: string
}

export interface InstagramProfile {
  publish_enabled: boolean
  collect_enabled: boolean
  schedule_type?: ScheduleType
  time_intervals?: TimeInterval[]
  username?: string | null
  password?: string | null
  usernames_to_read?: string[]
}

export interface InstagramPost {
  caption: string
  images?: string[]
  to_tg?: boolean
  to_tw?: boolean
  to_wp?: boolean
  to_vk?: boolean
  to_dzen?: boolean
  to_threads?: boolean
  to_instagram?: boolean
}

export interface InstagramPostListItem {
  id: number
  post_text: string
  images?: string[]
  status: string
  created_at: string
  updated_at: string
}

export interface InstagramPostFull {
  id: number
  user_id: number
  post_text: string
  images?: string[]
  status: string
  to_tg: boolean
  to_wp: boolean
  to_vk: boolean
  to_dzen: boolean
  to_threads: boolean
  to_instagram: boolean
  created_at: string
  updated_at: string
}
