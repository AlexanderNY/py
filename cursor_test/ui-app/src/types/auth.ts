export type UserRole = 'guest' | 'user' | 'admin' | 'manager' | 'author'

export interface User {
  id?: number
  username: string
  email: string
  role: UserRole
  tariff?: string
  is_email_verified: boolean
  created_at: string
  access_token?: string
  refresh_token?: string
  group_id?: number | null
  group_name?: string | null
  role_in_group?: 'manager' | 'author' | null
}

export interface GroupMemberResponse {
  user_id: number
  username: string
  email: string
  tariff: string
  role_in_group: 'manager' | 'author'
  joined_at: string
}

export interface GroupResponse {
  id: number
  name: string
  created_at: string
  created_by_user_id?: number | null
  role_in_group?: 'manager' | 'author' | null
  members?: GroupMemberResponse[] | null
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterCredentials {
  username: string
  email: string
  password: string
}

export interface ProfileUpdate {
  username?: string
  email?: string
  password?: string
}

export interface EmailVerificationRequest {
  code: string
}

export interface PasswordResetRequest {
  email: string
}

export interface PasswordResetConfirm {
  token: string
  new_password: string
}

export interface RoleTariffHistoryEntry {
  id: number
  user_id: number
  changed_at: string
  changed_by_user_id?: number | null
  role_old?: string | null
  role_new?: string | null
  tariff_old?: string | null
  tariff_new?: string | null
}

export interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

export type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; tokens: TokenResponse } }
  | { type: 'AUTH_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'UPDATE_USER'; payload: User }
  | { type: 'UPDATE_TOKENS'; payload: TokenResponse }
  | { type: 'CLEAR_ERROR' }


