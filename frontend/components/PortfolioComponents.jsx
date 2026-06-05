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
  const isPos = gainLoss >= 0

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div className="bg-[#111111] border border-[#2A2A2A] rounded-lg p-5">
        <p className="text-gray-500 text-xs font-medium uppercase tracking-wide">Total investi</p>
        <p className="text-2xl font-bold mt-2 text-white">{formatCurrency(stats.total_invested)}</p>
      </div>
      <div className="bg-[#111111] border border-[#2A2A2A] rounded-lg p-5">
        <p className="text-gray-500 text-xs font-medium uppercase tracking-wide">Valeur actuelle</p>
        <p className="text-2xl font-bold mt-2 text-white">{formatCurrency(stats.total_current_value)}</p>
      </div>
      <div className={`border rounded-lg p-5 ${isPos ? 'bg-green-900/10 border-green-800/30' : 'bg-red-900/10 border-red-800/30'}`}>
        <p className="text-gray-500 text-xs font-medium uppercase tracking-wide">Gain / Perte</p>
        <p className={`text-2xl font-bold mt-2 ${isPos ? 'text-green-400' : 'text-red-400'}`}>{formatCurrency(gainLoss)}</p>
        <p className={`text-sm mt-1 ${isPos ? 'text-green-500' : 'text-red-500'}`}>{formatPercent(gainLossPercent)}</p>
      </div>
      <div className="bg-[#111111] border border-[#2A2A2A] rounded-lg p-5">
        <p className="text-gray-500 text-xs font-medium uppercase tracking-wide">Titres distincts</p>
        <p className="text-2xl font-bold mt-2 text-white">{distinctCount}</p>
      </div>
    </div>
  )
}

