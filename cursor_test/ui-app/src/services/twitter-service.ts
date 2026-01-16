import { apiClient, getErrorMessage } from './api-client'
import axios from 'axios'
import type { TwitterProfile, TwitterPost } from '@/types/twitter'

export const twitterService = {
  async getProfile(): Promise<TwitterProfile | null> {
    try {
      const response = await apiClient.get<TwitterProfile>('/tw/profile')
      return response.data
    } catch (error) {
      // Если профиль не найден, возвращаем null
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        return null
      }
      throw new Error(getErrorMessage(error))
    }
  },

  async saveProfile(profile: TwitterProfile): Promise<void> {
    try {
      await apiClient.post('/tw/profile', profile)
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async createPost(post: TwitterPost): Promise<void> {
    try {
      await apiClient.post('/tw/post', post)
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },
}
