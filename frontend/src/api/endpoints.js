import api from './client'

export const authApi = {
  login: (username, password) => api.post('/auth/login/', { username, password }),
  register: (data) => api.post('/auth/register/', data),
  refresh: (refresh) => api.post('/auth/refresh/', { refresh }),
}

export const vehiclesApi = {
  list: (params) => api.get('/vehicles/', { params }),
  get: (id) => api.get(`/vehicles/${id}/`),
  create: (data) => api.post('/vehicles/', data),
  update: (id, data) => api.patch(`/vehicles/${id}/`, data),
  delete: (id) => api.delete(`/vehicles/${id}/`),
  dashboard: (id) => api.get(`/vehicles/${id}/dashboard/`),
  maintenances: (id, params) => api.get(`/vehicles/${id}/maintenances/`, { params }),
  createMaintenance: (id, data) => api.post(`/vehicles/${id}/maintenances/`, data),
  expenses: (id, params) => api.get(`/vehicles/${id}/expenses/`, { params }),
  createExpense: (id, data) => api.post(`/vehicles/${id}/expenses/`, data),
  expensesSummary: (id, params) => api.get(`/vehicles/${id}/expenses/summary/`, { params }),
  alerts: (id) => api.get(`/vehicles/${id}/alerts/`),
  trackedItems: (id) => api.get(`/vehicles/${id}/tracked-items/`),
  createTrackedItem: (id, data) => api.post(`/vehicles/${id}/tracked-items/`, data),
  search: (q) => api.get('/vehicules/', { params: { q } }),
  nhtsaMakes: (type) => api.get('/vehicles/nhtsa/makes/', { params: { type } }),
  nhtsaModels: (make, type, year) => api.get('/vehicles/nhtsa/models/', { params: { make, type, year } }),
  nhtsaDecodeVin: (vin) => api.get(`/vehicles/nhtsa/decode-vin/${vin}/`),
}

export const partsApi = {
  list: (params) => api.get('/parts/', { params }),
  get: (id) => api.get(`/parts/${id}/`),
  create: (data) => api.post('/parts/', data),
  update: (id, data) => api.patch(`/parts/${id}/`, data),
  delete: (id) => api.delete(`/parts/${id}/`),
  categories: () => api.get('/parts/categories/'),
  addCompatibility: (partId, vehicleId) => api.post(`/parts/${partId}/compatibilities/`, { vehicle: vehicleId }),
}

export const referenceApi = {
  list: (params) => api.get('/reference/vehicles/', { params }),
  get: (id) => api.get(`/reference/vehicles/${id}/`),
  schedule: (id) => api.get(`/reference/vehicles/${id}/schedule/`),
  parts: (id) => api.get(`/reference/vehicles/${id}/parts/`),
}

export const garageApi = {
  me: () => api.get('/garage/me/'),
  dashboard: () => api.get('/garage/dashboard/'),
  repairOrders: (params) => api.get('/garage/repair-orders/', { params }),
  getRepairOrder: (id) => api.get(`/garage/repair-orders/${id}/`),
  createRepairOrder: (data) => api.post('/garage/repair-orders/', data),
  updateRepairOrder: (id, data) => api.patch(`/garage/repair-orders/${id}/`, data),
}