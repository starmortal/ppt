/**
 * API client for PPT Master Web backend
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ========== Session API ==========

export const sessionAPI = {
  create: async (userId: string) => {
    const response = await apiClient.post('/session/create', { user_id: userId })
    return response.data
  },

  get: async (sessionId: string) => {
    const response = await apiClient.get(`/session/${sessionId}`)
    return response.data
  },

  delete: async (sessionId: string) => {
    const response = await apiClient.delete(`/session/${sessionId}`)
    return response.data
  },
}

// ========== Chat API ==========

export const chatAPI = {
  sendMessage: async (sessionId: string, message: string) => {
    const response = await apiClient.post('/chat/message', {
      session_id: sessionId,
      message,
    })
    return response.data
  },

  getHistory: async (sessionId: string, limit = 50, offset = 0) => {
    const response = await apiClient.get(`/chat/history/${sessionId}`, {
      params: { limit, offset },
    })
    return response.data
  },
}

// ========== File API ==========

export const fileAPI = {
  upload: async (file: File, sessionId: string, category = 'source') => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('session_id', sessionId)
    formData.append('category', category)

    const response = await apiClient.post('/file/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  process: async (sessionId: string, fileId: string) => {
    const formData = new FormData()
    formData.append('session_id', sessionId)
    formData.append('file_id', fileId)

    const response = await apiClient.post('/file/process', formData)
    return response.data
  },

  getProcessStatus: async (taskId: string) => {
    const response = await apiClient.get(`/file/process/${taskId}`)
    return response.data
  },

  list: async (sessionId: string, category?: string) => {
    const response = await apiClient.get(`/file/list/${sessionId}`, {
      params: { category },
    })
    return response.data
  },

  delete: async (fileId: string) => {
    const response = await apiClient.delete(`/file/${fileId}`)
    return response.data
  },
}

// ========== Project API ==========

export const projectAPI = {
  getStatus: async (projectId: string) => {
    const response = await apiClient.get(`/project/${projectId}/status`)
    return response.data
  },

  listFiles: async (projectId: string, category?: string) => {
    const response = await apiClient.get(`/project/${projectId}/files`, {
      params: { category },
    })
    return response.data
  },

  validate: async (projectId: string) => {
    const response = await apiClient.post(`/project/${projectId}/validate`)
    return response.data
  },

  delete: async (projectId: string) => {
    const response = await apiClient.delete(`/project/${projectId}`)
    return response.data
  },
}

// ========== Preview API ==========

export const previewAPI = {
  getSvg: (projectId: string, fileName: string) => {
    return `${API_BASE_URL}/preview/svg/${projectId}/${fileName}`
  },

  getSpec: async (projectId: string) => {
    const response = await apiClient.get(`/preview/spec/${projectId}`)
    return response.data
  },

  downloadPptx: (projectId: string) => {
    return `${API_BASE_URL}/preview/download/pptx/${projectId}`
  },

  downloadSvgZip: (projectId: string) => {
    return `${API_BASE_URL}/preview/download/svg/${projectId}`
  },
}

export default apiClient
