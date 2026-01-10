import { apiClient, getErrorMessage } from './api-client'
import type { TelegramConfig } from '@/types/telegram'

export const telegramService = {
  async saveConfig(config: TelegramConfig): Promise<void> {
    try {
      await apiClient.post('/tg/config', config)
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },
}
