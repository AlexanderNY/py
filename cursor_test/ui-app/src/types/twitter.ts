export interface TwitterProfile {
  publish_enabled: boolean
  collect_enabled: boolean
  publish_schedule_type: 'on_new_messages' | 'by_intervals'
  time_intervals?: TimeInterval[]
  use_proxy?: boolean
  proxy_user?: string
  proxy_pass?: string
  proxy_host?: string
  proxy_port?: number
  username?: string
  password?: string
}

export interface TwitterPost {
  text: string
}

export interface TimeInterval {
  start: string // HH:MM format
  end: string // HH:MM format
}
