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

export interface Notification {
  id: number
  message: string
  user_id?: number | null
  type?: string | null
  created_at: string
}

export interface NotificationResponse {
  notifications: Notification[]
}

export interface NotificationCreate {
  message: string
  user_id?: number | null
  type?: string | null
}

// Admin: services status & posts tables

export interface LoopStatus {
  last_run_at?: string | null
  total_processed: number
  last_cycle_count: number
}

export interface CollectorStatusDetail {
  service: string
  version: string
  collect_interval_sec?: number | null
  distribute_interval_sec?: number | null
  collector?: LoopStatus | null
  distributor?: LoopStatus | null
  error?: string | null
}

export interface ProcessorStatusDetail {
  service: string
  version: string
  process_interval_sec?: number | null
  processor?: LoopStatus | null
  error?: string | null
}

export interface SchedulerStatusDetail {
  service: string
  version: string
  poll_interval_sec?: number | null
  last_poll_at?: string | null
  error?: string | null
}

export interface ServicesStatusResponse {
  healthchecks: HealthcheckItem[]
  collector?: CollectorStatusDetail | null
  processor?: ProcessorStatusDetail | null
  scheduler?: SchedulerStatusDetail | null
}

export interface PlatformMetric {
  platform: string
  table: string
  collected_count: number
  ready_count: number
  processing_count: number
}

export interface PostsTablesResponse {
  platforms: PlatformMetric[]
  posts_table_collector?: Record<string, number> | null
  posts_table_processor?: Record<string, number> | null
  collector_error?: string | null
  processor_error?: string | null
}
