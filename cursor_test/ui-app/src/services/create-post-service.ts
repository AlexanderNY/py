import { apiClient, getErrorMessage } from './api-client'
import axios from 'axios'
import type { CreatePostRequest } from '@/types/create-post'

export interface CreatePostProfile {
  social_networks: {
    tg?: boolean
    tw?: boolean
    vk?: boolean
    wp?: boolean
  }
}

export const createPostService = {
  async getProfile(): Promise<CreatePostProfile | null> {
    try {
      const response = await apiClient.get<CreatePostProfile>('/cpost/profile')
      return response.data
    } catch (error) {
      // Если профиль не найден, возвращаем null
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        return null
      }
      throw new Error(getErrorMessage(error))
    }
  },

  async saveProfile(profile: CreatePostProfile): Promise<void> {
    try {
      await apiClient.post('/cpost/profile', profile)
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async createPost(post: CreatePostRequest): Promise<void> {
    try {
      await apiClient.post('/cpost/post', post)
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },
}
