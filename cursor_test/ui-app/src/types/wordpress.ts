export interface TimeInterval {
  start: string
  end: string
}

export type PublishScheduleType = 'on_new_messages' | 'by_intervals'

export type PostStatus = 'draft' | 'publish' | 'pending' | 'private'

export interface WordPressProfile {
  site_url?: string
  username?: string
  app_password?: string
  publish_enabled: boolean
  collect_enabled: boolean
  publish_schedule_type: PublishScheduleType
  time_intervals?: TimeInterval[]
  collect_sites?: WordPressCollectSiteItem[]
}

/** Профиль публикации WordPress (Post Profile Settings). time_intervals — одно значение "HH:MM". */
export interface WordPressPublishProfile {
  publish_enabled: boolean
  schedule_type?: PublishScheduleType
  time_intervals?: string // "HH:MM"
  site_url?: string
  username?: string
  app_password?: string
}

/** Один сайт сбора: site_url, schedule_type, time_intervals (HH:MM) */
export interface WordPressCollectSiteItem {
  site_url?: string
  schedule_type?: PublishScheduleType
  time_intervals?: string // "HH:MM"
}

/** Профиль сбора WordPress (Parser Profile Settings) */
export interface WordPressCollectProfile {
  collect_enabled: boolean
  collect_sites?: WordPressCollectSiteItem[]
}

export interface WordPressPost {
  pageID?: string
  tagIdList?: number[]
  categoriesIdList?: number[]
  post: {
    title: string
    content: string
    status?: PostStatus
    categories?: string[]
    tags?: string[]
    excerpt?: string
    slug?: string
    featured_media?: number
    meta?: Record<string, any>
  }
}

export interface WordPressPostListItem {
  id?: number
  title: string
  status: PostStatus
  excerpt?: string
}
