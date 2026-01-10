export interface TelegramConfig {
  collect_messages: boolean
  send_messages: boolean
  api_id: string
  api_hash: string
  chats_to_read: string[]
  save_conditions: string[]
  channel_to_post: string
  should_process: boolean
  processing_description?: string
}

export interface TelegramMessage {
  id: number
  chat_id: number
  text: string
  date: string
  sender_id: number
  sender_name: string
}


