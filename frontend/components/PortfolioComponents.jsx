import React from 'react'
import { formatCurrency, formatPercent, getColorClass, getBackgroundColorClass } from '@/lib/utils'

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
            return (
              <tr key={idx} className="border-b hover:bg-gray-50">
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
                  <div className="flex items-center gap-3">
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
