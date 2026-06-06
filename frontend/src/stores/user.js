import { defineStore } from 'pinia'
import { authApi } from '@/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    isManager: (state) => state.user?.role === 'manager',
    isExecutor: (state) => state.user?.role === 'executor',
    isReviewer: (state) => state.user?.role === 'reviewer',
    userRole: (state) => state.user?.role || '',
    userRoleDisplay: (state) => {
      const roleMap = {
        'manager': '管理者',
        'executor': '执行者',
        'reviewer': '复核者'
      }
      return roleMap[state.user?.role] || ''
    }
  },
  actions: {
    async login(username, password) {
      const response = await authApi.login({ username, password })
      this.token = response.access
      localStorage.setItem('token', response.access)
      
      const userInfo = await authApi.getCurrentUser()
      this.user = userInfo
      localStorage.setItem('user', JSON.stringify(userInfo))
      
      return userInfo
    },
    async fetchCurrentUser() {
      if (this.token) {
        try {
          const userInfo = await authApi.getCurrentUser()
          this.user = userInfo
          localStorage.setItem('user', JSON.stringify(userInfo))
        } catch (error) {
          this.logout()
        }
      }
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
