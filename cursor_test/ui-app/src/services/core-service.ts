import { apiClient, getErrorMessage } from './api-client'
import type { HealthcheckResponse, StatisticsResponse, UserStatisticsResponse, ScheduleResponse } from '@/types/core'

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

  async getUsersStatistics(): Promise<UserStatisticsResponse> {
    try {
      const response = await apiClient.get<UserStatisticsResponse>('/core/users-statistics')
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async getSchedule(): Promise<ScheduleResponse> {
    try {
      const response = await apiClient.get<ScheduleResponse>('/core/schedule')
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async startDiscovery(): Promise<{ status: string; message: string; changed: boolean }> {
    try {
      const response = await apiClient.post<{ status: string; message: string; changed: boolean }>('/core/start-discovery')
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async startBot(platforms: string[]): Promise<{ status: string; message: string; results: Record<string, any> }> {
    try {
      const response = await apiClient.post<{ status: string; message: string; results: Record<string, any> }>('/core/start-bot', { platforms })
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },
}
