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