export const HoldingsList = ({ holdings, onDelete, onEdit }) => {
  if (!holdings || holdings.length === 0) {
    return (
      <div className="p-10 text-center">
        <p className="text-gray-600">Aucune position dans le portefeuille</p>
      </div>
    )
  }

  const handleDelete = (holdingId, symbol) => {
    if (window.confirm(`Supprimer la position ${symbol} ?`)) onDelete(holdingId)
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="border-b border-[#2A2A2A]">
          <tr>
            {['Date', 'Actif', 'Qté', "Prix d'achat", 'Prix actuel', 'Investi', 'Valeur actuelle', 'Gain / Perte', ''].map(h => (
              <th key={h} className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {holdings.map((holding, idx) => {
            const gainLoss = holding.gain_loss
            const isPos = gainLoss >= 0
            const dateLabel = holding.purchase_date
              ? new Date(holding.purchase_date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
              : '—'
            return (
              <tr key={idx} className="border-b border-[#1A1A1A] hover:bg-[#1A1A1A] transition">
                <td className="px-6 py-4 text-sm text-gray-500 whitespace-nowrap">{dateLabel}</td>
                <td className="px-6 py-4">
                  <p className="font-semibold text-white text-sm">{holding.symbol}</p>
                  <p className="text-xs text-gray-600">{holding.name}</p>
                </td>
                <td className="px-6 py-4 text-gray-300 text-sm">{holding.quantity.toFixed(4)}</td>
                <td className="px-6 py-4 text-gray-300 text-sm">{formatCurrency(holding.avg_price)}</td>
                <td className="px-6 py-4 text-gray-300 text-sm">{formatCurrency(holding.current_price)}</td>
                <td className="px-6 py-4 text-gray-300 text-sm">{formatCurrency(holding.invested)}</td>
                <td className="px-6 py-4 text-gray-300 text-sm">{formatCurrency(holding.current_value)}</td>
                <td className={`px-6 py-4 text-sm font-semibold ${isPos ? 'text-green-400' : 'text-red-400'}`}>
                  <div>{formatCurrency(gainLoss)}</div>
                  <div className="text-xs font-normal">{formatPercent(holding.gain_loss_percent)}</div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-4">
                    <button
                      onClick={() => onEdit && onEdit(holding)}
                      className="text-gray-600 hover:text-[#C9A84C] transition"
                      title="Modifier"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      onClick={() => handleDelete(holding.id, holding.symbol)}
                      className="text-gray-600 hover:text-red-500 transition"
                      title="Supprimer"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
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
      <div className="p-10 text-center">
        <p className="text-gray-600">Aucune position dans le portefeuille</p>
      </div>
    )
  }

  const grouped = {}
  for (const h of holdings) {
    if (!grouped[h.symbol]) {
      grouped[h.symbol] = { symbol: h.symbol, name: h.name, current_price: h.current_price, total_quantity: 0, total_invested: 0 }
    }
    grouped[h.symbol].total_quantity += h.quantity
    grouped[h.symbol].total_invested += h.invested
    grouped[h.symbol].current_price = h.current_price
  }

  const totalPortfolioValue = Object.values(grouped).reduce((sum, g) => sum + g.total_quantity * g.current_price, 0)

  const consolidated = Object.values(grouped).map(g => {
    const current_value = g.total_quantity * g.current_price
    const gain_loss = current_value - g.total_invested
    const gain_loss_percent = g.total_invested > 0 ? (gain_loss / g.total_invested) * 100 : 0
    const weight = totalPortfolioValue > 0 ? (current_value / totalPortfolioValue) * 100 : 0
    return { ...g, avg_price: g.total_invested / g.total_quantity, current_value, gain_loss, gain_loss_percent, weight }
  }).sort((a, b) => b.gain_loss_percent - a.gain_loss_percent)

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="border-b border-[#2A2A2A]">
          <tr>
            {['Titre', 'Qté totale', 'PRU', 'Prix actuel', 'Investi', 'Valeur actuelle', 'Gain / Perte', 'Poids'].map(h => (
              <th key={h} className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {consolidated.map((item, idx) => {
            const isPos = item.gain_loss >= 0
            return (
              <tr key={idx} className="border-b border-[#1A1A1A] hover:bg-[#1A1A1A] transition">
                <td className="px-6 py-4">
                  <p className="font-semibold text-white text-sm">{item.symbol}</p>
                  <p className="text-xs text-gray-600">{item.name}</p>
                </td>
                <td className="px-6 py-4 text-gray-300 text-sm">{item.total_quantity.toFixed(4)}</td>
                <td className="px-6 py-4 text-gray-300 text-sm">{formatCurrency(item.avg_price)}</td>
                <td className="px-6 py-4 text-gray-300 text-sm">{formatCurrency(item.current_price)}</td>
                <td className="px-6 py-4 text-gray-300 text-sm">{formatCurrency(item.total_invested)}</td>
                <td className="px-6 py-4 text-gray-300 text-sm">{formatCurrency(item.current_value)}</td>
                <td className={`px-6 py-4 text-sm font-semibold ${isPos ? 'text-green-400' : 'text-red-400'}`}>
                  <div>{formatCurrency(item.gain_loss)}</div>
                  <div className="text-xs font-normal">{formatPercent(item.gain_loss_percent)}</div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className="w-16 bg-[#2A2A2A] rounded-full h-1">
                      <div className="bg-[#C9A84C] h-1 rounded-full" style={{ width: `${Math.min(item.weight, 100)}%` }} />
                    </div>
                    <span className="text-xs text-gray-500">{item.weight.toFixed(1)}%</span>
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
  { key: '1d',  label: '1J'   },
  { key: '1w',  label: '1S'   },
  { key: '1mo', label: '1M'   },
  { key: '1y',  label: '1A'   },
  { key: 'all', label: 'Tout' },
]
const COMP_COLORS = ['#C9A84C', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16']

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
      <text x={0} y={0} dy={14} textAnchor="middle" fill="#6B7280" fontSize={11}>{line1}</text>
      {line2 && <text x={0} y={0} dy={26} textAnchor="middle" fill="#6B7280" fontSize={10}>{line2}</text>}
    </g>
  )
}

const normalize = (data) => {
  if (!data?.length) return []
  const first = data[0].value
  if (!first) return []
  return data.map(d => ({ date: d.date, pct: ((d.value / first) - 1) * 100 }))
}

const normalizeFromDate = (data, startDate) => {
  if (!data?.length) return []
  const entry = data.find(d => d.date >= startDate) || data[0]
  if (!entry?.value) return normalize(data)
  const base = entry.value
  return data.map(d => ({ date: d.date, pct: ((d.value / base) - 1) * 100 }))
}

export const PortfolioChart = () => {
  const [period, setPeriod]               = useState('1mo')
  const [portfolioRaw, setPortfolioRaw]   = useState([])
  const [orderDates, setOrderDates]       = useState([])
  const [totalInvested, setTotalInvested] = useState(null)
  const [loading, setLoading]             = useState(true)
  const [comparisons, setComparisons]     = useState([])
  const [query, setQuery]                 = useState('')
  const [results, setResults]             = useState([])
  const [searching, setSearching]         = useState(false)
  const [showDrop, setShowDrop]           = useState(false)

  const hasComp = comparisons.length > 0
  const comparisonsRef = useRef(comparisons)
  useEffect(() => { comparisonsRef.current = comparisons }, [comparisons])

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

  useEffect(() => {
    if (!comparisonsRef.current.length) return
    setComparisons(prev => prev.map(c => ({ ...c, loading: true })))
    comparisonsRef.current.forEach(c => fetchComp(c.symbol))
  }, [period])

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

  const chartData = useMemo(() => {
    if (!portfolioRaw.length) return []
    if (!hasComp) return portfolioRaw
    const portNorm = portfolioRaw.map(d => ({
      date: d.date,
      pct: d.twr !== undefined ? d.twr - 100 : ((d.value / portfolioRaw[0].value) - 1) * 100
    }))
    const isIntraday = portNorm.some(d => d.date?.includes('T'))
    const portfolioStartDateKey = (portNorm[0]?.date ?? '').split('T')[0]
    const compMaps = comparisons
      .filter(c => c.visible && c.data.length > 0)
      .map(c => {
        const norm = isIntraday ? normalize(c.data) : normalizeFromDate(c.data, portfolioStartDateKey)
        return { symbol: c.symbol, map: new Map(norm.map(d => [d.date.split('T')[0], d.pct])) }
      })
    const seenDates = new Set()
    return portNorm.map(d => {
      const dk = d.date.split('T')[0]
      const isFirst = !seenDates.has(dk)
      if (isFirst) seenDates.add(dk)
      return {
        date: d.date,
        portfolio: d.pct,
        ...Object.fromEntries(compMaps.map(cm => [cm.symbol, isFirst ? cm.map.get(dk) ?? null : null]))
      }
    })
  }, [portfolioRaw, comparisons, hasComp])

  const rawFirst  = portfolioRaw[0]?.value
  const rawLast   = portfolioRaw[portfolioRaw.length - 1]?.value
  const twrLast   = portfolioRaw[portfolioRaw.length - 1]?.twr
  const twrPct    = twrLast !== undefined ? twrLast - 100 : null
  const soloPct   = period === 'all' && totalInvested && rawLast
    ? ((rawLast - totalInvested) / totalInvested) * 100
    : twrPct
  const isPos     = hasComp ? (twrPct === null || twrPct >= 0) : (soloPct === null || soloPct >= 0)
  const portColor = isPos ? '#10b981' : '#ef4444'
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
      <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded-lg px-4 py-3 text-sm min-w-[160px]">
        <p className="text-gray-500 text-xs mb-2">{dl}</p>
        {payload.filter(p => p.value !== null).map((p, i) => {
          const isPort = p.dataKey === 'portfolio' || p.dataKey === 'value'
          const lbl = isPort ? 'Portefeuille' : p.dataKey
          const val = hasComp ? `${p.value >= 0 ? '+' : ''}${p.value?.toFixed(2)}%` : formatCurrency(p.value)
          return (
            <div key={i} className="flex items-center justify-between gap-4 mb-1">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: p.stroke }} />
                <span className="text-gray-400">{lbl}</span>
              </div>
              <span className="font-semibold text-white">{val}</span>
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          {!hasComp && rawLast && (
            <>
              <p className="text-3xl font-bold text-white">{formatCurrency(rawLast)}</p>
              {soloPct !== null && (
                <p className={`text-sm font-medium mt-1 ${isPos ? 'text-green-400' : 'text-red-400'}`}>
                  {isPos ? '+' : ''}{soloPct.toFixed(2)}%
                  <span className="text-gray-600 font-normal ml-1">
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
                <span className="text-gray-400 font-medium">Portefeuille</span>
                {twrPct !== null && (
                  <span className={`font-semibold ${isPos ? 'text-green-400' : 'text-red-400'}`}>
                    {isPos ? '+' : ''}{twrPct.toFixed(2)}%
                  </span>
                )}
                <span className="text-xs text-gray-600 bg-[#1A1A1A] px-1.5 py-0.5 rounded" title="Time-Weighted Return">TWR</span>
              </div>
              {comparisons.filter(c => c.visible && c.data.length > 0).map(c => {
                const isIntraday = portfolioRaw.some(d => d.date?.includes('T'))
                const startKey = (portfolioRaw[0]?.date ?? '').split('T')[0]
                const n = isIntraday ? normalize(c.data) : normalizeFromDate(c.data, startKey)
                const last = n[n.length - 1]?.pct
                return (
                  <div key={c.symbol} className="flex items-center gap-1.5 text-sm">
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: c.color }} />
                    <span className="text-gray-400 font-medium">{c.symbol}</span>
                    {last !== undefined && (
                      <span className={`font-semibold ${last >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {last >= 0 ? '+' : ''}{last.toFixed(2)}%
                      </span>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Period selector */}
        <div className="flex gap-1 bg-[#1A1A1A] p-1 rounded-lg flex-shrink-0">
          {PERIODS.map(p => (
            <button key={p.key} onClick={() => setPeriod(p.key)}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                period === p.key
                  ? 'bg-[#C9A84C] text-black'
                  : 'text-gray-500 hover:text-gray-300'
              }`}>
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-[#C9A84C] border-t-transparent" />
        </div>
      ) : chartData.length < 2 ? (
        <div className="flex items-center justify-center h-64 text-gray-600 text-sm">Pas assez de données pour cette période.</div>
      ) : (
        <ResponsiveContainer width="100%" height={320}>
          <AreaChart data={chartData} margin={{ top: 4, right: 4, left: 0, bottom: 8 }}>
            <defs>
              <linearGradient id="gPort" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor={portColor} stopOpacity={hasComp ? 0.04 : 0.15} />
                <stop offset="95%" stopColor={portColor} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
            <XAxis dataKey="date"
              tick={<MultiLineTick period={period} />}
              tickLine={false} axisLine={false}
              interval={xAxisInterval} minTickGap={60}
              height={period === '1w' || period === '1mo' ? 42 : 24} />
            <YAxis tickFormatter={formatY} tick={{ fontSize: 11, fill: '#6B7280' }}
              tickLine={false} axisLine={false} width={56} domain={['auto', 'auto']} />
            <Tooltip content={<TooltipContent />} />
            {!hasComp && orderDates.map(d => (
              <ReferenceLine key={d} x={d} stroke="#C9A84C" strokeWidth={1} strokeDasharray="4 3" strokeOpacity={0.5} />
            ))}
            <Area type="monotone" dataKey={hasComp ? 'portfolio' : 'value'}
              stroke={portColor} strokeWidth={2} fill="url(#gPort)"
              dot={false} activeDot={{ r: 4, fill: portColor, strokeWidth: 0 }} />
            {comparisons.filter(c => c.visible && c.data.length > 0).map(c => (
              <Area key={c.symbol} type="monotone" dataKey={c.symbol}
                stroke={c.color} strokeWidth={2} fill="none"
                dot={false} activeDot={{ r: 4, fill: c.color, strokeWidth: 0 }}
                connectNulls={true} />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      )}

      {/* Comparison panel */}
      <div className="mt-6 pt-5 border-t border-[#1A1A1A]">
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">Comparer avec</p>
        <div className="relative">
          <input type="text" value={query}
            onChange={e => setQuery(e.target.value)}
            onBlur={() => setTimeout(() => setShowDrop(false), 150)}
            onFocus={() => results.length > 0 && setShowDrop(true)}
            placeholder="Rechercher un actif (AAPL, S&P 500, Bitcoin…)"
            className="w-full px-4 py-2 pr-10 bg-[#1A1A1A] border border-[#2A2A2A] rounded-lg text-sm text-white placeholder-gray-600 focus:outline-none focus:border-[#C9A84C] transition" />
          <div className="absolute right-3 top-2.5 text-gray-600">
            {searching
              ? <div className="animate-spin rounded-full h-4 w-4 border-2 border-[#C9A84C] border-t-transparent" />
              : <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
                </svg>
            }
          </div>
          {showDrop && results.length > 0 && (
            <div className="absolute w-full bg-[#1A1A1A] border border-[#2A2A2A] rounded-lg mt-1 z-10 max-h-48 overflow-y-auto">
              {results.map((a, i) => (
                <button key={i} onMouseDown={() => addComp(a)}
                  disabled={comparisons.some(c => c.symbol === a.symbol) || comparisons.length >= 5}
                  className="w-full px-4 py-2.5 text-left hover:bg-[#222] border-b border-[#2A2A2A] last:border-0 flex justify-between items-center disabled:opacity-40">
                  <div>
                    <p className="font-medium text-sm text-white">{a.display_symbol}</p>
                    <p className="text-xs text-gray-500 truncate">{a.name}</p>
                  </div>
                  <span className="text-xs text-gray-600 bg-[#111] px-2 py-0.5 rounded ml-2 flex-shrink-0">{a.type}</span>
                </button>
              ))}
            </div>
          )}
        </div>
        {comparisons.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {comparisons.map(c => (
              <div key={c.symbol}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm transition-all ${
                  c.visible ? 'border-[#2A2A2A] bg-[#1A1A1A]' : 'border-[#1A1A1A] bg-[#0D0D0D] opacity-50'
                }`}>
                <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: c.color }} />
                <span className="font-medium text-gray-300 text-xs">{c.symbol}</span>
                {c.loading && <div className="animate-spin rounded-full h-3 w-3 border-2 border-[#C9A84C] border-t-transparent" />}
                <button onClick={() => setComparisons(prev => prev.map(x => x.symbol === c.symbol ? { ...x, visible: !x.visible } : x))}
                  className="text-gray-600 hover:text-gray-300 transition">
                  {c.visible
                    ? <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20"><path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/><path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd"/></svg>
                    : <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clipRule="evenodd"/><path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.064 7 9.542 7 .847 0 1.669-.105 2.454-.303z"/></svg>
                  }
                </button>
                <button onClick={() => setComparisons(prev => prev.filter(x => x.symbol !== c.symbol))}
                  className="text-gray-600 hover:text-red-500 transition">
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
        {comparisons.length >= 5 && (
          <p className="text-xs text-gray-600 mt-2">Maximum 5 comparaisons atteintes.</p>
        )}
      </div>
    </div>
  )
}

export const AssetsList = ({ assets, onDelete }) => {
  if (!assets || assets.length === 0) return null

  const TYPE_LABEL = { stock: 'Action', etf: 'ETF', crypto: 'Crypto', forex: 'Devise', bond: 'Obligation' }
  const TYPE_COLOR = {
    etf:    'bg-blue-900/30 text-blue-400 border border-blue-800/30',
    crypto: 'bg-orange-900/30 text-orange-400 border border-orange-800/30',
    stock:  'bg-[#1A1A1A] text-gray-400 border border-[#2A2A2A]',
  }

  const handleDelete = (symbol) => {
    if (window.confirm(`Supprimer ${symbol} et toutes ses positions associées ?`)) onDelete(symbol)
  }

  return (
    <div>
      <div className="px-6 py-4 border-b border-[#2A2A2A] flex items-center justify-between">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Actifs suivis ({assets.length})</h3>
        <p className="text-xs text-gray-600">Supprimer un actif efface toutes ses positions.</p>
      </div>
      <div className="divide-y divide-[#1A1A1A]">
        {assets.map(asset => (
          <div key={asset.symbol} className="flex items-center justify-between px-6 py-3 hover:bg-[#1A1A1A] transition">
            <div className="flex items-center gap-3">
              <span className={`text-xs px-2 py-0.5 rounded font-medium ${TYPE_COLOR[asset.asset_type] ?? TYPE_COLOR.stock}`}>
                {TYPE_LABEL[asset.asset_type] ?? asset.asset_type}
              </span>
              <div>
                <span className="font-semibold text-white text-sm">{asset.symbol}</span>
                <span className="text-xs text-gray-600 ml-2">{asset.name}</span>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium text-[#C9A84C]">{formatCurrency(asset.current_price)}</span>
              <button onClick={() => handleDelete(asset.symbol)}
                className="text-gray-600 hover:text-red-500 transition"
                title={`Supprimer ${asset.symbol}`}>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
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
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
      <div className="bg-[#111111] border border-green-900/30 rounded-lg p-5 border-l-2 border-l-green-500">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-4">Meilleur performer</h3>
        {topGainer ? (
          <div>
            <p className="text-xl font-bold text-white">{topGainer.symbol}</p>
            <p className="text-xs text-gray-600 mb-2">{topGainer.name}</p>
            <p className="text-green-400 font-semibold">{formatPercent(topGainer.gain_loss_percent)}</p>
            <p className="text-green-400 text-sm">{formatCurrency(topGainer.gain_loss)}</p>
          </div>
        ) : <p className="text-gray-600 text-sm">Pas de données</p>}
      </div>
      <div className="bg-[#111111] border border-red-900/30 rounded-lg p-5 border-l-2 border-l-red-500">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-4">Moins bon performer</h3>
        {topLoser ? (
          <div>
            <p className="text-xl font-bold text-white">{topLoser.symbol}</p>
            <p className="text-xs text-gray-600 mb-2">{topLoser.name}</p>
            <p className="text-red-400 font-semibold">{formatPercent(topLoser.gain_loss_percent)}</p>
            <p className="text-red-400 text-sm">{formatCurrency(topLoser.gain_loss)}</p>
          </div>
        ) : <p className="text-gray-600 text-sm">Pas de données</p>}
      </div>
    </div>
  )
}
