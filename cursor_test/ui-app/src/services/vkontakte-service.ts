import { apiClient, getErrorMessage } from './api-client'
import axios from 'axios'
import type { VKontakteProfile, VKontaktePost } from '@/types/vkontakte'

export const vkontakteService = {
  async getProfile(): Promise<VKontakteProfile | null> {
    try {
      const response = await apiClient.get<VKontakteProfile>('/vk/profile')
      return response.data
    } catch (error) {
      // Если профиль не найден, возвращаем null
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        return null
      }
      throw new Error(getErrorMessage(error))
    }
  },

  async saveProfile(profile: VKontakteProfile): Promise<void> {
    try {
      await apiClient.post('/vk/profile', profile)
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async createPost(post: VKontaktePost): Promise<void> {
    try {
      await apiClient.post('/vk/post', post)
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },
}
