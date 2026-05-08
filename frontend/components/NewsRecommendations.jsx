'use client'

import React, { useState } from 'react'
import { analyzePortfolioNews, getNewsStatus } from '@/lib/api'

const SIGNAL_STYLE = {
  RENFORCER: { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-200', dot: 'bg-green-500' },
  ALLEGER:   { bg: 'bg-red-100',   text: 'text-red-800',   border: 'border-red-200',   dot: 'bg-red-500'   },
  SURVEILLER:{ bg: 'bg-amber-100', text: 'text-amber-800', border: 'border-amber-200', dot: 'bg-amber-500'  },
  CONSERVER: { bg: 'bg-gray-100',  text: 'text-gray-700',  border: 'border-gray-200',  dot: 'bg-gray-400'  },
  AUCUN:     { bg: 'bg-gray-50',   text: 'text-gray-500',  border: 'border-gray-100',  dot: 'bg-gray-300'  },
}
const IMPACT_COLOR = { positif: 'text-green-600', negatif: 'text-red-600', neutre: 'text-gray-500' }

export default function NewsRecommendations() {
  const [result, setResult]     = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')
  const [days, setDays]         = useState(3)
  const [expanded, setExpanded] = useState(null)  // index de l'article ouvert

  const handleAnalyze = async () => {
    setLoading(true); setError(''); setResult(null); setExpanded(null)
    try {
      const res = await analyzePortfolioNews(days)
      if (res.data.error) {
        setError(res.data.error)
      } else {
        setResult(res.data)
      }
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  const articles = result?.articles ?? []
  const relevant = articles.filter(a => a.relevance !== 'faible')

  return (
    <div className="bg-white rounded-b-lg shadow p-6 space-y-6">

      {/* En-tête + contrôles */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Actualités & Recommandations IA</h2>
          <p className="text-sm text-gray-500 mt-0.5">
            Claude analyse les actualités récentes en tenant compte de votre portefeuille.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select value={days} onChange={e => setDays(Number(e.target.value))}
            className="px-3 py-1.5 border border-gray-200 rounded-lg text-sm text-gray-700">
            <option value={1}>24 heures</option>
            <option value={3}>3 jours</option>
            <option value={7}>7 jours</option>
          </select>
          <button onClick={handleAnalyze} disabled={loading}
            className="px-4 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm font-medium flex items-center gap-2">
            {loading
              ? <><div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" /> Analyse en cours…</>
              : '✨ Analyser'}
          </button>
        </div>
      </div>

      {/* Erreur */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          <strong>Erreur :</strong> {error}
          {(error.includes('Anthropic') || error.includes('NewsAPI')) && (
            <span className="ml-1">— Configurez les clés dans <strong>Paramètres ⚙️</strong>.</span>
          )}
        </div>
      )}

      {/* État initial */}
      {!result && !loading && !error && (
        <div className="py-16 text-center text-gray-400">
          <p className="text-4xl mb-3">📰</p>
          <p className="font-medium">Cliquez sur <strong>Analyser</strong> pour lancer l'analyse IA.</p>
          <p className="text-sm mt-1">
            Claude va récupérer les actualités des derniers {days} jours et les analyser<br />
            en tenant compte de vos positions (ETF, secteurs, exposition géographique…).
          </p>
        </div>
      )}

      {/* Résultats */}
      {result && (
        <div className="space-y-5">

          {/* Résumé marché */}
          {result.market_summary && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-xs font-semibold text-blue-600 uppercase tracking-wide mb-1">
                Résumé du marché — Claude {result.model ? `(${result.model})` : ''}
              </p>
              <p className="text-sm text-blue-900">{result.market_summary}</p>
            </div>
          )}

          {/* Méta */}
          <p className="text-xs text-gray-400">
            {result.articles_fetched ?? 0} articles analysés · {relevant.length} pertinents pour votre portefeuille
          </p>

          {/* Articles pertinents */}
          {relevant.length === 0 && (
            <p className="text-sm text-gray-500 py-4 text-center">
              Aucune actualité directement pertinente trouvée sur cette période.
            </p>
          )}

          <div className="space-y-3">
            {relevant.map((a, i) => {
              const style = SIGNAL_STYLE[a.signal] ?? SIGNAL_STYLE.AUCUN
              const isOpen = expanded === i
              return (
                <div key={i}
                  className={`border rounded-lg overflow-hidden ${style.border} cursor-pointer hover:shadow-sm transition`}
                  onClick={() => setExpanded(isOpen ? null : i)}>
                  {/* Ligne principale */}
                  <div className={`flex items-start gap-3 p-4 ${style.bg}`}>
                    <span className={`mt-1.5 w-2.5 h-2.5 rounded-full flex-shrink-0 ${style.dot}`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <span className={`text-xs font-bold px-2 py-0.5 rounded ${style.bg} ${style.text}`}>
                          {a.signal}
                        </span>
                        {a.affected_symbols?.length > 0 && a.affected_symbols.map(s => (
                          <span key={s} className="text-xs font-medium text-gray-600 bg-white px-2 py-0.5 rounded border border-gray-200">{s}</span>
                        ))}
                        <span className={`text-xs ml-auto ${IMPACT_COLOR[a.impact] ?? 'text-gray-500'}`}>
                          {a.impact} · {a.confidence}% confiance
                        </span>
                      </div>
                      <p className="text-sm font-medium text-gray-900 truncate">{a.title}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{a.source} · {a.date}</p>
                    </div>
                    <span className="text-gray-400 text-xs mt-1">{isOpen ? '▲' : '▼'}</span>
                  </div>

                  {/* Détail déplié */}
                  {isOpen && (
                    <div className="px-4 pb-4 pt-2 bg-white border-t border-gray-100 space-y-2">
                      <p className="text-sm text-gray-800">{a.analysis}</p>
                      {a.url && (
                        <a href={a.url} target="_blank" rel="noreferrer"
                          className="text-xs text-blue-600 hover:underline" onClick={e => e.stopPropagation()}>
                          Lire l'article complet →
                        </a>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          {/* Articles peu pertinents (repliés) */}
          {articles.length > relevant.length && (
            <details className="text-xs text-gray-400">
              <summary className="cursor-pointer hover:text-gray-600">
                {articles.length - relevant.length} article(s) jugé(s) peu pertinents (cliquer pour voir)
              </summary>
              <div className="mt-2 space-y-1 pl-2">
                {articles.filter(a => a.relevance === 'faible').map((a, i) => (
                  <div key={i} className="truncate">— {a.title} ({a.source})</div>
                ))}
              </div>
            </details>
          )}
        </div>
      )}
    </div>
  )
}
