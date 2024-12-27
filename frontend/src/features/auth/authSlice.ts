import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { api } from '@/lib/api'

interface User {
  id: number
  email: string
  full_name: string
  mfa_enabled: boolean
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

interface RegisterData {
  email: string
  full_name: string
  password: string
  confirmPassword: string
}

interface LoginData {
  email: string
  password: string
  mfa_code?: string
}

interface AuthResponse {
  detail: string
  user: User
  tokens: {
    access: string
    refresh: string
  }
}

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
}

export const register = createAsyncThunk<
  AuthResponse,
  RegisterData,
  { rejectValue: any }
>('auth/register', async (data, { rejectWithValue }) => {
  try {
    const response = await api.post<AuthResponse>('/api/auth/register/', data)
    localStorage.setItem('token', response.data.tokens.access)
    localStorage.setItem('refreshToken', response.data.tokens.refresh)
    return response.data
  } catch (error: any) {
    if (error.response?.data) {
      return rejectWithValue(error.response.data)
    }
    return rejectWithValue({ detail: 'An unexpected error occurred.' })
  }
})

export const login = createAsyncThunk<
  AuthResponse,
  LoginData,
  { rejectValue: any }
>('auth/login', async (data, { rejectWithValue }) => {
  try {
    const response = await api.post<AuthResponse>('/api/auth/login/', data)
    localStorage.setItem('token', response.data.tokens.access)
    localStorage.setItem('refreshToken', response.data.tokens.refresh)
    return response.data
  } catch (error: any) {
    if (error.response?.data) {
      return rejectWithValue(error.response.data)
    }
    return rejectWithValue({ detail: 'An unexpected error occurred.' })
  }
})

export const logout = createAsyncThunk('auth/logout', async () => {
  try {
    await api.post('/api/auth/logout/')
  } catch (error) {
    console.error('Logout failed:', error)
  } finally {
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  }
})

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      // Register
      .addCase(register.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(register.fulfilled, (state, action) => {
        state.isLoading = false
        state.user = action.payload.user
        state.isAuthenticated = true
        state.error = null
      })
      .addCase(register.rejected, (state, action) => {
        state.isLoading = false
        state.isAuthenticated = false
        state.user = null
        state.error = action.payload?.detail || 'Registration failed.'
      })
      // Login
      .addCase(login.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false
        state.user = action.payload.user
        state.isAuthenticated = true
        state.error = null
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false
        state.isAuthenticated = false
        state.user = null
        state.error = action.payload?.detail || 'Login failed.'
      })
      // Logout
      .addCase(logout.fulfilled, (state) => {
        state.user = null
        state.isAuthenticated = false
        state.error = null
      })
  },
})

export const { clearError } = authSlice.actions
export default authSlice.reducer 