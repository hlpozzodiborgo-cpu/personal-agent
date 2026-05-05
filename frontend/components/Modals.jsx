import React, { useState, useEffect, useRef } from 'react'
import { addHolding, addAsset, searchAssets, getPriceAtDate } from '@/lib/api'

export const AddAssetModal = ({ isOpen, onClose, onSuccess }) => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [selected, setSelected] = useState(null)
  const [searching, setSearching] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const inputRef = useRef(null)

  // Reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      setQuery('')
      setResults([])
      setSelected(null)
      setError('')
      setShowDropdown(false)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [isOpen])

  // Debounced search
  useEffect(() => {
    if (query.length < 2) {
      setResults([])
      setShowDropdown(false)
      return
    }
    const timer = setTimeout(async () => {
      setSearching(true)
      try {
        const res = await searchAssets(query)
        setResults(res.data.results)
        setShowDropdown(true)
      } catch {
        setResults([])
      } finally {
        setSearching(false)
      }
    }, 400)
    return () => clearTimeout(timer)
  }, [query])

  const handleSelect = (asset) => {
    setSelected(asset)
    setQuery('')
    setShowDropdown(false)
    setResults([])
  }

  const handleAdd = async () => {
    if (!selected) return
    setLoading(true)
    setError('')
    try {
      await addAsset(selected.symbol, selected.name, selected.asset_type)
      setSelected(null)
      onSuccess()
      onClose()
    } catch (err) {
      setError(`Erreur: ${err.response?.data?.detail || err.message}`)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full shadow-xl">
        <h2 className="text-2xl font-bold mb-1">Ajouter un Actif</h2>
        <p className="text-sm text-gray-500 mb-4">Recherchez par nom ou symbole (actions, ETF, crypto…)</p>

        {/* Barre de recherche */}
        <div className="relative mb-4">
          <div className="relative">
            <input
              ref={inputRef}
              type="text"
              placeholder="Ex: Apple, Amundi Nasdaq, BTC-USD…"
              value={query}
              onChange={(e) => { setQuery(e.target.value); setSelected(null) }}
              onBlur={() => setTimeout(() => setShowDropdown(false), 150)}
              onFocus={() => results.length > 0 && setShowDropdown(true)}
              className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <div className="absolute right-3 top-2.5 text-gray-400">
              {searching
                ? <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500" />
                : <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" /></svg>
              }
            </div>
          </div>

          {/* Dropdown résultats */}
          {showDropdown && (
            <div className="absolute w-full bg-white border border-gray-200 rounded-lg shadow-lg mt-1 z-10 max-h-60 overflow-y-auto">
              {results.length > 0 ? results.map((asset, idx) => (
                <button
                  key={idx}
                  onMouseDown={() => handleSelect(asset)}
                  className="w-full px-4 py-3 text-left hover:bg-blue-50 border-b last:border-0 flex justify-between items-center gap-2"
                >
                  <div className="min-w-0">
                    <p className="font-semibold text-gray-900 text-sm">{asset.display_symbol}</p>
                    <p className="text-xs text-gray-500 truncate">{asset.name}</p>
                  </div>
                  <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded flex-shrink-0">{asset.type}</span>
                </button>
              )) : (
                <p className="px-4 py-3 text-sm text-gray-500">Aucun résultat pour « {query} »</p>
              )}
            </div>
          )}
        </div>

        {/* Actif sélectionné */}
        {selected && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg flex justify-between items-center">
            <div>
              <p className="font-semibold text-blue-900">{selected.display_symbol}</p>
              <p className="text-sm text-blue-700">{selected.name}</p>
            </div>
            <button onClick={() => setSelected(null)} className="text-blue-400 hover:text-blue-600 text-2xl leading-none ml-2">×</button>
          </div>
        )}

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        <div className="flex gap-2">
          <button
            onClick={handleAdd}
            disabled={!selected || loading}
            className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {loading ? 'Ajout en cours…' : 'Ajouter'}
          </button>
          <button
            onClick={onClose}
            className="flex-1 bg-gray-200 text-gray-800 py-2 rounded-lg hover:bg-gray-300"
          >
            Annuler
          </button>
        </div>
      </div>
    </div>
  )
}

export const AddHoldingModal = ({ isOpen, onClose, onSuccess, availableAssets }) => {
  const [assetId, setAssetId] = useState('')
  const [purchaseDate, setPurchaseDate] = useState('')
  const [exactPrice, setExactPrice] = useState('')
  const [quantity, setQuantity] = useState('')
  const [notes, setNotes] = useState('')
  const [historicalPrice, setHistoricalPrice] = useState(null)
  const [fetchingPrice, setFetchingPrice] = useState(false)
  const [priceUnavailable, setPriceUnavailable] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const today = new Date().toISOString().split('T')[0]
  const selectedAsset = availableAssets?.find(a => a.id === parseInt(assetId))

  // Reset when modal opens
  useEffect(() => {
    if (isOpen) {
      setAssetId(''); setPurchaseDate(''); setExactPrice('')
      setQuantity(''); setNotes(''); setHistoricalPrice(null)
      setPriceUnavailable(false); setError('')
    }
  }, [isOpen])

  // Auto-fetch historical price when asset + date are both set
  useEffect(() => {
    if (!selectedAsset?.symbol || !purchaseDate) {
      setHistoricalPrice(null); setPriceUnavailable(false); return
    }
    setFetchingPrice(true); setHistoricalPrice(null); setPriceUnavailable(false)
    getPriceAtDate(selectedAsset.symbol, purchaseDate)
      .then(res => setHistoricalPrice(res.data.price))
      .catch(() => setPriceUnavailable(true))
      .finally(() => setFetchingPrice(false))
  }, [selectedAsset?.symbol, purchaseDate])

  const effectivePrice = exactPrice ? parseFloat(exactPrice) : historicalPrice
  const canSubmit = assetId && purchaseDate && quantity && effectivePrice

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!canSubmit) return
    setLoading(true); setError('')
    try {
      await addHolding(
        parseInt(assetId),
        parseFloat(quantity),
        purchaseDate,
        effectivePrice,
        notes || null
      )
      onSuccess(); onClose()
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full shadow-xl">
        <h2 className="text-2xl font-bold mb-1">Ajouter une Position</h2>
        <p className="text-sm text-gray-500 mb-4">Le prix de clôture est récupéré automatiquement depuis la date d'achat.</p>

        <form onSubmit={handleSubmit} className="space-y-4">

          {/* Actif */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Actif *</label>
            <select
              value={assetId}
              onChange={e => setAssetId(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Sélectionnez un actif</option>
              {availableAssets?.map(asset => (
                <option key={asset.id} value={asset.id}>{asset.symbol} — {asset.name}</option>
              ))}
            </select>
          </div>

          {/* Date d'achat */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date d'achat *</label>
            <input
              type="date"
              value={purchaseDate}
              onChange={e => setPurchaseDate(e.target.value)}
              max={today}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          {/* Prix affiché */}
          {(fetchingPrice || historicalPrice || priceUnavailable) && (
            <div className={`p-3 rounded-lg text-sm ${priceUnavailable ? 'bg-amber-50 border border-amber-200 text-amber-700' : 'bg-blue-50 border border-blue-200 text-blue-700'}`}>
              {fetchingPrice && (
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500" />
                  Récupération du prix historique…
                </div>
              )}
              {!fetchingPrice && historicalPrice && !exactPrice && (
                <span>Prix de clôture récupéré : <strong>{historicalPrice.toFixed(2)} €</strong></span>
              )}
              {!fetchingPrice && historicalPrice && exactPrice && (
                <span>Prix historique : {historicalPrice.toFixed(2)} € — <strong>remplacé par {parseFloat(exactPrice).toFixed(2)} €</strong></span>
              )}
              {!fetchingPrice && priceUnavailable && (
                <span>Prix introuvable pour cette date — entrez le prix manuellement ci-dessous.</span>
              )}
            </div>
          )}

          {/* Prix exact optionnel */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Prix exact payé {priceUnavailable ? '*' : '(optionnel — remplace le prix historique)'}
            </label>
            <input
              type="number"
              placeholder={historicalPrice ? `${historicalPrice.toFixed(2)} (automatique)` : 'Ex: 150.50'}
              step="0.0001"
              min="0"
              value={exactPrice}
              onChange={e => setExactPrice(e.target.value)}
              required={priceUnavailable && !historicalPrice}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Quantité */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Quantité *</label>
            <input
              type="number"
              placeholder="Ex: 10"
              step="0.0001"
              min="0"
              value={quantity}
              onChange={e => setQuantity(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          {/* Total estimé */}
          {effectivePrice && quantity && (
            <div className="text-sm text-gray-500 text-right">
              Total investi : <strong className="text-gray-800">{(effectivePrice * parseFloat(quantity)).toFixed(2)} €</strong>
            </div>
          )}

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes (optionnel)</label>
            <input
              type="text"
              placeholder="Ex: Investissement long terme"
              value={notes}
              onChange={e => setNotes(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
          )}

          <div className="flex gap-2 pt-1">
            <button
              type="submit"
              disabled={!canSubmit || loading}
              className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {loading ? 'Ajout en cours…' : 'Ajouter la position'}
            </button>
            <button type="button" onClick={onClose} className="flex-1 bg-gray-200 text-gray-800 py-2 rounded-lg hover:bg-gray-300">
              Annuler
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
