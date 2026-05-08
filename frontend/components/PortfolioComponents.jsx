import React, { useState, useEffect, useRef, useMemo } from 'react'
import { formatCurrency, formatPercent, getColorClass, getBackgroundColorClass } from '@/lib/utils'
import { getPortfolioHistory, getAssetPriceHistory, searchAssets } from '@/lib/api'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ReferenceLine, ResponsiveContainer
} from 'recharts'

export const PortfolioSummary = ({ portfolio }) => {
  if (!portfolio || !portfolio.stats) return <div>Aucune donnée</div>

  const stats = portfolio.stats
  const gainLoss = stats.total_gain_loss
  const gainLossPercent = stats.gain_loss_percent
  const distinctCount = new Set((portfolio.holdings || []).map(h => h.symbol)).size

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div className="bg-white rounded-lg p-6 shadow">
        <h3 className="text-gray-500 text-sm font-medium">Total Investi</h3>
        <p className="text-2xl font-bold mt-2">{formatCurrency(stats.total_invested)}</p>
      </div>
      <div className="bg-white rounded-lg p-6 shadow">
        <h3 className="text-gray-500 text-sm font-medium">Valeur Actuelle</h3>
        <p className="text-2xl font-bold mt-2">{formatCurrency(stats.total_current_value)}</p>
      </div>
      <div className={`rounded-lg p-6 shadow ${getBackgroundColorClass(gainLoss)}`}>
        <h3 className="text-gray-500 text-sm font-medium">Gain/Perte</h3>
        <p className={`text-2xl font-bold mt-2 ${getColorClass(gainLoss)}`}>{formatCurrency(gainLoss)}</p>
        <p className={`text-sm mt-1 ${getColorClass(gainLoss)}`}>{formatPercent(gainLossPercent)}</p>
      </div>
      <div className="bg-white rounded-lg p-6 shadow">
        <h3 className="text-gray-500 text-sm font-medium">Titres distincts</h3>
        <p className="text-2xl font-bold mt-2">{distinctCount}</p>
      </div>
    </div>
  )
}

