import { configureStore } from '@reduxjs/toolkit'
import axios from 'axios'
import authReducer from '../features/auth/authSlice'
import filesReducer from '../features/files/filesSlice'

// Configure axios defaults
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
axios.defaults.withCredentials = true

// Add token to requests if available
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const store = configureStore({
  reducer: {
    auth: authReducer,
    files: filesReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch 