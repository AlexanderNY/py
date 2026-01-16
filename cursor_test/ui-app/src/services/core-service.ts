import { apiClient, getErrorMessage } from './api-client'
import type { HealthcheckResponse, StatisticsResponse } from '@/types/core'

export const coreService = {
  async getHealthcheck(): Promise<HealthcheckResponse> {
    try {
      const response = await apiClient.get<HealthcheckResponse>('/core/healthchecks')
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async getStatistics(): Promise<StatisticsResponse> {
    try {
      const response = await apiClient.get<StatisticsResponse>('/core/statistics')
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },
}
