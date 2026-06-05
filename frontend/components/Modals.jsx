import React, { useState, useEffect, useRef } from 'react'
import { addHolding, updateHolding, addAsset, searchAssets, getPriceAtDate, getSettings, updateFinnhubKey, updateAnthropicKey, updateNewsApiKey, updateGeminiKey, updateGroqKey, deleteFinnhubKey, deleteAnthropicKey, deleteNewsApiKey, deleteGeminiKey, deleteGroqKey, testFinnhubKey, testAnthropicKey, testNewsApiKey, testGeminiKey, testGroqKey, setAiProvider, getMaskedKey, getPreferences, updatePreferences } from '@/lib/api'

// Shared input classes
const INPUT = 'w-full px-3 py-2 bg-[#1A1A1A] border border-[#2A2A2A] rounded-lg text-white text-sm placeholder-gray-600 focus:outline-none focus:border-[#C9A84C] transition'
const LABEL = 'block text-xs font-medium text-gray-500 mb-1.5 uppercase tracking-wide'

export const AddAssetModal = ({ isOpen, onClose, onSuccess }) => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [selected, setSelected] = useState(null)
  const [searching, setSearching] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const inputRef = useRef(null)

  useEffect(() => {
    if (isOpen) {
      setQuery(''); setResults([]); setSelected(null); setError(''); setShowDropdown(false)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [isOpen])

  useEffect(() => {
    if (query.length < 2) { setResults([]); setShowDropdown(false); return }
    const timer = setTimeout(async () => {
      setSearching(true)
      try {
        const res = await searchAssets(query)
        setResults(res.data.results); setShowDropdown(true)
      } catch { setResults([]) }
      finally { setSearching(false) }
    }, 400)
    return () => clearTimeout(timer)
  }, [query])

  const handleSelect = (asset) => { setSelected(asset); setQuery(''); setShowDropdown(false); setResults([]) }

  const handleAdd = async () => {
    if (!selected) return
    setLoading(true); setError('')
    try {
      await addAsset(selected.symbol, selected.name, selected.asset_type)
      setSelected(null); onSuccess(); onClose()
    } catch (err) { setError(`Erreur : ${err.response?.data?.detail || err.message}`) }
    finally { setLoading(false) }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/75 flex items-center justify-center z-50 p-4">
      <div className="bg-[#111111] border border-[#2A2A2A] rounded-xl p-6 max-w-md w-full">
        <h2 className="text-lg font-semibold text-white mb-1">Ajouter un actif</h2>
        <p className="text-sm text-gray-500 mb-5">Recherchez par nom ou symbole (actions, ETF, crypto…)</p>

        <div className="relative mb-4">
          <div className="relative">
            <input ref={inputRef} type="text"
              placeholder="Ex: Apple, Amundi Nasdaq, BTC-USD…"
              value={query}
              onChange={(e) => { setQuery(e.target.value); setSelected(null) }}
              onBlur={() => setTimeout(() => setShowDropdown(false), 150)}
              onFocus={() => results.length > 0 && setShowDropdown(true)}
              className={INPUT}
            />
            <div className="absolute right-3 top-2.5 text-gray-600">
              {searching
                ? <div className="animate-spin rounded-full h-4 w-4 border-2 border-[#C9A84C] border-t-transparent" />
                : <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" /></svg>
              }
            </div>
          </div>
          {showDropdown && (
            <div className="absolute w-full bg-[#1A1A1A] border border-[#2A2A2A] rounded-lg mt-1 z-10 max-h-60 overflow-y-auto">
              {results.length > 0 ? results.map((asset, idx) => (
                <button key={idx} onMouseDown={() => handleSelect(asset)}
                  className="w-full px-4 py-3 text-left hover:bg-[#222] border-b border-[#2A2A2A] last:border-0 flex justify-between items-center gap-2">
                  <div className="min-w-0">
                    <p className="font-semibold text-white text-sm">{asset.display_symbol}</p>
                    <p className="text-xs text-gray-500 truncate">{asset.name}</p>
                  </div>
                  <span className="text-xs text-gray-600 bg-[#111] px-2 py-0.5 rounded flex-shrink-0">{asset.type}</span>
                </button>
              )) : (
                <p className="px-4 py-3 text-sm text-gray-500">Aucun résultat pour « {query} »</p>
              )}
            </div>
          )}
        </div>

        {selected && (
          <div className="mb-4 p-3 bg-[#C9A84C]/10 border border-[#C9A84C]/20 rounded-lg flex justify-between items-center">
            <div>
              <p className="font-semibold text-[#C9A84C] text-sm">{selected.display_symbol}</p>
              <p className="text-xs text-gray-400">{selected.name}</p>
            </div>
            <button onClick={() => setSelected(null)} className="text-gray-600 hover:text-gray-300 ml-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
        )}

        {error && <div className="mb-4 p-3 bg-red-900/20 border border-red-800/40 rounded-lg text-red-400 text-sm">{error}</div>}

        <div className="flex gap-2">
          <button onClick={handleAdd} disabled={!selected || loading}
            className="flex-1 btn-gold py-2 rounded-lg text-sm disabled:opacity-40">
            {loading ? 'Ajout…' : 'Ajouter'}
          </button>
          <button onClick={onClose}
            className="flex-1 bg-[#1A1A1A] border border-[#2A2A2A] text-gray-400 py-2 rounded-lg hover:bg-[#222] text-sm transition">
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

  useEffect(() => {
    if (isOpen) {
      setAssetId(''); setPurchaseDate(''); setExactPrice(''); setQuantity(''); setNotes('')
      setHistoricalPrice(null); setPriceUnavailable(false); setError('')
    }
  }, [isOpen])

  useEffect(() => {
    if (!selectedAsset?.symbol || !purchaseDate) { setHistoricalPrice(null); setPriceUnavailable(false); return }
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
      await addHolding(parseInt(assetId), parseFloat(quantity), purchaseDate, effectivePrice, notes || null)
      onSuccess(); onClose()
    } catch (err) { setError(err.response?.data?.detail || err.message) }
    finally { setLoading(false) }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/75 flex items-center justify-center z-50 p-4">
      <div className="bg-[#111111] border border-[#2A2A2A] rounded-xl p-6 max-w-md w-full">
        <h2 className="text-lg font-semibold text-white mb-1">Ajouter une position</h2>
        <p className="text-sm text-gray-500 mb-5">Le prix de clôture est récupéré automatiquement.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className={LABEL}>Actif *</label>
            <select value={assetId} onChange={e => setAssetId(e.target.value)} required className={INPUT} style={{ colorScheme: 'dark' }}>
              <option value="">Sélectionnez un actif</option>
              {availableAssets?.map(asset => (
                <option key={asset.id} value={asset.id}>{asset.symbol} — {asset.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className={LABEL}>Date d'achat *</label>
            <input type="date" value={purchaseDate} onChange={e => setPurchaseDate(e.target.value)}
              max={today} required className={INPUT} style={{ colorScheme: 'dark' }} />
          </div>

          {(fetchingPrice || historicalPrice || priceUnavailable) && (
            <div className={`p-3 rounded-lg text-sm ${priceUnavailable ? 'bg-amber-900/20 border border-amber-800/40 text-amber-400' : 'bg-[#C9A84C]/10 border border-[#C9A84C]/20 text-[#C9A84C]'}`}>
              {fetchingPrice && <div className="flex items-center gap-2"><div className="animate-spin rounded-full h-4 w-4 border-2 border-[#C9A84C] border-t-transparent" />Récupération du prix…</div>}
              {!fetchingPrice && historicalPrice && !exactPrice && <span>Prix de clôture : <strong>{historicalPrice.toFixed(2)} €</strong></span>}
              {!fetchingPrice && historicalPrice && exactPrice && <span>Historique : {historicalPrice.toFixed(2)} € — <strong>remplacé par {parseFloat(exactPrice).toFixed(2)} €</strong></span>}
              {!fetchingPrice && priceUnavailable && <span>Prix introuvable — entrez-le manuellement ci-dessous.</span>}
            </div>
          )}

          <div>
            <label className={LABEL}>{priceUnavailable ? 'Prix exact payé *' : 'Prix exact payé (optionnel)'}</label>
            <input type="number"
              placeholder={historicalPrice ? `${historicalPrice.toFixed(2)} (automatique)` : 'Ex: 150.50'}
              step="0.0001" min="0" value={exactPrice} onChange={e => setExactPrice(e.target.value)}
              required={priceUnavailable && !historicalPrice}
              className={INPUT} />
          </div>

          <div>
            <label className={LABEL}>Quantité *</label>
            <input type="number" placeholder="Ex: 10" step="0.0001" min="0"
              value={quantity} onChange={e => setQuantity(e.target.value)} required className={INPUT} />
          </div>

          {effectivePrice && quantity && (
            <div className="text-xs text-gray-500 text-right">
              Total : <strong className="text-[#C9A84C]">{(effectivePrice * parseFloat(quantity)).toFixed(2)} €</strong>
            </div>
          )}

          <div>
            <label className={LABEL}>Notes (optionnel)</label>
            <input type="text" placeholder="Ex: Investissement long terme" value={notes}
              onChange={e => setNotes(e.target.value)} className={INPUT} />
          </div>

          {error && <div className="p-3 bg-red-900/20 border border-red-800/40 rounded-lg text-red-400 text-sm">{error}</div>}

          <div className="flex gap-2 pt-1">
            <button type="submit" disabled={!canSubmit || loading}
              className="flex-1 btn-gold py-2 rounded-lg text-sm disabled:opacity-40">
              {loading ? 'Ajout…' : 'Ajouter la position'}
            </button>
            <button type="button" onClick={onClose}
              className="flex-1 bg-[#1A1A1A] border border-[#2A2A2A] text-gray-400 py-2 rounded-lg hover:bg-[#222] text-sm transition">
              Annuler
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

const AI_PROVIDERS = [
  { id: 'claude', label: 'Claude Haiku',       badge: '~0.001€/analyse', free: false },
  { id: 'gemini', label: 'Gemini 1.5 Flash',   badge: '1M tokens/jour',  free: true  },
  { id: 'groq',   label: 'Llama 3.3 70B',      badge: '14 400 req/jour', free: true  },
]

const RISK_LEVELS = [
  { value: 1, label: 'Très défensif',  examples: 'Livret A, obligations d\'État' },
  { value: 2, label: 'Défensif',       examples: 'ETF obligataires, fonds prudents' },
  { value: 3, label: 'Équilibré',      examples: 'ETF indiciels (S&P 500, MSCI World)' },
  { value: 4, label: 'Dynamique',      examples: 'Actions, ETF sectoriels, émergents' },
  { value: 5, label: 'Très dynamique', examples: 'Crypto, options, levier' },
]

const HORIZONS = [
  { id: 'short',  label: 'Court terme',  sub: '< 1 an'    },
  { id: 'medium', label: 'Moyen terme',  sub: '1 – 5 ans' },
  { id: 'long',   label: 'Long terme',   sub: '> 5 ans'   },
]

const PreferencesTab = () => {
  const [horizon, setHorizon] = useState('long')
  const [risk,    setRisk]    = useState(3)
  const [saving,  setSaving]  = useState(false)
  const [saved,   setSaved]   = useState(false)

  useEffect(() => {
    getPreferences()
      .then(r => { setHorizon(r.data.investment_horizon); setRisk(r.data.risk_appetite) })
      .catch(() => {})
  }, [])

  const handleSave = async () => {
    setSaving(true)
    try { await updatePreferences(horizon, risk); setSaved(true); setTimeout(() => setSaved(false), 2500) }
    catch {} finally { setSaving(false) }
  }

  const current = RISK_LEVELS.find(l => l.value === risk) || RISK_LEVELS[2]

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Horizon d'investissement</p>
        <div className="grid grid-cols-3 gap-2">
          {HORIZONS.map(h => (
            <button key={h.id} onClick={() => setHorizon(h.id)}
              className={`p-3 rounded-lg border text-left transition ${
                horizon === h.id
                  ? 'border-[#C9A84C] bg-[#C9A84C]/10'
                  : 'border-[#2A2A2A] bg-[#1A1A1A] hover:border-[#333]'
              }`}>
              <p className={`text-sm font-medium mt-1 ${horizon === h.id ? 'text-[#C9A84C]' : 'text-gray-300'}`}>{h.label}</p>
              <p className="text-xs text-gray-600">{h.sub}</p>
            </button>
          ))}
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Appétence au risque</p>
          <span className="text-xs font-medium text-[#C9A84C] bg-[#C9A84C]/10 px-2.5 py-1 rounded-full border border-[#C9A84C]/20">
            {current.label}
          </span>
        </div>
        <input type="range" min={1} max={5} step={1} value={risk}
          onChange={e => setRisk(Number(e.target.value))}
          className="w-full h-1.5 rounded-lg appearance-none cursor-pointer mb-3"
          style={{ accentColor: '#C9A84C' }} />
        <div className="flex justify-between mb-4">
          {RISK_LEVELS.map(l => (
            <button key={l.value} onClick={() => setRisk(l.value)}
              className={`text-xs font-medium transition ${risk === l.value ? 'text-[#C9A84C]' : 'text-gray-600 hover:text-gray-400'}`}>
              {l.value}
            </button>
          ))}
        </div>
        <div className="p-3 rounded-lg bg-[#1A1A1A] border border-[#2A2A2A]">
          <p className="text-sm font-medium text-white mb-0.5">Niveau {risk}/5 — {current.label}</p>
          <p className="text-xs text-gray-500">{current.examples}</p>
        </div>
      </div>

      <button onClick={handleSave} disabled={saving}
        className="w-full py-2 btn-gold rounded-lg text-sm disabled:opacity-40">
        {saving ? 'Enregistrement…' : saved ? 'Préférences sauvegardées' : 'Enregistrer les préférences'}
      </button>
    </div>
  )
}

export const SettingsModal = ({ isOpen, onClose }) => {
  const [settingsTab, setSettingsTab] = useState('keys')
  const [status,      setStatus]      = useState({})
  const [keys,        setKeys]        = useState({})
  const [show,        setShow]        = useState({})
  const [masked,      setMasked]      = useState({})
  const [saving,      setSaving]      = useState({})
  const [deleting,    setDeleting]    = useState({})
  const [testing,     setTesting]     = useState({})
  const [testResults, setTestResults] = useState({})
  const [savedMsg,    setSavedMsg]    = useState({})

  const refresh = () => getSettings().then(r => setStatus(r.data)).catch(() => {})

  useEffect(() => {
    if (isOpen) {
      setSettingsTab('keys'); setKeys({}); setShow({}); setMasked({}); setTestResults({}); setSavedMsg({})
      refresh()
    }
  }, [isOpen])

  const handleReveal = async (id, dbKey) => {
    if (show[id]) { setShow(s => ({ ...s, [id]: false })); setMasked(m => ({ ...m, [id]: null })); return }
    try {
      const res = await getMaskedKey(dbKey)
      setMasked(m => ({ ...m, [id]: res.data.masked })); setShow(s => ({ ...s, [id]: true }))
    } catch {}
  }

  const handleSave = async (id, updateFn) => {
    const val = keys[id]?.trim()
    if (!val) return
    setSaving(s => ({ ...s, [id]: true }))
    try {
      await updateFn(val); await refresh()
      setKeys(k => ({ ...k, [id]: '' })); setMasked(m => ({ ...m, [id]: null })); setShow(s => ({ ...s, [id]: false }))
      setSavedMsg(m => ({ ...m, [id]: 'Clé sauvegardée.' }))
      setTimeout(() => setSavedMsg(m => ({ ...m, [id]: '' })), 3000)
    } catch { setSavedMsg(m => ({ ...m, [id]: 'Erreur.' })) }
    finally { setSaving(s => ({ ...s, [id]: false })) }
  }

  const handleDelete = async (id, deleteFn) => {
    if (!window.confirm('Supprimer cette clé API ?')) return
    setDeleting(d => ({ ...d, [id]: true }))
    try { await deleteFn(); await refresh(); setMasked(m => ({ ...m, [id]: null })) }
    catch {} finally { setDeleting(d => ({ ...d, [id]: false })) }
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

  const KeyField = ({ id, dbKey, isConfigured, updateFn, deleteFn, testFn, link, linkText }) => {
    const inputVal = keys[id] ?? ''
    const isTyping = inputVal.length > 0
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
              onChange={e => { if (!(!isTyping && show[id] && masked[id])) setKeys(k => ({ ...k, [id]: e.target.value })) }}
              className={`${INPUT} pr-14 ${!isTyping && show[id] && masked[id] ? 'font-mono text-gray-400' : ''}`}
            />
            <button type="button" onMouseDown={e => e.preventDefault()}
              onClick={() => isConfigured && !isTyping ? handleReveal(id, dbKey) : setShow(s => ({ ...s, [id]: !s[id] }))}
              className="absolute right-2 top-2 text-xs text-gray-600 hover:text-gray-300 px-1 py-0.5 rounded">
              {show[id] ? 'Cacher' : 'Voir'}
            </button>
          </div>
          <button onClick={() => handleSave(id, updateFn)} disabled={!isTyping || saving[id]}
            className="px-3 py-2 btn-gold rounded-lg text-xs disabled:opacity-40 whitespace-nowrap">
            {saving[id] ? '…' : 'Sauvegarder'}
          </button>
        </div>

        {savedMsg[id] && (
          <p className={`text-xs mb-2 ${savedMsg[id].includes('Erreur') ? 'text-red-400' : 'text-green-400'}`}>
            {savedMsg[id]}
          </p>
        )}

        <div className="flex gap-2">
          {testFn && (
            <button onClick={() => handleTest(id, testFn)} disabled={testing[id] || !isConfigured}
              className="flex-1 py-1.5 border border-[#2A2A2A] rounded-lg text-xs text-gray-500 hover:bg-[#1A1A1A] disabled:opacity-40 transition">
              {testing[id] ? 'Test…' : 'Tester'}
            </button>
          )}
          {link && (
            <a href={link} target="_blank" rel="noreferrer"
              className="flex-1 py-1.5 text-center border border-[#2A2A2A] rounded-lg text-xs text-[#C9A84C] hover:bg-[#1A1A1A] transition">
              {linkText} →
            </a>
          )}
          {isConfigured && deleteFn && (
            <button onClick={() => handleDelete(id, deleteFn)} disabled={deleting[id]}
              className="py-1.5 px-3 border border-red-800/40 rounded-lg text-xs text-red-500 hover:bg-red-900/20 disabled:opacity-40 transition">
              {deleting[id] ? '…' : 'Supprimer'}
            </button>
          )}
        </div>

        {testResults[id] && (
          <div className={`mt-2 p-2 rounded text-xs ${testResults[id].success ? 'bg-green-900/20 text-green-400 border border-green-800/40' : 'bg-red-900/20 text-red-400 border border-red-800/40'}`}>
            {testResults[id].success ? '✓ ' : '✗ '}{testResults[id].message}
          </div>
        )}
      </div>
    )
  }

  const Badge = ({ isConfigured }) => (
    <div className={`flex items-center gap-1.5 text-xs font-medium ${isConfigured ? 'text-green-400' : 'text-gray-600'}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${isConfigured ? 'bg-green-500' : 'bg-gray-700'}`} />
      {isConfigured ? 'Configurée' : 'Non configurée'}
    </div>
  )

  return (
    <div className="fixed inset-0 bg-black/75 flex items-center justify-center z-50 p-4">
      <div className="bg-[#111111] border border-[#2A2A2A] rounded-xl max-w-lg w-full overflow-y-auto max-h-[90vh]">

        <div className="px-6 pt-6 pb-0 border-b border-[#2A2A2A]">
          <h2 className="text-lg font-semibold text-white mb-4">Paramètres</h2>
          <div className="flex gap-1">
            {[['keys', 'Clés API'], ['prefs', 'Préférences']].map(([id, label]) => (
              <button key={id} onClick={() => setSettingsTab(id)}
                className={`px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition ${
                  settingsTab === id ? 'border-[#C9A84C] text-[#C9A84C]' : 'border-transparent text-gray-500 hover:text-gray-300'
                }`}>
                {label}
              </button>
            ))}
          </div>
        </div>

        <div className="p-6">
          {settingsTab === 'prefs' && <PreferencesTab />}
          {settingsTab === 'keys' && (
            <>
              <p className="text-xs text-gray-500 mb-5">
                Clés stockées dans votre base de données locale — elles ne quittent jamais votre machine.
              </p>

              {/* Finnhub */}
              <div className="border border-[#2A2A2A] rounded-lg p-4 mb-4">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Prix des actifs — Finnhub</p>
                  <Badge isConfigured={status.finnhub_configured} />
                </div>
                <KeyField id="finnhub" dbKey="finnhub_api_key" isConfigured={status.finnhub_configured}
                  updateFn={updateFinnhubKey} deleteFn={deleteFinnhubKey} testFn={testFinnhubKey}
                  link="https://finnhub.io" linkText="Clé gratuite" />
              </div>

              {/* AI provider */}
              <div className="border border-[#2A2A2A] rounded-lg p-4 mb-4">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Fournisseur IA</p>
                <div className="grid grid-cols-3 gap-2 mb-4">
                  {AI_PROVIDERS.map(p => (
                    <button key={p.id} onClick={() => handleProviderChange(p.id)}
                      className={`p-2.5 rounded-lg border text-left transition ${
                        status.ai_provider === p.id
                          ? 'border-[#C9A84C] bg-[#C9A84C]/10'
                          : 'border-[#2A2A2A] bg-[#1A1A1A] hover:border-[#333]'
                      }`}>
                      <div className="flex items-center gap-1 mb-1">
                        {status.ai_provider === p.id && <span className="w-1.5 h-1.5 rounded-full bg-[#C9A84C] flex-shrink-0" />}
                        {p.free && <span className="text-xs bg-green-900/40 text-green-400 px-1 rounded font-medium border border-green-800/40">FREE</span>}
                      </div>
                      <p className="text-xs font-medium text-gray-300 leading-tight">{p.label}</p>
                      <p className="text-xs text-gray-600 mt-0.5">{p.badge}</p>
                    </button>
                  ))}
                </div>

                {status.ai_provider === 'claude' && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-xs text-gray-600">Clé Anthropic <a href="https://console.anthropic.com" target="_blank" rel="noreferrer" className="text-[#C9A84C] hover:underline">console.anthropic.com →</a></p>
                      <Badge isConfigured={status.anthropic_configured} />
                    </div>
                    <KeyField id="anthropic" dbKey="anthropic_api_key" isConfigured={status.anthropic_configured}
                      updateFn={updateAnthropicKey} deleteFn={deleteAnthropicKey} testFn={testAnthropicKey} />
                  </div>
                )}
                {status.ai_provider === 'gemini' && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-xs text-gray-600">Clé Google Gemini <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer" className="text-[#C9A84C] hover:underline">aistudio.google.com →</a></p>
                      <Badge isConfigured={status.gemini_configured} />
                    </div>
                    <KeyField id="gemini" dbKey="gemini_api_key" isConfigured={status.gemini_configured}
                      updateFn={updateGeminiKey} deleteFn={deleteGeminiKey} testFn={testGeminiKey} />
                  </div>
                )}
                {status.ai_provider === 'groq' && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-xs text-gray-600">Clé Groq <a href="https://console.groq.com/keys" target="_blank" rel="noreferrer" className="text-[#C9A84C] hover:underline">console.groq.com →</a></p>
                      <Badge isConfigured={status.groq_configured} />
                    </div>
                    <KeyField id="groq" dbKey="groq_api_key" isConfigured={status.groq_configured}
                      updateFn={updateGroqKey} deleteFn={deleteGroqKey} testFn={testGroqKey} />
                  </div>
                )}
              </div>

              {/* NewsAPI */}
              <div className="border border-[#2A2A2A] rounded-lg p-4 mb-5">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Actualités — NewsAPI</p>
                  <Badge isConfigured={status.newsapi_configured} />
                </div>
                <p className="text-xs text-gray-600 mb-3">Gratuit jusqu'à 100 req/jour.</p>
                <KeyField id="newsapi" dbKey="newsapi_key" isConfigured={status.newsapi_configured}
                  updateFn={updateNewsApiKey} deleteFn={deleteNewsApiKey} testFn={testNewsApiKey}
                  link="https://newsapi.org/register" linkText="Clé gratuite" />
              </div>

              <button onClick={onClose}
                className="w-full py-2 bg-[#1A1A1A] border border-[#2A2A2A] text-gray-400 rounded-lg hover:bg-[#222] text-sm transition">
                Fermer
              </button>
            </>
          )}
        </div>
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
      setPriceUnavailable(false); setError('')
    }
  }, [isOpen, holding])

  useEffect(() => {
    if (!holding?.symbol || !purchaseDate) return
    if (purchaseDate === holding.purchase_date) return
    setFetchingPrice(true); setHistoricalPrice(null); setPriceUnavailable(false); setExactPrice('')
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
    } catch (err) { setError(err.response?.data?.detail || err.message) }
    finally { setLoading(false) }
  }

  if (!isOpen || !holding) return null

  return (
    <div className="fixed inset-0 bg-black/75 flex items-center justify-center z-50 p-4">
      <div className="bg-[#111111] border border-[#2A2A2A] rounded-xl p-6 max-w-md w-full">
        <h2 className="text-lg font-semibold text-white mb-1">Modifier l'ordre</h2>
        <p className="text-sm text-gray-500 mb-5">{holding.symbol} — {holding.name}</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className={LABEL}>Date d'achat *</label>
            <input type="date" value={purchaseDate} onChange={e => setPurchaseDate(e.target.value)}
              max={today} required className={INPUT} style={{ colorScheme: 'dark' }} />
          </div>

          {(fetchingPrice || historicalPrice || priceUnavailable) && (
            <div className={`p-3 rounded-lg text-sm ${priceUnavailable ? 'bg-amber-900/20 border border-amber-800/40 text-amber-400' : 'bg-[#C9A84C]/10 border border-[#C9A84C]/20 text-[#C9A84C]'}`}>
              {fetchingPrice && <div className="flex items-center gap-2"><div className="animate-spin rounded-full h-4 w-4 border-2 border-[#C9A84C] border-t-transparent" />Récupération…</div>}
              {!fetchingPrice && historicalPrice && !exactPrice && <span>Prix de clôture : <strong>{historicalPrice.toFixed(4)} €</strong></span>}
              {!fetchingPrice && historicalPrice && exactPrice && <span>Historique : {historicalPrice.toFixed(4)} € — <strong>remplacé par {parseFloat(exactPrice).toFixed(4)} €</strong></span>}
              {!fetchingPrice && priceUnavailable && <span>Prix introuvable — entrez-le manuellement.</span>}
            </div>
          )}

          <div>
            <label className={LABEL}>{priceUnavailable ? 'Prix unitaire *' : 'Prix unitaire (optionnel)'}</label>
            <input type="number" step="0.0001" min="0"
              placeholder={historicalPrice ? `${historicalPrice.toFixed(4)} (automatique)` : 'Ex: 6.57'}
              value={exactPrice} onChange={e => setExactPrice(e.target.value)}
              required={priceUnavailable && !historicalPrice}
              className={INPUT} />
          </div>

          <div>
            <label className={LABEL}>Quantité *</label>
            <input type="number" step="0.0001" min="0" value={quantity}
              onChange={e => setQuantity(e.target.value)} required className={INPUT} />
          </div>

          {effectivePrice && quantity && (
            <div className="text-xs text-gray-500 text-right">
              Total : <strong className="text-[#C9A84C]">{(effectivePrice * parseFloat(quantity)).toFixed(2)} €</strong>
            </div>
          )}

          <div>
            <label className={LABEL}>Notes (optionnel)</label>
            <input type="text" value={notes} onChange={e => setNotes(e.target.value)}
              placeholder="Ex: Investissement long terme" className={INPUT} />
          </div>

          {error && <div className="p-3 bg-red-900/20 border border-red-800/40 rounded-lg text-red-400 text-sm">{error}</div>}

          <div className="flex gap-2 pt-1">
            <button type="submit" disabled={!canSubmit}
              className="flex-1 btn-gold py-2 rounded-lg text-sm disabled:opacity-40">
              {loading ? 'Enregistrement…' : 'Enregistrer'}
            </button>
            <button type="button" onClick={onClose}
              className="flex-1 bg-[#1A1A1A] border border-[#2A2A2A] text-gray-400 py-2 rounded-lg hover:bg-[#222] text-sm transition">
              Annuler
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
