import { apiClient, getErrorMessage } from './api-client'
import axios from 'axios'
import type {
  ThreadsConfig,
  ThreadsPostListItem,
  ThreadsPostFull,
  ThreadsAuthStatus,
} from '@/types/threads'

export const threadsService = {
  async getProfile(): Promise<ThreadsConfig | null> {
    try {
      const response = await apiClient.get<ThreadsConfig>('/threads/profile')
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        return null
      }
      throw new Error(getErrorMessage(error))
    }
  },

  async saveConfig(config: ThreadsConfig): Promise<void> {
    await apiClient.post('/threads/profile', config)
  },

  async createPost(text: string, imageFile?: File): Promise<void> {
    const formData = new FormData()
    formData.append('text', text)
    if (imageFile) {
      formData.append('image', imageFile)
    }
    await apiClient.post('/threads/post', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  async getPosts(): Promise<ThreadsPostListItem[]> {
    const response = await apiClient.get<ThreadsPostListItem[]>('/threads/posts')
    return response.data
  },

  async getPost(id: number): Promise<ThreadsPostFull> {
    const response = await apiClient.get<ThreadsPostFull>(`/threads/post/${id}`)
    return response.data
  },

  async updatePost(id: number, text?: string, imageFile?: File): Promise<void> {
    const formData = new FormData()
    if (text !== undefined) {
      formData.append('text', text)
    }
    if (imageFile) {
      formData.append('image', imageFile)
    }
    await apiClient.put(`/threads/post/${id}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  async deletePost(id: number): Promise<void> {
    await apiClient.delete(`/threads/post/${id}`)
  },

  async getAuthStatus(userId: number): Promise<ThreadsAuthStatus> {
    try {
      const response = await apiClient.get<ThreadsAuthStatus>(
        `/threads-bot/auth/status/${userId}`
      )
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        return {
          user_id: userId,
          connected: false,
          message: 'Profile not found',
        }
      }
      throw new Error(getErrorMessage(error))
    }
  },

  async getAuthUrl(): Promise<{ url: string }> {
    const response = await apiClient.get<{ url: string }>('/threads-bot/auth/url')
    return response.data
  },

  async reloadBot(): Promise<void> {
    try {
      await apiClient.post('/threads-bot/reload')
    } catch (error) {
      console.warn('th-bot reload failed (non-critical):', getErrorMessage(error))
    }
  },
}
