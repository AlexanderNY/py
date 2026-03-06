import { apiClient, getErrorMessage } from './api-client'
import axios from 'axios'
import type {
  VKontakteProfile,
  VKontaktePost,
  VKontaktePostListItem,
  VKontaktePostFull,
} from '@/types/vkontakte'

export const vkontakteService = {
  async getProfile(): Promise<VKontakteProfile | null> {
    try {
      const response = await apiClient.get<VKontakteProfile>('/vk/profile')
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        return null
      }
      throw new Error(getErrorMessage(error))
    }
  },

  async saveProfile(profile: Partial<VKontakteProfile>): Promise<VKontakteProfile> {
    const response = await apiClient.post<VKontakteProfile>('/vk/profile', profile)
    return response.data
  },

  async createPost(post: VKontaktePost): Promise<unknown> {
    await apiClient.post('/vk/post', post)
  },

  async getPosts(limit = 50, offset = 0): Promise<VKontaktePostListItem[]> {
    const response = await apiClient.get<VKontaktePostListItem[]>('/vk/posts', {
      params: { limit, offset },
    })
    return response.data
  },

  async getPost(id: number): Promise<VKontaktePostFull> {
    const response = await apiClient.get<VKontaktePostFull>(`/vk/post/${id}`)
    return response.data
  },

  async updatePost(id: number, data: { text?: string; status?: string }): Promise<VKontaktePostFull> {
    const response = await apiClient.put<VKontaktePostFull>(`/vk/post/${id}`, data)
    return response.data
  },

  async deletePost(id: number): Promise<VKontaktePostFull> {
    const response = await apiClient.delete<VKontaktePostFull>(`/vk/post/${id}`)
    return response.data
  },
}
