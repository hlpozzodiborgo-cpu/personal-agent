'use client'

import React, { useEffect, useState, useRef } from 'react'
import { getPortfolio, getAssets, checkHealth, removeHolding, deleteAsset } from '@/lib/api'
import { PortfolioSummary, HoldingsList, ConsolidatedView, PortfolioChart, TopPerformers, AssetsList } from '@/components/PortfolioComponents'
import { AddAssetModal, AddHoldingModal, EditHoldingModal, SettingsModal } from '@/components/Modals'
import NewsRecommendations from '@/components/NewsRecommendations'

const PAGES = [
  { id: 'portfolio',        label: 'Investissements personnels' },
  { id: 'recommendations',  label: 'Recommandations'            },
  { id: 'ai',               label: 'Investissements IA'         },
]

const PORTFOLIO_TABS = [
  { id: 'evolution',    label: 'Évolution'      },
  { id: 'consolidated', label: 'Par titre'      },
  { id: 'positions',    label: 'Ordres passés'  },
  { id: 'assets',       label: 'Actifs suivis'  },
]

export default function Home() {
  const [portfolio,      setPortfolio]      = useState(null)
  const [assets,         setAssets]         = useState([])
  const [loading,        setLoading]        = useState(true)
  const [error,          setError]          = useState('')
  const [apiHealth,      setApiHealth]      = useState(null)
  const [activePage,     setActivePage]     = useState('portfolio')
  const [portfolioTab,   setPortfolioTab]   = useState('evolution')

  const [showAddAsset,   setShowAddAsset]   = useState(false)
  const [showAddHolding, setShowAddHolding] = useState(false)
  const [showSettings,   setShowSettings]   = useState(false)
  const [editingHolding, setEditingHolding] = useState(null)

  const isFirstLoad = useRef(true)

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 60000)
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      if (isFirstLoad.current) setLoading(true)
      setError('')
      try {
        await checkHealth()
        setApiHealth('ok')
      } catch {
        setApiHealth('error')
        setError("Impossible de se connecter à l'API. Vérifiez que le backend est en cours d'exécution.")
        return
      }
      const [portfolioRes, assetsRes] = await Promise.all([getPortfolio(), getAssets()])
      setPortfolio(portfolioRes.data)
      setAssets(assetsRes.data)
      isFirstLoad.current = false
    } catch (err) {
      setError(`Erreur lors du chargement : ${err.message}`)
      setApiHealth('error')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteHolding = async (holdingId) => {
    try {
      await removeHolding(holdingId)
      await loadData()
    } catch (err) {
      setError(`Erreur lors de la suppression : ${err.message}`)
    }
  }

  const handleDeleteAsset = async (symbol) => {
    try {
      await deleteAsset(symbol)
      await loadData()
    } catch (err) {
      setError(`Erreur lors de la suppression de ${symbol} : ${err.message}`)
    }
  }

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white">

      {/* ── HEADER ────────────────────────────────────────────── */}
      <header className="bg-[#111111] border-b border-[#2A2A2A] sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">

            {/* Logo */}
            <div className="flex items-center gap-8 flex-shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-7 h-7 rounded-sm bg-[#C9A84C] flex items-center justify-center">
                  <svg className="w-4 h-4 text-black" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                    <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd"/>
                  </svg>
                </div>
                <span className="text-white font-bold text-lg tracking-widest uppercase">
                  Big Brother
                </span>
              </div>

              {/* Main nav */}
              <nav className="hidden md:flex items-center gap-1">
                {PAGES.map(page => (
                  <button
                    key={page.id}
                    onClick={() => setActivePage(page.id)}
                    className={`px-4 py-2 text-sm font-medium rounded-md transition-all duration-150 ${
                      activePage === page.id
                        ? 'bg-gold-muted text-[#C9A84C] border border-[#C9A84C]/30'
                        : 'text-gray-400 hover:text-white hover:bg-[#1A1A1A]'
                    }`}
                  >
                    {page.label}
                  </button>
                ))}
              </nav>
            </div>

            {/* Right side */}
            <div className="flex items-center gap-3">
              {apiHealth === 'ok' && (
                <div className="hidden sm:flex items-center gap-1.5 text-xs text-gray-500">
                  <span className="w-1.5 h-1.5 bg-[#C9A84C] rounded-full animate-pulse" />
                  Connecté
                </div>
              )}
              {apiHealth === 'error' && (
                <div className="hidden sm:flex items-center gap-1.5 text-xs text-red-400">
                  <span className="w-1.5 h-1.5 bg-red-500 rounded-full" />
                  Déconnecté
                </div>
              )}
              <button
                onClick={() => setShowSettings(true)}
                className="p-2 rounded-md text-gray-500 hover:text-[#C9A84C] hover:bg-[#1A1A1A] transition"
                title="Paramètres"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* ── MAIN ──────────────────────────────────────────────── */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {error && (
          <div className="mb-6 p-4 bg-red-900/20 border border-red-800/50 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* ── PAGE : INVESTISSEMENTS PERSONNELS ── */}
        {activePage === 'portfolio' && (
          <>
            {/* Action buttons */}
            <div className="mb-6 flex flex-wrap gap-3">
              <button
                onClick={() => setShowAddAsset(true)}
                className="btn-gold px-4 py-2 rounded-md text-sm flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4"/></svg>
                Ajouter un actif
              </button>
              <button
                onClick={() => setShowAddHolding(true)}
                disabled={assets.length === 0}
                className="btn-ghost px-4 py-2 rounded-md text-sm flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
                Ajouter une position
              </button>
              <button
                onClick={loadData}
                className="px-4 py-2 rounded-md text-sm text-gray-400 border border-[#2A2A2A] hover:border-[#333] hover:text-white transition flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                Actualiser
              </button>
            </div>

            {loading && !portfolio && (
              <div className="text-center py-24">
                <div className="animate-spin rounded-full h-10 w-10 border-2 border-[#C9A84C] border-t-transparent mx-auto" />
                <p className="text-gray-500 mt-4 text-sm">Chargement…</p>
              </div>
            )}

            {portfolio && (
              <>
                <PortfolioSummary portfolio={portfolio} />

                {/* Sub-tabs */}
                <div className="bg-[#111111] rounded-t-lg border border-[#2A2A2A] border-b-0 mt-6">
                  <nav className="flex px-2 pt-2 gap-1">
                    {PORTFOLIO_TABS.map(tab => (
                      <button
                        key={tab.id}
                        onClick={() => setPortfolioTab(tab.id)}
                        className={`px-4 py-2.5 text-sm font-medium rounded-t-md transition-all border-b-2 ${
                          portfolioTab === tab.id
                            ? 'border-[#C9A84C] text-[#C9A84C]'
                            : 'border-transparent text-gray-500 hover:text-gray-300'
                        }`}
                      >
                        {tab.label}
                      </button>
                    ))}
                  </nav>
                </div>

                {/* Tab content */}
                <div className="bg-[#111111] rounded-b-lg border border-[#2A2A2A] border-t-0 mb-8">
                  <div className={portfolioTab !== 'evolution'    ? 'hidden' : ''}><PortfolioChart /></div>
                  <div className={portfolioTab !== 'consolidated' ? 'hidden' : ''}><ConsolidatedView holdings={portfolio.holdings} /></div>
                  <div className={portfolioTab !== 'positions'    ? 'hidden' : ''}>
                    <HoldingsList holdings={portfolio.holdings} onDelete={handleDeleteHolding} onEdit={setEditingHolding} />
                  </div>
                  <div className={portfolioTab !== 'assets'       ? 'hidden' : ''}>
                    <AssetsList assets={assets} onDelete={handleDeleteAsset} />
                  </div>
                </div>

                <TopPerformers topGainer={portfolio.top_gainer} topLoser={portfolio.top_loser} />
              </>
            )}

            {!loading && !portfolio && (
              <div className="bg-[#111111] border border-[#2A2A2A] rounded-lg p-16 text-center">
                <p className="text-gray-500">Aucun portefeuille. Commencez par ajouter des actifs et des positions.</p>
              </div>
            )}
          </>
        )}

        {/* ── PAGE : RECOMMANDATIONS ── */}
        {activePage === 'recommendations' && (
          <div className="bg-[#111111] border border-[#2A2A2A] rounded-lg">
            <NewsRecommendations />
          </div>
        )}

        {/* ── PAGE : INVESTISSEMENTS IA ── */}
        {activePage === 'ai' && <AIPage />}

      </main>

      {/* ── FOOTER ────────────────────────────────────────────── */}
      <footer className="border-t border-[#1A1A1A] mt-12 py-6">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-600 text-xs tracking-widest uppercase">
          Big Brother — Investor AI
        </div>
      </footer>

      {/* ── MODALS ────────────────────────────────────────────── */}
      <AddAssetModal    isOpen={showAddAsset}    onClose={() => setShowAddAsset(false)}    onSuccess={loadData} />
      <AddHoldingModal  isOpen={showAddHolding}  onClose={() => setShowAddHolding(false)}  onSuccess={loadData} availableAssets={assets} />
      <EditHoldingModal isOpen={!!editingHolding} holding={editingHolding} onClose={() => setEditingHolding(null)} onSuccess={loadData} />
      <SettingsModal    isOpen={showSettings}    onClose={() => setShowSettings(false)} />
    </div>
  )
}


// ── Investissements IA placeholder ──────────────────────────────────────────
function AIPage() {
  const stages = [
    { id: 1, name: 'Ingest',         desc: 'GDELT + YFinance — collecte & déduplication',          status: 'planned' },
    { id: 2, name: 'Signals',        desc: 'Embeddings MiniLM, clustering, scoring multi-facteur', status: 'planned' },
    { id: 3, name: 'Analyse LLM',    desc: 'Fetch articles, appel LLM, extraction JSON structuré', status: 'planned' },
    { id: 4, name: 'Thèse',          desc: 'Génération de thèse d\'investissement par le LLM',     status: 'planned' },
    { id: 5, name: 'Quant',          desc: 'Vérification quantitative — momentum, volatilité',     status: 'planned' },
    { id: 6, name: 'Risque',         desc: 'Scoring de risque et sizing de position',              status: 'planned' },
    { id: 7, name: 'Recommandation', desc: 'Action finale : BUY / HOLD / WATCH + rationale',      status: 'planned' },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-[#111111] border border-[#2A2A2A] rounded-lg p-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-xl font-semibold text-white">Pipeline Big Brother</h2>
            <p className="text-gray-500 text-sm mt-1">
              Agent d'investissement automatisé — 7 stages de traitement en cours de développement
            </p>
          </div>
          <span className="px-3 py-1 text-xs font-medium bg-[#C9A84C]/10 text-[#C9A84C] border border-[#C9A84C]/20 rounded-full">
            En développement
          </span>
        </div>

        {/* Pipeline visual */}
        <div className="mt-6 flex items-center gap-2 overflow-x-auto pb-2">
          {stages.map((stage, i) => (
            <React.Fragment key={stage.id}>
              <div className="flex-shrink-0 flex flex-col items-center gap-2">
                <div className="w-10 h-10 rounded-full border-2 border-[#2A2A2A] bg-[#1A1A1A] flex items-center justify-center text-xs text-gray-600 font-mono">
                  {stage.id}
                </div>
                <span className="text-xs text-gray-600 whitespace-nowrap">{stage.name}</span>
              </div>
              {i < stages.length - 1 && (
                <div className="flex-shrink-0 w-6 h-px bg-[#2A2A2A] mt-[-12px]" />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Stage details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {stages.map(stage => (
          <div key={stage.id} className="bg-[#111111] border border-[#2A2A2A] rounded-lg p-4 flex items-start gap-4 hover:border-[#333] transition">
            <div className="w-8 h-8 rounded-md bg-[#1A1A1A] border border-[#2A2A2A] flex items-center justify-center text-xs text-[#C9A84C] font-mono font-bold flex-shrink-0">
              {stage.id}
            </div>
            <div>
              <p className="text-sm font-medium text-white">Stage {stage.id} — {stage.name}</p>
              <p className="text-xs text-gray-500 mt-0.5">{stage.desc}</p>
            </div>
          </div>
        ))}
      </div>

      {/* LLM providers */}
      <div className="bg-[#111111] border border-[#2A2A2A] rounded-lg p-6">
        <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-4">Fournisseurs LLM</h3>
        <div className="grid grid-cols-3 gap-4">
          {[
            { name: 'Gemini 2.5 Flash', role: 'Primaire',  color: 'text-[#C9A84C]' },
            { name: 'Groq Llama 3.3',   role: 'Backup',    color: 'text-gray-400'   },
            { name: 'Claude Haiku',      role: 'Fallback',  color: 'text-gray-600'   },
          ].map(p => (
            <div key={p.name} className="text-center">
              <p className={`text-sm font-medium ${p.color}`}>{p.name}</p>
              <p className="text-xs text-gray-600 mt-0.5">{p.role}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
