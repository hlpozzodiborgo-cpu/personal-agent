'use client'

import React, { useState } from 'react'
import { analyzePortfolioNews } from '@/lib/api'

const SIGNAL_STYLE = {
  RENFORCER:  { border: 'border-green-800/40',  bg: 'bg-green-900/10',  dot: 'bg-green-500',  text: 'text-green-400',  badge: 'bg-green-900/30 text-green-400 border-green-800/40' },
  ALLEGER:    { border: 'border-red-800/40',    bg: 'bg-red-900/10',    dot: 'bg-red-500',    text: 'text-red-400',    badge: 'bg-red-900/30 text-red-400 border-red-800/40'       },
  SURVEILLER: { border: 'border-amber-800/40',  bg: 'bg-amber-900/10',  dot: 'bg-amber-500',  text: 'text-amber-400',  badge: 'bg-amber-900/30 text-amber-400 border-amber-800/40'  },
  CONSERVER:  { border: 'border-[#2A2A2A]',     bg: 'bg-[#1A1A1A]',    dot: 'bg-gray-500',   text: 'text-gray-400',   badge: 'bg-[#1A1A1A] text-gray-400 border-[#2A2A2A]'        },
  AUCUN:      { border: 'border-[#1A1A1A]',     bg: 'bg-[#111111]',    dot: 'bg-gray-700',   text: 'text-gray-600',   badge: 'bg-[#111111] text-gray-600 border-[#1A1A1A]'         },
}
const IMPACT_COLOR = { positif: 'text-green-400', negatif: 'text-red-400', neutre: 'text-gray-500' }

export default function NewsRecommendations() {
  const [result,   setResult]   = useState(null)
  const [loading,  setLoading]  = useState(false)
  const [error,    setError]    = useState('')
  const [days,     setDays]     = useState(3)
  const [expanded, setExpanded] = useState(null)

  const handleAnalyze = async () => {
    setLoading(true); setError(''); setResult(null); setExpanded(null)
    try {
      const res = await analyzePortfolioNews(days)
      if (res.data.error) setError(res.data.error)
      else setResult(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  const articles = result?.articles ?? []
  const relevant = articles.filter(a => a.relevance !== 'faible')

  return (
    <div className="p-6 space-y-6">

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-white">Analyse IA des actualités</h2>
          <p className="text-sm text-gray-500 mt-0.5">
            Analyse les actualités récentes en tenant compte de votre portefeuille.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={days}
            onChange={e => setDays(Number(e.target.value))}
            className="px-3 py-1.5 bg-[#1A1A1A] border border-[#2A2A2A] rounded-md text-sm text-gray-300 focus:outline-none focus:border-[#C9A84C] transition"
          >
            <option value={1}>24 heures</option>
            <option value={3}>3 jours</option>
            <option value={7}>7 jours</option>
          </select>
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="btn-gold px-4 py-1.5 rounded-md text-sm flex items-center gap-2"
          >
            {loading
              ? <><div className="animate-spin rounded-full h-4 w-4 border-2 border-black border-t-transparent" /> Analyse…</>
              : 'Analyser'
            }
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-900/20 border border-red-800/40 rounded-lg text-sm text-red-400">
          <strong>Erreur :</strong> {error}
          {(error.includes('Anthropic') || error.includes('NewsAPI') || error.includes('Gemini') || error.includes('Groq')) && (
            <span className="ml-1 text-red-500">— Configurez les clés dans <strong>Paramètres ⚙️</strong>.</span>
          )}
        </div>
      )}

      {/* Empty state */}
      {!result && !loading && !error && (
        <div className="py-20 text-center text-gray-600">
          <div className="w-10 h-10 border border-[#2A2A2A] rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
            </svg>
          </div>
          <p className="font-medium text-gray-500">Cliquez sur <strong className="text-gray-400">Analyser</strong> pour lancer l'analyse.</p>
          <p className="text-sm mt-1 text-gray-600">
            Le LLM va analyser les actualités des {days} derniers jours<br />
            en tenant compte de vos positions.
          </p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-5">

          {/* Market summary */}
          {result.market_summary && (
            <div className="p-4 bg-[#1A1A1A] border border-[#C9A84C]/20 rounded-lg">
              <p className="text-xs font-semibold text-[#C9A84C] uppercase tracking-wide mb-2">
                Résumé du marché {result.model ? `— ${result.model}` : ''}
              </p>
              <p className="text-sm text-gray-300 leading-relaxed">{result.market_summary}</p>
            </div>
          )}

          {/* Meta */}
          <p className="text-xs text-gray-600">
            {result.articles_fetched ?? 0} articles analysés · {relevant.length} pertinents pour votre portefeuille
          </p>

          {relevant.length === 0 && (
            <p className="text-sm text-gray-600 py-6 text-center">
              Aucune actualité directement pertinente trouvée sur cette période.
            </p>
          )}

          <div className="space-y-2">
            {relevant.map((a, i) => {
              const style = SIGNAL_STYLE[a.signal] ?? SIGNAL_STYLE.AUCUN
              const isOpen = expanded === i
              return (
                <div
                  key={i}
                  className={`border rounded-lg overflow-hidden cursor-pointer transition hover:border-[#333] ${style.border}`}
                  onClick={() => setExpanded(isOpen ? null : i)}
                >
                  <div className={`flex items-start gap-3 p-4 ${style.bg}`}>
                    <span className={`mt-1.5 w-2 h-2 rounded-full flex-shrink-0 ${style.dot}`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <span className={`text-xs font-bold px-2 py-0.5 rounded border ${style.badge}`}>
                          {a.signal}
                        </span>
                        {a.affected_symbols?.length > 0 && a.affected_symbols.map(s => (
                          <span key={s} className="text-xs font-medium text-gray-400 bg-[#111] px-2 py-0.5 rounded border border-[#2A2A2A]">{s}</span>
                        ))}
                        <span className={`text-xs ml-auto ${IMPACT_COLOR[a.impact] ?? 'text-gray-500'}`}>
                          {a.impact} · {a.confidence}%
                        </span>
                      </div>
                      <p className="text-sm font-medium text-white truncate">{a.title}</p>
                      <p className="text-xs text-gray-600 mt-0.5">{a.source} · {a.date}</p>
                    </div>
                    <span className={`text-gray-600 text-xs mt-1 flex-shrink-0 ${style.text}`}>{isOpen ? '▲' : '▼'}</span>
                  </div>

                  {isOpen && (
                    <div className="px-4 pb-4 pt-3 bg-[#0D0D0D] border-t border-[#1A1A1A] space-y-2">
                      <p className="text-sm text-gray-300 leading-relaxed">{a.analysis}</p>
                      {a.url && (
                        <a href={a.url} target="_blank" rel="noreferrer"
                          className="text-xs text-[#C9A84C] hover:underline" onClick={e => e.stopPropagation()}>
                          Lire l'article →
                        </a>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          {articles.length > relevant.length && (
            <details className="text-xs text-gray-600">
              <summary className="cursor-pointer hover:text-gray-400 transition">
                {articles.length - relevant.length} article(s) jugé(s) peu pertinents
              </summary>
              <div className="mt-2 space-y-1 pl-2">
                {articles.filter(a => a.relevance === 'faible').map((a, i) => (
                  <div key={i} className="truncate text-gray-700">— {a.title} ({a.source})</div>
                ))}
              </div>
            </details>
          )}
        </div>
      )}
    </div>
  )
}
