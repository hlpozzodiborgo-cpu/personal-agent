import React from 'react'
import { formatCurrency, formatPercent, getColorClass, getBackgroundColorClass } from '@/lib/utils'

export const PortfolioSummary = ({ portfolio }) => {
  if (!portfolio || !portfolio.stats) return <div>Aucune donnée</div>

  const stats = portfolio.stats
  const gainLoss = stats.total_gain_loss
  const gainLossPercent = stats.gain_loss_percent

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      {/* Total Investi */}
      <div className="bg-white rounded-lg p-6 shadow">
        <h3 className="text-gray-500 text-sm font-medium">Total Investi</h3>
        <p className="text-2xl font-bold mt-2">
          {formatCurrency(stats.total_invested)}
        </p>
      </div>

      {/* Valeur Actuelle */}
      <div className="bg-white rounded-lg p-6 shadow">
        <h3 className="text-gray-500 text-sm font-medium">Valeur Actuelle</h3>
        <p className="text-2xl font-bold mt-2">
          {formatCurrency(stats.total_current_value)}
        </p>
      </div>

      {/* Gain/Perte */}
      <div className={`rounded-lg p-6 shadow ${getBackgroundColorClass(gainLoss)}`}>
        <h3 className="text-gray-500 text-sm font-medium">Gain/Perte</h3>
        <p className={`text-2xl font-bold mt-2 ${getColorClass(gainLoss)}`}>
          {formatCurrency(gainLoss)}
        </p>
        <p className={`text-sm mt-1 ${getColorClass(gainLoss)}`}>
          {formatPercent(gainLossPercent)}
        </p>
      </div>

      {/* Nombre de positions */}
      <div className="bg-white rounded-lg p-6 shadow">
        <h3 className="text-gray-500 text-sm font-medium">Positions</h3>
        <p className="text-2xl font-bold mt-2">
          {stats.number_of_holdings}
        </p>
      </div>
    </div>
  )
}

export const HoldingsList = ({ holdings, onDelete }) => {
  if (!holdings || holdings.length === 0) {
    return (
      <div className="bg-white rounded-lg p-6 shadow text-center">
        <p className="text-gray-500">Aucune position dans le portefeuille</p>
      </div>
    )
  }

  const handleDelete = (holdingId, symbol) => {
    if (window.confirm(`⚠️ Êtes-vous sûr de vouloir supprimer la position ${symbol}?\n\nCette action ne peut pas être annulée.`)) {
      onDelete(holdingId)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <table className="w-full">
        <thead className="bg-gray-50 border-b">
          <tr>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Actif</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Quantité</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Prix d'Achat</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Prix Actuel</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Investi</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Valeur Actuelle</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Gain/Perte</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Actions</th>
          </tr>
        </thead>
        <tbody>
          {holdings.map((holding, idx) => {
            const gainLoss = holding.gain_loss
            return (
              <tr key={idx} className="border-b hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div>
                    <p className="font-semibold text-gray-900">{holding.symbol}</p>
                    <p className="text-sm text-gray-500">{holding.name}</p>
                  </div>
                </td>
                <td className="px-6 py-4 text-gray-700">{holding.quantity.toFixed(2)}</td>
                <td className="px-6 py-4 text-gray-700">{formatCurrency(holding.avg_price)}</td>
                <td className="px-6 py-4 text-gray-700">{formatCurrency(holding.current_price)}</td>
                <td className="px-6 py-4 text-gray-700">{formatCurrency(holding.invested)}</td>
                <td className="px-6 py-4 text-gray-700">{formatCurrency(holding.current_value)}</td>
                <td className={`px-6 py-4 font-semibold ${getColorClass(gainLoss)}`}>
                  <div>{formatCurrency(gainLoss)}</div>
                  <div className="text-sm">{formatPercent(holding.gain_loss_percent)}</div>
                </td>
                <td className="px-6 py-4">
                  <button
                    onClick={() => handleDelete(holding.id, holding.symbol)}
                    className="text-gray-400 hover:text-red-600 text-xl transition"
                    title="Supprimer cette position"
                  >
                    🗑️
                  </button>
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
      {/* Meilleur performer */}
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

      {/* Moins bon performer */}
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
