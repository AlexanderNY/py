import { apiClient, getErrorMessage } from './api-client'
import type { 
  TokenResponse, 
  User, 
  LoginCredentials, 
  RegisterCredentials, 
  ProfileUpdate,
  RoleTariffHistoryEntry,
} from '@/types'

export const authService = {
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    try {
      const response = await apiClient.post<TokenResponse>('/auth/login', credentials)
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async register(credentials: RegisterCredentials): Promise<TokenResponse> {
    try {
      const response = await apiClient.post<TokenResponse>('/auth/register', credentials)
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async logout(refreshToken: string): Promise<void> {
    try {
      await apiClient.post('/auth/logout', { refresh_token: refreshToken })
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async logoutAll(): Promise<void> {
    try {
      await apiClient.post('/auth/all-logout')
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async getProfile(): Promise<User> {
    try {
      const response = await apiClient.get<User>('/auth/profile')
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async updateProfile(data: ProfileUpdate): Promise<User> {
    try {
      const response = await apiClient.post<User>('/auth/profile', data)
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async resetPassword(email: string): Promise<void> {
    try {
      await apiClient.post('/auth/reset-password', { email })
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async confirmPasswordReset(token: string, newPassword: string): Promise<void> {
    try {
      await apiClient.post('/auth/reset-password/confirm', { 
        token, 
        new_password: newPassword 
      })
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async refreshTokens(refreshToken: string): Promise<TokenResponse> {
    try {
      const response = await apiClient.post<TokenResponse>('/auth/refresh', { 
        refresh_token: refreshToken 
      })
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async verifyEmail(code: string): Promise<void> {
    try {
      await apiClient.post('/auth/verify', { code })
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async getUsers(): Promise<User[]> {
    try {
      const response = await apiClient.get<User[]>('/auth/users')
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async updateUser(
    userId: number,
    data: { role?: 'guest' | 'user' | 'admin'; tariff?: string }
  ): Promise<User> {
    try {
      const response = await apiClient.patch<User>(`/auth/users/${userId}`, data)
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },

  async getRoleTariffHistory(userId: number): Promise<RoleTariffHistoryEntry[]> {
    try {
      const response = await apiClient.get<RoleTariffHistoryEntry[]>(
        `/auth/users/${userId}/role-tariff-history`
      )
      return response.data
    } catch (error) {
      throw new Error(getErrorMessage(error))
    }
  },
}


