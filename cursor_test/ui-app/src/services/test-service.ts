import { apiClient, getErrorMessage } from './api-client'
import type { SearchResponse, SubmitRequest, SubmitResponse, Product } from '@/types/test'

export const testService = {
  async getProducts(): Promise<Product[]> {
    try {
      const response = await apiClient.get<Product[]>('/test/products')
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async searchOrder(orderId: string): Promise<SearchResponse> {
    try {
      const response = await apiClient.get<SearchResponse>(`/test/search/${orderId}`)
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async submitTest(data: SubmitRequest): Promise<SubmitResponse> {
    try {
      const response = await apiClient.post<SubmitResponse>('/test/submit', data)
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },
}
