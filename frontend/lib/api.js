import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ============ ASSETS ============
export const getAssets = () => api.get('/api/assets')

export const addAsset = (symbol, name, assetType = 'stock') => 
  api.post('/api/assets/add', null, {
    params: { symbol, name, asset_type: assetType }
  })

export const searchAssets = (q) => api.get('/api/search', { params: { q } })

export const getAssetInfo = (symbol) => api.get(`/api/assets/${symbol}/info`)

export const getAssetHistory = (symbol, period = '1mo', interval = '1d') =>
  api.get(`/api/assets/${symbol}/history`, {
    params: { period, interval }
  })

// ============ PORTFOLIO ============
export const getPortfolio = () => api.get('/api/portfolio')

// ============ HOLDINGS ============
export const getPriceAtDate = (symbol, date) =>
  api.get(`/api/assets/${symbol}/price-at`, { params: { date } })

export const addHolding = (assetId, quantity, purchaseDate, price = null, notes = null) =>
  api.post('/api/holdings/add', null, {
    params: { asset_id: assetId, quantity, purchase_date: purchaseDate, price, notes }
  })

export const updateHolding = (holdingId, quantity, purchaseDate, price, notes = null) =>
  api.put(`/api/holdings/${holdingId}`, null, {
    params: { quantity, purchase_date: purchaseDate, price, notes }
  })

export const removeHolding = (holdingId) =>
  api.delete(`/api/holdings/${holdingId}`)

// ============ SETTINGS ============
export const getSettings = () => api.get('/api/settings')
export const updateFinnhubKey = (key) => api.put('/api/settings/finnhub-key', null, { params: { key } })
export const testFinnhubKey = () => api.get('/api/settings/test-finnhub')

// ============ HEALTH ============
export const checkHealth = () => api.get('/health')

export default api
