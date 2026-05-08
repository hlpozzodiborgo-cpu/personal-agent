import React, { useState, useEffect, useRef } from 'react'
import { addHolding, updateHolding, addAsset, searchAssets, getPriceAtDate, getSettings, updateFinnhubKey, updateAnthropicKey, updateNewsApiKey, updateGeminiKey, updateGroqKey, deleteFinnhubKey, deleteAnthropicKey, deleteNewsApiKey, deleteGeminiKey, deleteGroqKey, testFinnhubKey, testAnthropicKey, testNewsApiKey, testGeminiKey, testGroqKey, setAiProvider, getMaskedKey } from '@/lib/api'

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

const AI_PROVIDERS = [
  { id: 'claude',  label: 'Claude (Anthropic)', badge: '~0.001€/analyse',  free: false },
  { id: 'gemini',  label: 'Gemini 1.5 Flash',   badge: '1M tokens/jour',   free: true  },
  { id: 'groq',    label: 'Llama 3.1 70B (Groq)',badge: '14 400 req/jour',  free: true  },
]

export const SettingsModal = ({ isOpen, onClose }) => {
  const [status, setStatus]     = useState({})
  const [keys, setKeys]         = useState({})
  const [show, setShow]         = useState({})
  const [masked, setMasked]     = useState({})  // clé masquée récupérée du backend
  const [saving, setSaving]     = useState({})
  const [deleting, setDeleting] = useState({})
  const [testing, setTesting]   = useState({})
  const [testResults, setTestResults] = useState({})
  const [savedMsg, setSavedMsg] = useState({})

  const refresh = () => getSettings().then(r => setStatus(r.data)).catch(() => {})

  useEffect(() => {
    if (isOpen) {
      setKeys({}); setShow({}); setMasked({}); setTestResults({}); setSavedMsg({})
      refresh()
    }
  }, [isOpen])

  const handleReveal = async (id, dbKey) => {
    if (show[id]) {
      // Cacher : réinitialiser
      setShow(s => ({ ...s, [id]: false }))
      setMasked(m => ({ ...m, [id]: null }))
      return
    }
    try {
      const res = await getMaskedKey(dbKey)
      setMasked(m => ({ ...m, [id]: res.data.masked }))
      setShow(s => ({ ...s, [id]: true }))
    } catch {}
  }

  const handleSave = async (id, updateFn) => {
    const val = keys[id]?.trim()
    if (!val) return
    setSaving(s => ({ ...s, [id]: true }))
    try {
      await updateFn(val)
      await refresh()
      setKeys(k => ({ ...k, [id]: '' }))
      setMasked(m => ({ ...m, [id]: null })); setShow(s => ({ ...s, [id]: false }))
      setSavedMsg(m => ({ ...m, [id]: 'Clé sauvegardée.' }))
      setTimeout(() => setSavedMsg(m => ({ ...m, [id]: '' })), 3000)
    } catch { setSavedMsg(m => ({ ...m, [id]: 'Erreur lors de la sauvegarde.' })) }
    finally { setSaving(s => ({ ...s, [id]: false })) }
  }

  const handleDelete = async (id, deleteFn) => {
    if (!window.confirm('Supprimer cette clé API ?')) return
    setDeleting(d => ({ ...d, [id]: true }))
    try { await deleteFn(); await refresh(); setMasked(m => ({ ...m, [id]: null })) }
    catch {}
    finally { setDeleting(d => ({ ...d, [id]: false })) }
  }

  const handleTest = async (id, testFn) => {
    setTesting(t => ({ ...t, [id]: true })); setTestResults(r => ({ ...r, [id]: null }))
    try { const res = await testFn(); setTestResults(r => ({ ...r, [id]: res.data })) }
    catch { setTestResults(r => ({ ...r, [id]: { success: false, message: 'Erreur réseau.' } })) }
    finally { setTesting(t => ({ ...t, [id]: false })) }
  }

  const handleProviderChange = async (p) => {
    try { await setAiProvider(p); await refresh() } catch {}
  }

  if (!isOpen) return null

  // Composant champ clé API réutilisable
  const KeyField = ({ id, dbKey, isConfigured, updateFn, deleteFn, testFn, link, linkText }) => {
    const inputVal = keys[id] ?? ''
    const isTyping = inputVal.length > 0
    // Si on a une clé masquée ET show activé ET pas en train de taper → afficher masqué en readonly
    const displayVal = (!isTyping && show[id] && masked[id]) ? masked[id] : inputVal
    const inputType  = (show[id] && !(!isTyping && masked[id])) ? 'text' : 'password'

    return (
      <div>
        <div className="flex gap-2 mb-2">
          <div className="relative flex-1">
            <input
              type={inputType}
              readOnly={!isTyping && show[id] && !!masked[id]}
              placeholder={isConfigured ? '••••••••• (remplacer)' : 'Collez votre clé ici'}
              value={displayVal}
              onChange={e => {
                if (!(!isTyping && show[id] && masked[id])) // ignore si readonly masqué
                  setKeys(k => ({ ...k, [id]: e.target.value }))
              }}
              className={`w-full px-3 py-2 pr-16 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 ${
                !isTyping && show[id] && masked[id] ? 'border-gray-200 bg-gray-50 font-mono text-gray-600' : 'border-gray-300'
              }`}
            />
            <button
              type="button"
              onMouseDown={e => e.preventDefault()}
              onClick={() => {
                if (isConfigured && !isTyping) {
                  handleReveal(id, dbKey)
                } else {
                  setShow(s => ({ ...s, [id]: !s[id] }))
                }
              }}
              className="absolute right-2 top-2 text-xs text-gray-400 hover:text-gray-700 px-1 py-0.5 rounded select-none"
            >
              {show[id] ? 'Cacher' : (isConfigured && !isTyping ? 'Voir' : 'Voir')}
            </button>
          </div>
          <button onClick={() => handleSave(id, updateFn)} disabled={!isTyping || saving[id]}
            className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 text-sm font-medium whitespace-nowrap">
            {saving[id] ? '…' : 'Sauvegarder'}
          </button>
        </div>

        {savedMsg[id] && (
          <p className={`text-xs mb-2 ${savedMsg[id].includes('Erreur') ? 'text-red-600' : 'text-green-600'}`}>
            {savedMsg[id]}
          </p>
        )}

        <div className="flex gap-2">
          {testFn && (
            <button onClick={() => handleTest(id, testFn)} disabled={testing[id] || !isConfigured}
              className="flex-1 py-1.5 border border-gray-200 rounded-lg text-xs text-gray-600 hover:bg-gray-50 disabled:opacity-40">
              {testing[id] ? 'Test…' : '🔌 Tester'}
            </button>
          )}
          {link && (
            <a href={link} target="_blank" rel="noreferrer"
              className="flex-1 py-1.5 text-center border border-gray-200 rounded-lg text-xs text-blue-600 hover:bg-blue-50">
              {linkText} →
            </a>
          )}
          {isConfigured && deleteFn && (
            <button onClick={() => handleDelete(id, deleteFn)} disabled={deleting[id]}
              className="py-1.5 px-3 border border-red-200 rounded-lg text-xs text-red-500 hover:bg-red-50 disabled:opacity-40">
              {deleting[id] ? '…' : '🗑'}
            </button>
          )}
        </div>

        {testResults[id] && (
          <div className={`mt-2 p-2 rounded text-xs ${testResults[id].success ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
            {testResults[id].success ? '✓ ' : '✗ '}{testResults[id].message}
          </div>
        )}
      </div>
    )
  }

  const Badge = ({ isConfigured }) => (
    <div className={`flex items-center gap-1.5 text-xs font-medium ${isConfigured ? 'text-green-600' : 'text-gray-400'}`}>
      <span className={`w-2 h-2 rounded-full ${isConfigured ? 'bg-green-500' : 'bg-gray-300'}`} />
      {isConfigured ? 'Configurée' : 'Non configurée'}
    </div>
  )

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-lg w-full shadow-xl overflow-y-auto max-h-[90vh]">
        <h2 className="text-2xl font-bold mb-1">Paramètres</h2>
        <p className="text-sm text-gray-500 mb-5">
          Clés stockées dans votre base de données locale — elles ne quittent jamais votre machine.
        </p>

        {/* Prix des actifs */}
        <div className="border rounded-lg p-4 mb-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Prix des actifs</p>
            <Badge isConfigured={status.finnhub_configured} />
          </div>
          <KeyField id="finnhub" dbKey="finnhub_api_key" isConfigured={status.finnhub_configured}
            updateFn={updateFinnhubKey} deleteFn={deleteFinnhubKey} testFn={testFinnhubKey}
            link="https://finnhub.io" linkText="Clé gratuite" />
        </div>

        {/* Fournisseur IA */}
        <div className="border rounded-lg p-4 mb-4">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Fournisseur IA — Analyse des actualités</p>
          <div className="grid grid-cols-3 gap-2 mb-4">
            {AI_PROVIDERS.map(p => (
              <button key={p.id} onClick={() => handleProviderChange(p.id)}
                className={`p-2.5 rounded-lg border text-left transition ${
                  status.ai_provider === p.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}>
                <div className="flex items-center gap-1 mb-1">
                  {status.ai_provider === p.id && <span className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0" />}
                  {p.free && <span className="text-xs bg-green-100 text-green-700 px-1 rounded font-medium">GRATUIT</span>}
                </div>
                <p className="text-xs font-medium text-gray-800 leading-tight">{p.label}</p>
                <p className="text-xs text-gray-400 mt-0.5">{p.badge}</p>
              </button>
            ))}
          </div>

          {/* Clé du fournisseur actif */}
          {status.ai_provider === 'claude' && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-gray-600">Clé Anthropic <a href="https://console.anthropic.com" target="_blank" rel="noreferrer" className="text-blue-500 hover:underline">console.anthropic.com →</a></p>
                <Badge isConfigured={status.anthropic_configured} />
              </div>
              <KeyField id="anthropic" dbKey="anthropic_api_key" isConfigured={status.anthropic_configured}
                updateFn={updateAnthropicKey} deleteFn={deleteAnthropicKey} testFn={testAnthropicKey} />
            </div>
          )}
          {status.ai_provider === 'gemini' && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-gray-600">Clé Google Gemini <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer" className="text-blue-500 hover:underline">aistudio.google.com →</a></p>
                <Badge isConfigured={status.gemini_configured} />
              </div>
              <KeyField id="gemini" dbKey="gemini_api_key" isConfigured={status.gemini_configured}
                updateFn={updateGeminiKey} deleteFn={deleteGeminiKey} testFn={testGeminiKey} />
            </div>
          )}
          {status.ai_provider === 'groq' && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-gray-600">Clé Groq <a href="https://console.groq.com/keys" target="_blank" rel="noreferrer" className="text-blue-500 hover:underline">console.groq.com →</a></p>
                <Badge isConfigured={status.groq_configured} />
              </div>
              <KeyField id="groq" dbKey="groq_api_key" isConfigured={status.groq_configured}
                updateFn={updateGroqKey} deleteFn={deleteGroqKey} testFn={testGroqKey} />
            </div>
          )}
        </div>

        {/* Actualités */}
        <div className="border rounded-lg p-4 mb-5">
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Actualités (NewsAPI)</p>
            <Badge isConfigured={status.newsapi_configured} />
          </div>
          <p className="text-xs text-gray-400 mb-3">Gratuit jusqu'à 100 req/jour. Couvre les ETF européens par recherche de nom.</p>
          <KeyField id="newsapi" dbKey="newsapi_key" isConfigured={status.newsapi_configured}
            updateFn={updateNewsApiKey} deleteFn={deleteNewsApiKey} testFn={testNewsApiKey}
            link="https://newsapi.org/register" linkText="Clé gratuite" />
        </div>

        <button onClick={onClose} className="w-full py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300">
          Fermer
        </button>
      </div>
    </div>
  )
}

