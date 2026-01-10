export interface TimeInterval {
  start: string
  end: string
}

export type PublishScheduleType = 'on_new_messages' | 'by_intervals'

export interface WordPressProfile {
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
    description?: string
    tags?: string[]
    categories?: string[]
    meta?: Record<string, any>
    slug?: string
  }
}
