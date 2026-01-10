import { apiClient, getErrorMessage } from './api-client'
import type { WordPressProfile, WordPressPost } from '@/types/wordpress'

export const wordpressService = {
  async getProfile(): Promise<WordPressProfile> {
    try {
      const response = await apiClient.get<WordPressProfile>('/wp/profile')
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async saveProfile(profile: WordPressProfile): Promise<void> {
    try {
      await apiClient.post('/wp/profile', profile)
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async createPost(post: WordPressPost): Promise<void> {
    try {
      await apiClient.post('/wp/post', post)
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },
}
