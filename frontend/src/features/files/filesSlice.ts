import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { api } from '@/lib/api'

interface File {
  id: string
  name: string
  size: number
  uploaded_at: string
  owner: {
    id: number
    email: string
    full_name: string
  }
}

interface FilesState {
  files: File[]
  isLoading: boolean
  error: string | null
}

const initialState: FilesState = {
  files: [],
  isLoading: false,
  error: null,
}

export const fetchFiles = createAsyncThunk(
  'files/fetchFiles',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get<File[]>('/api/files/')
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data || { detail: 'Failed to fetch files.' })
    }
  }
)

export const uploadFile = createAsyncThunk(
  'files/uploadFile',
  async (formData: FormData, { rejectWithValue }) => {
    try {
      const response = await api.post<File>('/api/files/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data || { detail: 'Failed to upload file.' })
    }
  }
)

export const deleteFile = createAsyncThunk(
  'files/deleteFile',
  async (fileId: string, { rejectWithValue }) => {
    try {
      await api.delete(`/api/files/${fileId}/`)
      return fileId
    } catch (error: any) {
      return rejectWithValue(error.response?.data || { detail: 'Failed to delete file.' })
    }
  }
)

export const downloadFile = createAsyncThunk(
  'files/downloadFile',
  async (fileId: string, { rejectWithValue }) => {
    try {
      const response = await api.get(`/api/files/${fileId}/download/`, {
        responseType: 'blob'
      })
      
      // Get filename from Content-Disposition header or use a default
      const contentDisposition = response.headers['content-disposition']
      let filename = 'download'
      if (contentDisposition) {
        const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition)
        if (matches != null && matches[1]) {
          filename = matches[1].replace(/['"]/g, '')
        }
      }
      
      // Create blob URL and trigger download
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      return fileId
    } catch (error: any) {
      return rejectWithValue(error.response?.data || { detail: 'Failed to download file.' })
    }
  }
)

interface ErrorResponse {
  detail?: string;
  errors?: Record<string, string[]>;
}

const filesSlice = createSlice({
  name: 'files',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Files
      .addCase(fetchFiles.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(fetchFiles.fulfilled, (state, action) => {
        state.isLoading = false
        state.files = action.payload
      })
      .addCase(fetchFiles.rejected, (state, action) => {
        state.isLoading = false
        const payload = action.payload as ErrorResponse
        state.error = payload?.detail || 'Failed to fetch files.'
      })
      // Upload File
      .addCase(uploadFile.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(uploadFile.fulfilled, (state, action) => {
        state.isLoading = false
        state.files.unshift(action.payload)
      })
      .addCase(uploadFile.rejected, (state, action) => {
        state.isLoading = false
        const payload = action.payload as ErrorResponse
        state.error = payload?.detail || 'Failed to upload file.'
      })
      // Delete File
      .addCase(deleteFile.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(deleteFile.fulfilled, (state, action) => {
        state.isLoading = false
        state.files = state.files.filter(file => file.id !== action.payload)
      })
      .addCase(deleteFile.rejected, (state, action) => {
        state.isLoading = false
        const payload = action.payload as ErrorResponse
        state.error = payload?.detail || 'Failed to delete file.'
      })
      // Download File (no state changes needed)
      .addCase(downloadFile.rejected, (state, action) => {
        const payload = action.payload as ErrorResponse
        state.error = payload?.detail || 'Failed to download file.'
      })
  },
})

export const { clearError } = filesSlice.actions
export default filesSlice.reducer 