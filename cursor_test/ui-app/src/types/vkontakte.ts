export interface VKontakteProfile {
  publish_enabled: boolean
  collect_enabled: boolean
  publish_schedule_type: 'on_new_messages' | 'by_intervals'
  time_intervals?: TimeInterval[]
  owner_id?: string
  friends_only?: boolean
  from_group?: boolean
  message?: string
  attachments?: string
  signed?: boolean
  mark_as_ads?: boolean
}

export interface VKontaktePost {
  text: string
}

export interface TimeInterval {
  start: string // HH:MM format
  end: string // HH:MM format
}
