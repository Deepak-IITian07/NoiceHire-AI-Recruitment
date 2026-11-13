
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// Automatically attach admin token to API requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')

  if (token) {
    config.headers.Authorization = `Token ${token}`
  }

  return config
})

export const authAPI = {
  login: async (username, password) => {
    const response = await api.post('/auth/login/', { username, password })

    localStorage.setItem('admin_token', response.data.token)
    localStorage.setItem('admin_username', response.data.username)

    return response.data
  },

  logout: async () => {
    try {
      await api.post('/auth/logout/')
    } finally {
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_username')
    }
  },
}

export const resumeAPI = {
  getAll: () => api.get('/resumes/'),
  getById: (id) => api.get(`/resumes/${id}/`),
  getStatus: (id) => api.get(`/resumes/${id}/status/`),
  process: (id) => api.post(`/resumes/${id}/process/`, {}, {
    timeout: 120000,
    }),
  delete: (id) => api.delete(`/resumes/${id}/`),
  upload: (file, onUploadProgress) => {
    const formData = new FormData()
    formData.append('file', file)

    return api.post('/resumes/upload/', formData, {
      onUploadProgress,
    })
  },
}

export const jobAPI = {
  getAll: () => api.get('/jobs/'),
  getById: (id) => api.get(`/jobs/${id}/`),
}

export const rankingAPI = {
  getByJob: (jobId) => api.get(`/rankings/${jobId}/`),
}

export default api
