/**
 * Composant NewsRecommendations
 * Phase 2: Actualités & Recommandations avec interface compacte
 */
'use client';

import { useEffect, useState } from 'react';

export default function NewsRecommendations({ symbols = [] }) {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState({ buy: 0, sell: 0, hold: 0, monitor: 0 });
  const [selectedCategory, setSelectedCategory] = useState(null); // 'buy', 'sell', 'hold', 'monitor'
  const [selectedRec, setSelectedRec] = useState(null); // Recommandation détaillée
  const [email, setEmail] = useState('');
  const [emailMessage, setEmailMessage] = useState('');
  const [sendingEmail, setSendingEmail] = useState(false);

  useEffect(() => {
    if (symbols.length === 0) return;
    fetchRecommendations();
  }, [symbols]);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const symbolsParam = symbols.join(',');
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      const response = await fetch(
        `${apiUrl}/api/news/recommendations?symbols=${symbolsParam}&hours=24`
      );
      
      if (!response.ok) {
        throw new Error(`Erreur: ${response.status}`);
      }
      
      const data = await response.json();
      setRecommendations(data.recommendations || []);
      setSummary(data.summary || {});
    } catch (err) {
      console.error('❌ Erreur récupération recommandations:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getRecommendationsByType = (type) => {
    return recommendations.filter(rec => {
      if (type === 'buy') return rec.recommendation_type.includes('BUY');
      if (type === 'sell') return rec.recommendation_type.includes('SELL');
      if (type === 'hold') return rec.recommendation_type.includes('HOLD');
      if (type === 'monitor') return rec.recommendation_type.includes('MONITOR');
      return false;
    });
  };

  const handleSendEmail = async () => {
    if (!email) {
      setEmailMessage('❌ Veuillez entrer votre email');
      return;
    }

    setSendingEmail(true);
    setEmailMessage('');

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/news/send-recommendations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email,
          include_all: false
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        setEmailMessage(`✅ Recommandations envoyées à ${email}`);
        setEmail('');
        setTimeout(() => setEmailMessage(''), 5000);
      } else {
        setEmailMessage(`❌ Erreur: ${data.detail || 'Impossible d\'envoyer les recommandations'}`);
      }
    } catch (err) {
      console.error('Erreur envoi email:', err);
      setEmailMessage('❌ Erreur réseau - vérifiez la configuration email');
    } finally {
      setSendingEmail(false);
    }
  };

  if (symbols.length === 0) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
        <p className="text-blue-700">📰 Aucun actif dans le portefeuille - impossible d'afficher les actualités</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">📰 Actualités & Recommandations</h2>
        <button
          onClick={fetchRecommendations}
          disabled={loading}
          className="px-3 py-1 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? '⏳' : '🔄'} Actualiser
        </button>
      </div>

      {/* Email Configuration */}
      <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg p-4 text-white">
        <div className="flex gap-2 items-center">
          <input
            type="email"
            placeholder="votre@email.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="flex-1 px-3 py-2 rounded text-gray-900 text-sm"
          />
          <button
            onClick={handleSendEmail}
            disabled={sendingEmail || loading}
            className="px-4 py-2 bg-white text-purple-600 rounded font-medium hover:bg-gray-100 disabled:opacity-50 text-sm"
          >
            📧 Envoyer
          </button>
        </div>
        {emailMessage && (
          <p className="text-sm mt-2 {emailMessage.includes('✅') ? 'text-green-100' : 'text-red-100'}">
            {emailMessage}
          </p>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-red-700 text-sm">❌ Erreur: {error}</p>
        </div>
      )}

      {/* Summary Cards - Clickable */}
      <div className="grid grid-cols-4 gap-3">
        <button
          onClick={() => setSelectedCategory(selectedCategory === 'buy' ? null : 'buy')}
          className={`rounded-lg p-3 text-center transition cursor-pointer ${
            selectedCategory === 'buy'
              ? 'bg-green-200 border-2 border-green-600 scale-105'
              : 'bg-green-50 border border-green-200 hover:bg-green-100'
          }`}
        >
          <p className="text-green-600 text-2xl font-bold">{summary.buy || 0}</p>
          <p className="text-green-700 text-xs font-semibold">À acheter</p>
        </button>

        <button
          onClick={() => setSelectedCategory(selectedCategory === 'sell' ? null : 'sell')}
          className={`rounded-lg p-3 text-center transition cursor-pointer ${
            selectedCategory === 'sell'
              ? 'bg-red-200 border-2 border-red-600 scale-105'
              : 'bg-red-50 border border-red-200 hover:bg-red-100'
          }`}
        >
          <p className="text-red-600 text-2xl font-bold">{summary.sell || 0}</p>
          <p className="text-red-700 text-xs font-semibold">À vendre</p>
        </button>

        <button
          onClick={() => setSelectedCategory(selectedCategory === 'hold' ? null : 'hold')}
          className={`rounded-lg p-3 text-center transition cursor-pointer ${
            selectedCategory === 'hold'
              ? 'bg-gray-300 border-2 border-gray-600 scale-105'
              : 'bg-gray-50 border border-gray-200 hover:bg-gray-100'
          }`}
        >
          <p className="text-gray-600 text-2xl font-bold">{summary.hold || 0}</p>
          <p className="text-gray-700 text-xs font-semibold">À tenir</p>
        </button>

        <button
          onClick={() => setSelectedCategory(selectedCategory === 'monitor' ? null : 'monitor')}
          className={`rounded-lg p-3 text-center transition cursor-pointer ${
            selectedCategory === 'monitor'
              ? 'bg-yellow-200 border-2 border-yellow-600 scale-105'
              : 'bg-yellow-50 border border-yellow-200 hover:bg-yellow-100'
          }`}
        >
          <p className="text-yellow-600 text-2xl font-bold">{summary.monitor || 0}</p>
          <p className="text-yellow-700 text-xs font-semibold">À surveiller</p>
        </button>
      </div>

      {/* Category View - Modale */}
      {selectedCategory && !selectedRec && (
        <div className="bg-white border border-gray-300 rounded-lg p-4 max-h-64 overflow-y-auto">
          <h3 className="font-bold text-gray-900 mb-3">
            {selectedCategory === 'buy' && '🟢 À acheter'}
            {selectedCategory === 'sell' && '🔴 À vendre'}
            {selectedCategory === 'hold' && '⚪ À tenir'}
            {selectedCategory === 'monitor' && '🟡 À surveiller'}
          </h3>
          
          {loading && <p className="text-gray-500 text-sm">⏳ Chargement...</p>}
          
          {!loading && getRecommendationsByType(selectedCategory).length === 0 && (
            <p className="text-gray-500 text-sm">Aucune recommandation dans cette catégorie</p>
          )}

          <div className="space-y-2">
            {getRecommendationsByType(selectedCategory).map((rec, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedRec(rec)}
                className="w-full text-left bg-gray-50 hover:bg-gray-100 p-2 rounded border border-gray-200 transition"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-semibold text-gray-900">{rec.symbol}</p>
                    <p className="text-xs text-gray-600">{rec.title.substring(0, 50)}...</p>
                  </div>
                  <span className="text-xs font-bold bg-gray-200 px-2 py-1 rounded">
                    {rec.confidence}%
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Detail View */}
      {selectedRec && (
        <div className="bg-white border border-gray-300 rounded-lg p-4">
          <button
            onClick={() => setSelectedRec(null)}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium mb-3"
          >
            ← Retour
          </button>
          
          <div>
            <div className="flex justify-between items-start mb-3">
              <div>
                <h3 className="text-xl font-bold text-gray-900">{selectedRec.symbol}</h3>
                <p className={`text-sm ${selectedRec.sentiment_score > 0.3 ? 'text-green-600' : selectedRec.sentiment_score < -0.3 ? 'text-red-600' : 'text-gray-600'}`}>
                  {selectedRec.sentiment_label}
                </p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold">{selectedRec.recommendation_type}</p>
                <p className="text-xs text-gray-500">Confiance: {selectedRec.confidence}%</p>
              </div>
            </div>

            <h4 className="font-semibold text-gray-900 mb-2">{selectedRec.title}</h4>
            
            {selectedRec.summary && (
              <p className="text-sm text-gray-700 mb-3">{selectedRec.summary}</p>
            )}

            <div className="flex justify-between items-center text-xs text-gray-500 mb-3 pb-3 border-b">
              <span>📰 {selectedRec.source}</span>
              <span>⏰ {new Date(selectedRec.published_at).toLocaleDateString('fr-FR')}</span>
            </div>

            <a
              href={selectedRec.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block text-blue-600 hover:text-blue-800 font-medium text-sm"
            >
              Lire l'article complet →
            </a>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && !selectedCategory && recommendations.length === 0 && !error && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <p className="text-blue-700 text-sm">✨ Aucune actualité récente - cliquez sur Actualiser</p>
        </div>
      )}
    </div>
  );
}