export const EditHoldingModal = ({ isOpen, onClose, onSuccess, holding }) => {
  const [quantity, setQuantity] = useState('')
  const [purchaseDate, setPurchaseDate] = useState('')
  const [exactPrice, setExactPrice] = useState('')
  const [notes, setNotes] = useState('')
  const [historicalPrice, setHistoricalPrice] = useState(null)
  const [fetchingPrice, setFetchingPrice] = useState(false)
  const [priceUnavailable, setPriceUnavailable] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const today = new Date().toISOString().split('T')[0]

  useEffect(() => {
    if (isOpen && holding) {
      setQuantity(holding.quantity?.toString() || '')
      setPurchaseDate(holding.purchase_date || '')
      setExactPrice(holding.avg_price?.toFixed(4) || '')
      setNotes(holding.notes || '')
      setHistoricalPrice(holding.avg_price || null)
      setPriceUnavailable(false)
      setError('')
    }
  }, [isOpen, holding])

  // Re-fetch price uniquement si la date change
  useEffect(() => {
    if (!holding?.symbol || !purchaseDate) return
    if (purchaseDate === holding.purchase_date) return
    setFetchingPrice(true)
    setHistoricalPrice(null)
    setPriceUnavailable(false)
    setExactPrice('')
    getPriceAtDate(holding.symbol, purchaseDate)
      .then(res => setHistoricalPrice(res.data.price))
      .catch(() => setPriceUnavailable(true))
      .finally(() => setFetchingPrice(false))
  }, [purchaseDate])

  const effectivePrice = exactPrice ? parseFloat(exactPrice) : historicalPrice
  const canSubmit = quantity && purchaseDate && effectivePrice && !loading

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!canSubmit) return
    setLoading(true); setError('')
    try {
      await updateHolding(holding.id, parseFloat(quantity), purchaseDate, effectivePrice, notes || null)
      onSuccess(); onClose()
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally { setLoading(false) }
  }

  if (!isOpen || !holding) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full shadow-xl">
        <h2 className="text-2xl font-bold mb-1">Modifier l'ordre</h2>
        <p className="text-sm text-gray-500 mb-4">{holding.symbol} — {holding.name}</p>

        <form onSubmit={handleSubmit} className="space-y-4">

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date d'achat *</label>
            <input type="date" value={purchaseDate} onChange={e => setPurchaseDate(e.target.value)}
              max={today} required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
          </div>

          {(fetchingPrice || historicalPrice || priceUnavailable) && (
            <div className={`p-3 rounded-lg text-sm ${priceUnavailable ? 'bg-amber-50 border border-amber-200 text-amber-700' : 'bg-blue-50 border border-blue-200 text-blue-700'}`}>
              {fetchingPrice && <div className="flex items-center gap-2"><div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500" />Récupération du prix…</div>}
              {!fetchingPrice && historicalPrice && !exactPrice && <span>Prix de clôture : <strong>{historicalPrice.toFixed(4)} €</strong></span>}
              {!fetchingPrice && historicalPrice && exactPrice && <span>Historique : {historicalPrice.toFixed(4)} € — <strong>remplacé par {parseFloat(exactPrice).toFixed(4)} €</strong></span>}
              {!fetchingPrice && priceUnavailable && <span>Prix introuvable pour cette date — entrez-le manuellement.</span>}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Prix unitaire {priceUnavailable ? '*' : '(optionnel — remplace le prix historique)'}
            </label>
            <input type="number" step="0.0001" min="0"
              placeholder={historicalPrice ? `${historicalPrice.toFixed(4)} (automatique)` : 'Ex: 6.57'}
              value={exactPrice} onChange={e => setExactPrice(e.target.value)}
              required={priceUnavailable && !historicalPrice}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Quantité *</label>
            <input type="number" step="0.0001" min="0" value={quantity}
              onChange={e => setQuantity(e.target.value)} required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
          </div>

          {effectivePrice && quantity && (
            <div className="text-sm text-gray-500 text-right">
              Total : <strong className="text-gray-800">{(effectivePrice * parseFloat(quantity)).toFixed(2)} €</strong>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes (optionnel)</label>
            <input type="text" value={notes} onChange={e => setNotes(e.target.value)}
              placeholder="Ex: Investissement long terme"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
          </div>

          {error && <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>}

          <div className="flex gap-2 pt-1">
            <button type="submit" disabled={!canSubmit}
              className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed">
              {loading ? 'Enregistrement…' : 'Enregistrer'}
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
