import React, { useState } from 'react'
import { addHolding, addAsset } from '@/lib/api'

export const AddAssetModal = ({ isOpen, onClose, onSuccess }) => {
  const [symbols, setSymbols] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (!isOpen) return null

  const handleAddAsset = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const symbolList = symbols.split(',').map(s => s.trim().toUpperCase())
      
      for (const symbol of symbolList) {
        if (symbol) {
          await addAsset(symbol)
        }
      }
      
      setSymbols('')
      onSuccess()
      onClose()
    } catch (err) {
      setError(`Erreur: ${err.response?.data?.detail || err.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full shadow-xl">
        <h2 className="text-2xl font-bold mb-4">Ajouter des Actifs</h2>
        
        <form onSubmit={handleAddAsset}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Symboles (séparés par des virgules)
            </label>
            <input
              type="text"
              placeholder="Ex: AAPL, GOOGL, BTC-USD, EUR=X"
              value={symbols}
              onChange={(e) => setSymbols(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
            <p className="text-xs text-gray-500 mt-2">
              💡 Utilisez les symboles Yahoo Finance (AAPL, BTC-USD, EUR=X, etc.)
            </p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <div className="flex gap-2">
            <button
              type="submit"
              disabled={loading || !symbols.trim()}
              className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
            >
              {loading ? 'Ajout en cours...' : 'Ajouter'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-300 text-gray-800 py-2 rounded-lg hover:bg-gray-400"
            >
              Annuler
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export const AddHoldingModal = ({ isOpen, onClose, onSuccess, availableAssets }) => {
  const [formData, setFormData] = useState({
    assetId: '',
    quantity: '',
    avgPrice: '',
    notes: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (!isOpen) return null

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      if (!formData.assetId || !formData.quantity || !formData.avgPrice) {
        setError('Veuillez remplir tous les champs requis')
        setLoading(false)
        return
      }

      await addHolding(
        parseInt(formData.assetId),
        parseFloat(formData.quantity),
        parseFloat(formData.avgPrice),
        formData.notes || null
      )

      setFormData({ assetId: '', quantity: '', avgPrice: '', notes: '' })
      onSuccess()
      onClose()
    } catch (err) {
      setError(`Erreur: ${err.response?.data?.detail || err.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full shadow-xl">
        <h2 className="text-2xl font-bold mb-4">Ajouter une Position</h2>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Actif *
            </label>
            <select
              name="assetId"
              value={formData.assetId}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              <option value="">Sélectionnez un actif</option>
              {availableAssets?.map(asset => (
                <option key={asset.id} value={asset.id}>
                  {asset.symbol} - {asset.name}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quantité *
              </label>
              <input
                type="number"
                name="quantity"
                placeholder="Ex: 10"
                step="0.01"
                value={formData.quantity}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Prix Moyen (€) *
              </label>
              <input
                type="number"
                name="avgPrice"
                placeholder="Ex: 150.50"
                step="0.01"
                value={formData.avgPrice}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notes (optionnel)
            </label>
            <input
              type="text"
              name="notes"
              placeholder="Ex: Investissement long terme"
              value={formData.notes}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <div className="flex gap-2">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
            >
              {loading ? 'Ajout en cours...' : 'Ajouter'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-300 text-gray-800 py-2 rounded-lg hover:bg-gray-400"
            >
              Annuler
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
