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

// ============ PORTFOLIO HISTORY ============
export const getPortfolioHistory = (period = '1mo') =>
  api.get('/api/portfolio/history', { params: { period } })

export const getAssetPriceHistory = (symbol, period = '1mo') =>
  api.get(`/api/assets/${symbol}/price-history`, { params: { period } })

// ============ SETTINGS ============
export const getSettings        = ()    => api.get('/api/settings')
export const updateFinnhubKey   = (key) => api.put('/api/settings/finnhub-key',   null, { params: { key } })
export const updateAnthropicKey = (key) => api.put('/api/settings/anthropic-key', null, { params: { key } })
export const updateNewsApiKey   = (key) => api.put('/api/settings/newsapi-key',   null, { params: { key } })
export const deleteFinnhubKey   = ()    => api.delete('/api/settings/finnhub-key')
export const deleteAnthropicKey = ()    => api.delete('/api/settings/anthropic-key')
export const deleteNewsApiKey   = ()    => api.delete('/api/settings/newsapi-key')
export const deleteGeminiKey    = ()    => api.delete('/api/settings/gemini-key')
export const deleteGroqKey      = ()    => api.delete('/api/settings/groq-key')
export const testFinnhubKey     = ()    => api.get('/api/settings/test-finnhub')
export const testAnthropicKey   = ()    => api.get('/api/settings/test-anthropic')
export const testNewsApiKey     = ()    => api.get('/api/settings/test-newsapi')
export const testGeminiKey      = ()    => api.get('/api/settings/test-gemini')
export const testGroqKey        = ()    => api.get('/api/settings/test-groq')
export const updateGeminiKey    = (key) => api.put('/api/settings/gemini-key',   null, { params: { key } })
export const updateGroqKey      = (key) => api.put('/api/settings/groq-key',     null, { params: { key } })
export const setAiProvider      = (p)   => api.put('/api/settings/ai-provider',  null, { params: { provider: p } })
export const getMaskedKey       = (name) => api.get(`/api/settings/masked-key/${name}`)

// ============ NEWS & IA ============
export const analyzePortfolioNews = (days = 3) =>
  api.get('/api/news/analyze', { params: { days } })
export const getNewsStatus = () => api.get('/api/news/status')

// ============ HEALTH ============
export const checkHealth = () => api.get('/health')

export default api
