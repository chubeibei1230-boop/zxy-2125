import request from '@/utils/request'

export const authApi = {
  login(data) {
    return request.post('/token/', data)
  },
  refreshToken(data) {
    return request.post('/token/refresh/', data)
  },
  getCurrentUser() {
    return request.get('/users/me/')
  }
}

export const userApi = {
  list(params) {
    return request.get('/users/', { params })
  },
  create(data) {
    return request.post('/users/', data)
  },
  byRole(role) {
    return request.get('/users/by_role/', { params: { role } })
  }
}

export const projectApi = {
  list(params) {
    return request.get('/projects/', { params })
  },
  create(data) {
    return request.post('/projects/', data)
  },
  update(id, data) {
    return request.put(`/projects/${id}/`, data)
  },
  delete(id) {
    return request.delete(`/projects/${id}/`)
  }
}

export const stationApi = {
  list(params) {
    return request.get('/stations/', { params })
  },
  create(data) {
    return request.post('/stations/', data)
  },
  update(id, data) {
    return request.put(`/stations/${id}/`, data)
  },
  delete(id) {
    return request.delete(`/stations/${id}/`)
  }
}

export const templateApi = {
  list(params) {
    return request.get('/task-templates/', { params })
  },
  create(data) {
    return request.post('/task-templates/', data)
  },
  update(id, data) {
    return request.put(`/task-templates/${id}/`, data)
  },
  delete(id) {
    return request.delete(`/task-templates/${id}/`)
  }
}

export const taskApi = {
  list(params) {
    return request.get('/tasks/', { params })
  },
  myTasks(params) {
    return request.get('/tasks/my_tasks/', { params })
  },
  detail(id) {
    return request.get(`/tasks/${id}/`)
  },
  create(data) {
    return request.post('/tasks/', data)
  },
  update(id, data) {
    return request.put(`/tasks/${id}/`, data)
  },
  delete(id, hard = false) {
    return request.delete(`/tasks/${id}/`, { params: { hard } })
  },
  transition(id, data) {
    return request.post(`/tasks/${id}/transition/`, data)
  },
  submitPreparation(id, data) {
    return request.post(`/tasks/${id}/submit_preparation/`, data)
  },
  submitReception(id, data) {
    return request.post(`/tasks/${id}/submit_reception/`, data)
  },
  submitClosing(id, data) {
    return request.post(`/tasks/${id}/submit_closing/`, data)
  },
  handleException(id, data) {
    return request.post(`/tasks/${id}/handle_exception/`, data)
  },
  initiateRectification(id, data) {
    return request.post(`/tasks/${id}/initiate_rectification/`, data)
  },
  submitRectification(id, data) {
    return request.post(`/tasks/${id}/submit_rectification/`, data)
  }
}

export const flowRecordApi = {
  list(params) {
    return request.get('/flow-records/', { params })
  }
}
