import { apiClient, getErrorMessage } from './api-client'
import axios from 'axios'
import type { TelegramConfig, TelegramPost, TelegramPostListItem, TelegramPostFull } from '@/types/telegram'

export const telegramService = {
  async getProfile(): Promise<TelegramConfig | null> {
    try {
      const response = await apiClient.get<TelegramConfig>('/tg/profile')
      return response.data
    } catch (error) {
      // Если профиль не найден, возвращаем null
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        return null
      }
      throw new Error(getErrorMessage(error))
    }
  },

  async saveConfig(config: TelegramConfig): Promise<void> {
    try {
      await apiClient.post('/tg/profile', config)
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async createPost(text: string, imageFile?: File): Promise<void> {
    try {
      const formData = new FormData()
      formData.append('text', text)
      if (imageFile) {
        formData.append('image', imageFile)
      }
      
      await apiClient.post('/tg/post', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async getPosts(): Promise<TelegramPostListItem[]> {
    try {
      const response = await apiClient.get<TelegramPostListItem[]>('/tg/posts')
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async getPost(id: number): Promise<TelegramPostFull> {
    try {
      const response = await apiClient.get<TelegramPostFull>(`/tg/post/${id}`)
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async updatePost(id: number, text?: string, imageFile?: File): Promise<void> {
    try {
      const formData = new FormData()
      if (text !== undefined) {
        formData.append('text', text)
      }
      if (imageFile) {
        formData.append('image', imageFile)
      }
      
      await apiClient.put(`/tg/post/${id}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async deletePost(id: number): Promise<void> {
    try {
      await apiClient.delete(`/tg/post/${id}`)
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },
}
