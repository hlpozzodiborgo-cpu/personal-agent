'use client'

import React, { useEffect, useState } from 'react'
import { getPortfolio, getAssets, checkHealth, removeHolding } from '@/lib/api'
import { PortfolioSummary, HoldingsList, TopPerformers } from '@/components/PortfolioComponents'
import { AddAssetModal, AddHoldingModal } from '@/components/Modals'

export default function Home() {
  const [portfolio, setPortfolio] = useState(null)
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [apiHealth, setApiHealth] = useState(null)
  const [deleting, setDeleting] = useState(false)
  
  // Modals
  const [showAddAsset, setShowAddAsset] = useState(false)
  const [showAddHolding, setShowAddHolding] = useState(false)

  // Charge les données
  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 60000) // Actualise toutes les minutes
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      setError('')
      
      // Vérifier la santé de l'API
      try {
        await checkHealth()
        setApiHealth('ok')
      } catch (err) {
        setApiHealth('error')
        setError('❌ Impossible de se connecter à l\'API. Vérifiez que le backend est en cours d\'exécution.')
        return
      }

      // Charger le portfolio et les actifs
      const [portfolioRes, assetsRes] = await Promise.all([
        getPortfolio(),
        getAssets()
      ])

      setPortfolio(portfolioRes.data)
      setAssets(assetsRes.data)
    } catch (err) {
      console.error('Erreur:', err)
      setError(`Erreur lors du chargement des données: ${err.message}`)
      setApiHealth('error')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteHolding = async (holdingId) => {
    try {
      setDeleting(true)
      await removeHolding(holdingId)
      // Rafraîchir les données
      await loadData()
    } catch (err) {
      setError(`Erreur lors de la suppression: ${err.message}`)
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">💰 Investor AI</h1>
              <p className="text-gray-600 text-sm mt-1">Votre analyste financier personnel</p>
            </div>
            <div className="flex items-center gap-3">
              {apiHealth === 'ok' && (
                <div className="flex items-center gap-2 px-3 py-2 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                  API Connectée
                </div>
              )}
              {apiHealth === 'error' && (
                <div className="flex items-center gap-2 px-3 py-2 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                  <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                  Déconnectée
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Action Buttons */}
        <div className="mb-8 flex gap-3">
          <button
            onClick={() => setShowAddAsset(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 font-medium flex items-center gap-2"
          >
            ➕ Ajouter des Actifs
          </button>
          <button
            onClick={() => setShowAddHolding(true)}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 font-medium flex items-center gap-2"
            disabled={assets.length === 0}
          >
            📊 Ajouter une Position
          </button>
          <button
            onClick={loadData}
            className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 font-medium flex items-center gap-2"
          >
            🔄 Actualiser
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Chargement des données...</p>
          </div>
        )}

        {/* Content */}
        {!loading && portfolio && (
          <>
            <PortfolioSummary portfolio={portfolio} />
            
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Mes Positions</h2>
              <HoldingsList 
                holdings={portfolio.holdings} 
                onDelete={handleDeleteHolding}
              />
            </div>

            <TopPerformers 
              topGainer={portfolio.top_gainer}
              topLoser={portfolio.top_loser}
            />
          </>
        )}

        {!loading && !portfolio && (
          <div className="bg-white rounded-lg p-12 shadow text-center">
            <p className="text-gray-500 text-lg">
              Aucun portefeuille encore. Commencez par ajouter des actifs et des positions!
            </p>
          </div>
        )}
      </main>

      {/* Modals */}
      <AddAssetModal 
        isOpen={showAddAsset}
        onClose={() => setShowAddAsset(false)}
        onSuccess={loadData}
      />

      <AddHoldingModal
        isOpen={showAddHolding}
        onClose={() => setShowAddHolding(false)}
        onSuccess={loadData}
        availableAssets={assets}
      />

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12 py-6">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-600 text-sm">
          <p>💡 Phase 1 en place: Dashboard de suivi. Phase 2: Actualités & Recommandations IA à venir</p>
        </div>
      </footer>
    </div>
  )
}
