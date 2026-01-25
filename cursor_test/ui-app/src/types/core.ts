export interface HealthcheckItem {
  service_name: string
  status: 'ok' | 'error'
  error?: string
}

export interface HealthcheckResponse {
  services: HealthcheckItem[]
}

export interface StatisticsItem {
  service_name: string
  collected_posts: number
  processed_posts: number
  published_posts: number
}

export interface StatisticsResponse {
  services: StatisticsItem[]
}

export interface UserStatisticsItem {
  user_id: number
  username: string
  email: string
  role: string
  total_posts: number
  collected_posts: number
  processed_posts: number
  published_posts: number
}

export interface UserStatisticsResponse {
  users: UserStatisticsItem[]
}

export interface ScheduleSnapshot {
  user_id: number
  platform: string
  publish_enabled: boolean
  collect_enabled: boolean
  schedule_type: string
  time_intervals: Array<{ start: string; end: string }>
  updated_at: string
}

export interface ScheduleResponse {
  schedules: ScheduleSnapshot[]
}
