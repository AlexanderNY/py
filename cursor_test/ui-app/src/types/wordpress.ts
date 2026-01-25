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