export const HoldingsList = ({ holdings, onDelete, onEdit }) => {
  if (!holdings || holdings.length === 0) {
    return (
      <div className="bg-white rounded-lg p-6 shadow text-center">
        <p className="text-gray-500">Aucune position dans le portefeuille</p>
      </div>
    )
  }

  const handleDelete = (holdingId, symbol) => {
    if (window.confirm(`Supprimer la position ${symbol} ?`)) onDelete(holdingId)
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50 border-b">
          <tr>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Date</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Actif</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Qté</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Prix d'Achat</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Prix Actuel</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Investi</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Valeur Actuelle</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Gain/Perte</th>
            <th className="px-6 py-3"></th>
          </tr>
        </thead>
        <tbody>
          {holdings.map((holding, idx) => {
            const gainLoss = holding.gain_loss
            const dateLabel = holding.purchase_date
              ? new Date(holding.purchase_date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
              : '—'
            return (
              <tr key={idx} className="border-b hover:bg-gray-50">
                <td className="px-6 py-4 text-sm text-gray-500 whitespace-nowrap">{dateLabel}</td>
                <td className="px-6 py-4">
                  <p className="font-semibold text-gray-900">{holding.symbol}</p>
                  <p className="text-xs text-gray-500">{holding.name}</p>
                </td>
                <td className="px-6 py-4 text-gray-700">{holding.quantity.toFixed(4)}</td>
                <td className="px-6 py-4 text-gray-700">{formatCurrency(holding.avg_price)}</td>
                <td className="px-6 py-4 text-gray-700">{formatCurrency(holding.current_price)}</td>
                <td className="px-6 py-4 text-gray-700">{formatCurrency(holding.invested)}</td>
                <td className="px-6 py-4 text-gray-700">{formatCurrency(holding.current_value)}</td>
                <td className={`px-6 py-4 font-semibold ${getColorClass(gainLoss)}`}>
                  <div>{formatCurrency(gainLoss)}</div>
                  <div className="text-xs">{formatPercent(holding.gain_loss_percent)}</div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-6">
                    <button
                      onClick={() => onEdit && onEdit(holding)}
                      className="text-gray-400 hover:text-blue-600 transition"
                      title="Modifier cet ordre"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      onClick={() => handleDelete(holding.id, holding.symbol)}
                      className="text-gray-400 hover:text-red-600 text-xl transition"
                      title="Supprimer cette position"
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export const ConsolidatedView = ({ holdings }) => {
  if (!holdings || holdings.length === 0) {
    return (
      <div className="bg-white rounded-lg p-6 shadow text-center">
        <p className="text-gray-500">Aucune position dans le portefeuille</p>
      </div>
    )
  }

  // Regrouper par symbole et calculer les valeurs consolidées
  const grouped = {}
  for (const h of holdings) {
    if (!grouped[h.symbol]) {
      grouped[h.symbol] = {
        symbol: h.symbol,
        name: h.name,
        current_price: h.current_price,
        total_quantity: 0,
        total_invested: 0,
      }
    }
    grouped[h.symbol].total_quantity += h.quantity
    grouped[h.symbol].total_invested += h.invested
    grouped[h.symbol].current_price = h.current_price
  }

  const totalPortfolioValue = Object.values(grouped).reduce((sum, g) => {
    return sum + g.total_quantity * g.current_price
  }, 0)

  const consolidated = Object.values(grouped).map(g => {
    const current_value = g.total_quantity * g.current_price
    const gain_loss = current_value - g.total_invested
    const gain_loss_percent = g.total_invested > 0 ? (gain_loss / g.total_invested) * 100 : 0
    const weight = totalPortfolioValue > 0 ? (current_value / totalPortfolioValue) * 100 : 0
    return {
      ...g,
      avg_price: g.total_invested / g.total_quantity,
      current_value,
      gain_loss,
      gain_loss_percent,
      weight,
    }
  }).sort((a, b) => b.gain_loss_percent - a.gain_loss_percent)

  return (
    <div className="bg-white rounded-lg shadow overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50 border-b">
          <tr>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Titre</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Qté totale</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">PRU</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Prix Actuel</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Investi</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Valeur Actuelle</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Gain/Perte</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Poids</th>
          </tr>
        </thead>
        <tbody>
          {consolidated.map((item, idx) => {
            const gl = item.gain_loss
            return (
              <tr key={idx} className="border-b hover:bg-gray-50">
                <td className="px-6 py-4">
                  <p className="font-semibold text-gray-900">{item.symbol}</p>
                  <p className="text-xs text-gray-500">{item.name}</p>
                </td>
                <td className="px-6 py-4 text-gray-700">{item.total_quantity.toFixed(4)}</td>
                <td className="px-6 py-4 text-gray-700">{formatCurrency(item.avg_price)}</td>
                <td className="px-6 py-4 text-gray-700">{formatCurrency(item.current_price)}</td>
                <td className="px-6 py-4 text-gray-700">{formatCurrency(item.total_invested)}</td>
                <td className="px-6 py-4 text-gray-700">{formatCurrency(item.current_value)}</td>
                <td className={`px-6 py-4 font-semibold ${getColorClass(gl)}`}>
                  <div>{formatCurrency(gl)}</div>
                  <div className="text-xs">{formatPercent(item.gain_loss_percent)}</div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className="w-16 bg-gray-200 rounded-full h-1.5">
                      <div
                        className="bg-blue-500 h-1.5 rounded-full"
                        style={{ width: `${Math.min(item.weight, 100)}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-600">{item.weight.toFixed(1)}%</span>
                  </div>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

const PERIODS = [
  { key: '1d',  label: '1J' },
  { key: '1w',  label: '1S' },
  { key: '1mo', label: '1M' },
  { key: '1y',  label: '1A' },
  { key: 'all', label: 'Tout' },
]
const COMP_COLORS = ['#3b82f6', '#8b5cf6', '#f59e0b', '#06b6d4', '#ec4899', '#84cc16']

// Tick X-axis sur deux lignes : date (ligne 1) + heure (ligne 2)
const MultiLineTick = ({ x, y, payload, period }) => {
  if (!payload?.value) return null
  const d = new Date(payload.value)
  const intraday = payload.value?.includes('T')
  let line1 = '', line2 = ''

  if (period === '1d') {
    line1 = d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
  } else if (period === '1w') {
    line1 = d.toLocaleDateString('fr-FR', { weekday: 'short', day: '2-digit' })
    line2 = d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
  } else if (period === '1mo') {
    line1 = d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })
    line2 = intraday ? d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }) : ''
  } else {
    line1 = d.toLocaleDateString('fr-FR', { month: 'short', year: '2-digit' })
  }

  return (
    <g transform={`translate(${x},${y})`}>
      <text x={0} y={0} dy={14} textAnchor="middle" fill="#9ca3af" fontSize={11}>{line1}</text>
      {line2 && <text x={0} y={0} dy={26} textAnchor="middle" fill="#9ca3af" fontSize={10}>{line2}</text>}
    </g>
  )
}

const normalize = (data) => {
  if (!data?.length) return []
  const first = data[0].value
  if (!first) return []
  return data.map(d => ({ date: d.date, pct: ((d.value / first) - 1) * 100 }))
}

// Normalise un actif depuis une date de référence (date de début du portefeuille).
// Garantit que toutes les courbes démarrent à 0% au même point.
const normalizeFromDate = (data, startDate) => {
  if (!data?.length) return []
  const entry = data.find(d => d.date >= startDate) || data[0]
  if (!entry?.value) return normalize(data)
  const base = entry.value
  return data.map(d => ({ date: d.date, pct: ((d.value / base) - 1) * 100 }))
}

export const PortfolioChart = () => {
  const [period, setPeriod]             = useState('1mo')
  const [portfolioRaw, setPortfolioRaw] = useState([])
  const [orderDates, setOrderDates]     = useState([])
  const [totalInvested, setTotalInvested] = useState(null)
  const [loading, setLoading]           = useState(true)
  const [comparisons, setComparisons]   = useState([])
  const [query, setQuery]               = useState('')
  const [results, setResults]           = useState([])
  const [searching, setSearching]       = useState(false)
  const [showDrop, setShowDrop]         = useState(false)

  const hasComp = comparisons.length > 0
  // Ref pour éviter le problème de closure dans les useEffect
  const comparisonsRef = useRef(comparisons)
  useEffect(() => { comparisonsRef.current = comparisons }, [comparisons])

  // Chargement portefeuille — spinner uniquement au premier chargement
  useEffect(() => {
    if (portfolioRaw.length === 0) setLoading(true)
    getPortfolioHistory(period)
      .then(r => {
        setPortfolioRaw(r.data.data || [])
        setOrderDates(r.data.order_dates || [])
        if (r.data.total_invested) setTotalInvested(r.data.total_invested)
      })
      .finally(() => setLoading(false))
  }, [period])

  // Re-chargement comparaisons quand la période change
  // On garde les anciennes données visibles (pas de data: []) pendant le fetch
  useEffect(() => {
    if (!comparisonsRef.current.length) return
    setComparisons(prev => prev.map(c => ({ ...c, loading: true })))
    comparisonsRef.current.forEach(c => fetchComp(c.symbol))
  }, [period])

  // Recherche avec debounce
  useEffect(() => {
    if (query.length < 2) { setResults([]); setShowDrop(false); return }
    const t = setTimeout(() => {
      setSearching(true)
      searchAssets(query)
        .then(r => { setResults(r.data.results || []); setShowDrop(true) })
        .catch(() => {})
        .finally(() => setSearching(false))
    }, 400)
    return () => clearTimeout(t)
  }, [query])

  const fetchComp = (symbol) => {
    getAssetPriceHistory(symbol, period)
      .then(r => setComparisons(prev => prev.map(c =>
        c.symbol === symbol ? { ...c, data: r.data.data || [], loading: false } : c
      )))
      .catch(() => setComparisons(prev => prev.map(c =>
        c.symbol === symbol ? { ...c, loading: false } : c
      )))
  }

  const addComp = (asset) => {
    if (comparisons.some(c => c.symbol === asset.symbol) || comparisons.length >= 5) return
    const color = COMP_COLORS[comparisons.length % COMP_COLORS.length]
    setComparisons(prev => [...prev, { symbol: asset.symbol, name: asset.name, color, visible: true, data: [], loading: true }])
    setQuery(''); setShowDrop(false)
    fetchComp(asset.symbol)
  }

  // Construction des données du graphique
  const chartData = useMemo(() => {
    if (!portfolioRaw.length) return []
    if (!hasComp) return portfolioRaw

    const portNorm = portfolioRaw.map(d => ({
      date: d.date,
      pct: d.twr !== undefined ? d.twr - 100 : ((d.value / portfolioRaw[0].value) - 1) * 100
    }))

    // Détecte si les données du portefeuille sont intraday (horodatage avec heure)
    const isIntraday = portNorm.some(d => d.date?.includes('T'))
    const portfolioStartDateKey = (portNorm[0]?.date ?? '').split('T')[0]

    // Pour intraday : normalise depuis la première donnée dispo (cohérent avec TWR)
    // Pour daily    : normalise depuis la date de début du portefeuille (alignement Tout/1A)
    const compMaps = comparisons
      .filter(c => c.visible && c.data.length > 0)
      .map(c => {
        const norm = isIntraday
          ? normalize(c.data)
          : normalizeFromDate(c.data, portfolioStartDateKey)
        return { symbol: c.symbol, map: new Map(norm.map(d => [d.date.split('T')[0], d.pct])) }
      })

    // Pour intraday : une seule valeur de comparaison par jour (premier timestamp),
    // connectNulls=true trace une ligne lisse entre les points journaliers.
    const seenDates = new Set()
    return portNorm.map(d => {
      const dk = d.date.split('T')[0]
      const isFirst = !seenDates.has(dk)
      if (isFirst) seenDates.add(dk)
      return {
        date: d.date,
        portfolio: d.pct,
        ...Object.fromEntries(compMaps.map(cm => [
          cm.symbol,
          isFirst ? cm.map.get(dk) ?? null : null
        ]))
      }
    })
  }, [portfolioRaw, comparisons, hasComp])

  // Métriques
  const rawFirst  = portfolioRaw[0]?.value
  const rawLast   = portfolioRaw[portfolioRaw.length - 1]?.value
  const twrLast   = portfolioRaw[portfolioRaw.length - 1]?.twr
  const twrPct    = twrLast !== undefined ? twrLast - 100 : null

  // Mode solo :
  // - "all"   : (valeur_actuelle - capital_investi) / capital_investi  → rendement réel sur le capital
  // - autres  : TWR de la période → hors effet des dépôts (identique au mode comparaison)
  const soloPct = period === 'all' && totalInvested && rawLast
    ? ((rawLast - totalInvested) / totalInvested) * 100
    : twrPct

  const isPos     = hasComp ? (twrPct === null || twrPct >= 0) : (soloPct === null || soloPct >= 0)
  const portColor = isPos ? '#10b981' : '#ef4444'

  // ~8 ticks répartis uniformément sur tous les périodes (évite le vide avant le dernier tick)
  const xAxisInterval = Math.max(1, Math.floor(chartData.length / 8))

  const formatY = hasComp
    ? v => `${v >= 0 ? '+' : ''}${v.toFixed(1)}%`
    : v => v >= 10000 ? `${(v/1000).toFixed(0)}k€` : v >= 1000 ? `${(v/1000).toFixed(1)}k€` : `${v.toFixed(0)}€`

  const TooltipContent = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null
    const d = new Date(label)
    const dl = period === '1d'
      ? d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
      : (period === 'all' || period === '1y')
        ? d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: '2-digit' })
        : d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })
          + (label?.includes('T') ? ' ' + d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }) : '')
    return (
      <div className="bg-white border border-gray-200 rounded-lg shadow-lg px-4 py-3 text-sm min-w-[160px]">
        <p className="text-gray-400 text-xs mb-2">{dl}</p>
        {payload.filter(p => p.value !== null).map((p, i) => {
          const isPort = p.dataKey === 'portfolio' || p.dataKey === 'value'
          const lbl = isPort ? 'Portefeuille' : p.dataKey
          const val = hasComp ? `${p.value >= 0 ? '+' : ''}${p.value?.toFixed(2)}%` : formatCurrency(p.value)
          return (
            <div key={i} className="flex items-center justify-between gap-4 mb-1">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: p.stroke }} />
                <span className="text-gray-600">{lbl}</span>
              </div>
              <span className="font-semibold text-gray-900">{val}</span>
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      {/* En-tête */}
      <div className="flex items-start justify-between mb-6">
        <div>
          {!hasComp && rawLast && (
            <>
              <p className="text-3xl font-bold text-gray-900">{formatCurrency(rawLast)}</p>
              {soloPct !== null && (
                <p className={`text-sm font-medium mt-1 ${isPos ? 'text-green-600' : 'text-red-600'}`}>
                  {isPos ? '+' : ''}{soloPct.toFixed(2)}%
                  <span className="text-gray-400 font-normal ml-1">
                    {period === 'all' ? 'sur le capital investi' : 'sur la période'}
                  </span>
                </p>
              )}
            </>
          )}
          {hasComp && (
            <div className="flex flex-wrap gap-3 items-center">
              <div className="flex items-center gap-1.5 text-sm">
                <span className="w-3 h-3 rounded-full" style={{ backgroundColor: portColor }} />
                <span className="text-gray-600 font-medium">Portefeuille</span>
                {twrPct !== null && (
                  <span className={`font-semibold ${isPos ? 'text-green-600' : 'text-red-600'}`}>
                    {isPos ? '+' : ''}{twrPct.toFixed(2)}%
                  </span>
                )}
                <span className="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded font-normal" title="Time-Weighted Return — élimine l'effet des dépôts">TWR</span>
              </div>
              {comparisons.filter(c => c.visible && c.data.length > 0).map(c => {
                const isIntraday = portfolioRaw.some(d => d.date?.includes('T'))
                const startKey = (portfolioRaw[0]?.date ?? '').split('T')[0]
                const n = isIntraday ? normalize(c.data) : normalizeFromDate(c.data, startKey)
                const last = n[n.length - 1]?.pct
                return (
                  <div key={c.symbol} className="flex items-center gap-1.5 text-sm">
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: c.color }} />
                    <span className="text-gray-600 font-medium">{c.symbol}</span>
                    {last !== undefined && (
                      <span className={`font-semibold ${last >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {last >= 0 ? '+' : ''}{last.toFixed(2)}%
                      </span>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Sélecteur période */}
        <div className="flex gap-1 bg-gray-100 p-1 rounded-lg flex-shrink-0">
          {PERIODS.map(p => (
            <button key={p.key} onClick={() => setPeriod(p.key)}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                period === p.key ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
              }`}>
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Graphique */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      ) : chartData.length < 2 ? (
        <div className="flex items-center justify-center h-64 text-gray-400 text-sm">Pas assez de données pour cette période.</div>
      ) : (
        <ResponsiveContainer width="100%" height={320}>
          <AreaChart data={chartData} margin={{ top: 4, right: 4, left: 0, bottom: 8 }}>
            <defs>
              <linearGradient id="gPort" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor={portColor} stopOpacity={hasComp ? 0.04 : 0.18} />
                <stop offset="95%" stopColor={portColor} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" vertical={false} />
            <XAxis dataKey="date"
              tick={<MultiLineTick period={period} />}
              tickLine={false} axisLine={false}
              interval={xAxisInterval}
              minTickGap={60}
              height={period === '1w' || period === '1mo' ? 42 : 24} />
            <YAxis tickFormatter={formatY} tick={{ fontSize: 11, fill: '#9ca3af' }}
              tickLine={false} axisLine={false} width={56} domain={['auto', 'auto']} />
            <Tooltip content={<TooltipContent />} />

            {!hasComp && orderDates.map(d => (
              <ReferenceLine key={d} x={d} stroke="#ef4444" strokeWidth={1} strokeDasharray="4 3" strokeOpacity={0.7} />
            ))}

            {/* Portefeuille */}
            <Area type="monotone" dataKey={hasComp ? 'portfolio' : 'value'}
              stroke={portColor} strokeWidth={2} fill="url(#gPort)"
              dot={false} activeDot={{ r: 4, fill: portColor, strokeWidth: 0 }} />

            {/* Courbes de comparaison */}
            {comparisons.filter(c => c.visible && c.data.length > 0).map(c => (
              <Area key={c.symbol} type="monotone" dataKey={c.symbol}
                stroke={c.color} strokeWidth={2} fill="none"
                dot={false} activeDot={{ r: 4, fill: c.color, strokeWidth: 0 }}
                connectNulls={true} />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      )}

      {/* Panneau comparaison */}
      <div className="mt-6 pt-5 border-t border-gray-100">
        <p className="text-sm font-medium text-gray-700 mb-3">Comparer avec</p>

        {/* Barre de recherche */}
        <div className="relative">
          <input type="text" value={query}
            onChange={e => setQuery(e.target.value)}
            onBlur={() => setTimeout(() => setShowDrop(false), 150)}
            onFocus={() => results.length > 0 && setShowDrop(true)}
            placeholder="Rechercher un actif (AAPL, S&P 500, Bitcoin…)"
            className="w-full px-4 py-2 pr-10 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
          <div className="absolute right-3 top-2.5 text-gray-400">
            {searching
              ? <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500" />
              : <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
                </svg>
            }
          </div>
          {showDrop && results.length > 0 && (
            <div className="absolute w-full bg-white border border-gray-200 rounded-lg shadow-lg mt-1 z-10 max-h-48 overflow-y-auto">
              {results.map((a, i) => (
                <button key={i} onMouseDown={() => addComp(a)}
                  disabled={comparisons.some(c => c.symbol === a.symbol) || comparisons.length >= 5}
                  className="w-full px-4 py-2.5 text-left hover:bg-blue-50 border-b last:border-0 flex justify-between items-center disabled:opacity-40 disabled:cursor-not-allowed">
                  <div>
                    <p className="font-medium text-sm text-gray-900">{a.display_symbol}</p>
                    <p className="text-xs text-gray-500 truncate">{a.name}</p>
                  </div>
                  <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded ml-2 flex-shrink-0">{a.type}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Liste des comparaisons */}
        {comparisons.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {comparisons.map(c => (
              <div key={c.symbol}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm transition-all ${
                  c.visible ? 'border-gray-200 bg-white' : 'border-gray-100 bg-gray-50 opacity-50'
                }`}>
                <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: c.color }} />
                <span className="font-medium text-gray-800">{c.symbol}</span>
                {c.loading && <div className="animate-spin rounded-full h-3 w-3 border-b border-gray-400" />}
                {/* Œil : masquer/afficher */}
                <button onClick={() => setComparisons(prev => prev.map(x => x.symbol === c.symbol ? { ...x, visible: !x.visible } : x))}
                  className="text-gray-400 hover:text-gray-700 transition">
                  {c.visible
                    ? <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20"><path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/><path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd"/></svg>
                    : <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clipRule="evenodd"/><path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.064 7 9.542 7 .847 0 1.669-.105 2.454-.303z"/></svg>
                  }
                </button>
                {/* Supprimer */}
                <button onClick={() => setComparisons(prev => prev.filter(x => x.symbol !== c.symbol))}
                  className="text-gray-300 hover:text-red-500 transition ml-0.5">
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
        {comparisons.length >= 5 && (
          <p className="text-xs text-gray-400 mt-2">Maximum 5 comparaisons atteintes.</p>
        )}
      </div>
    </div>
  )
}

export const AssetsList = ({ assets, onDelete }) => {
  if (!assets || assets.length === 0) return null

  const TYPE_LABEL = { stock: 'Action', etf: 'ETF', crypto: 'Crypto', forex: 'Devise', bond: 'Obligation' }

  const handleDelete = (symbol) => {
    if (window.confirm(`Supprimer ${symbol} et toutes ses positions associées ?`)) {
      onDelete(symbol)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-700">Actifs suivis ({assets.length})</h3>
        <p className="text-xs text-gray-400">Supprimer un actif efface aussi toutes ses positions.</p>
      </div>
      <div className="divide-y divide-gray-50">
        {assets.map(asset => (
          <div key={asset.symbol} className="flex items-center justify-between px-6 py-3 hover:bg-gray-50">
            <div className="flex items-center gap-3">
              <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                asset.asset_type === 'etf'    ? 'bg-blue-100 text-blue-700'   :
                asset.asset_type === 'crypto' ? 'bg-orange-100 text-orange-700' :
                'bg-gray-100 text-gray-600'
              }`}>
                {TYPE_LABEL[asset.asset_type] ?? asset.asset_type}
              </span>
              <div>
                <span className="font-semibold text-gray-900 text-sm">{asset.symbol}</span>
                <span className="text-xs text-gray-500 ml-2">{asset.name}</span>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium text-gray-700">{formatCurrency(asset.current_price)}</span>
              <button onClick={() => handleDelete(asset.symbol)}
                className="text-gray-300 hover:text-red-500 transition text-lg leading-none"
                title={`Supprimer ${asset.symbol}`}>
                ×
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export const TopPerformers = ({ topGainer, topLoser }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
      <div className="bg-green-50 rounded-lg p-6 shadow border-l-4 border-green-500">
        <h3 className="text-green-700 font-semibold mb-4">🚀 Meilleur Performer</h3>
        {topGainer ? (
          <div>
            <p className="text-2xl font-bold text-green-700">{topGainer.symbol}</p>
            <p className="text-sm text-gray-600 mb-2">{topGainer.name}</p>
            <p className="text-green-600 font-semibold">{formatPercent(topGainer.gain_loss_percent)}</p>
            <p className="text-green-600">{formatCurrency(topGainer.gain_loss)}</p>
          </div>
        ) : (
          <p className="text-gray-500">Pas de données</p>
        )}
      </div>
      <div className="bg-red-50 rounded-lg p-6 shadow border-l-4 border-red-500">
        <h3 className="text-red-700 font-semibold mb-4">📉 Moins Bon Performer</h3>
        {topLoser ? (
          <div>
            <p className="text-2xl font-bold text-red-700">{topLoser.symbol}</p>
            <p className="text-sm text-gray-600 mb-2">{topLoser.name}</p>
            <p className="text-red-600 font-semibold">{formatPercent(topLoser.gain_loss_percent)}</p>
            <p className="text-red-600">{formatCurrency(topLoser.gain_loss)}</p>
          </div>
        ) : (
          <p className="text-gray-500">Pas de données</p>
        )}
      </div>
    </div>
  )
}
