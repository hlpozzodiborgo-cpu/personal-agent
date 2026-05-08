# Phase 2 - Actualités & Recommandations 📰

## Overview

La Phase 2 ajoute des capacités de recommandation basées sur les actualités financières avec:
- **Récupération d'actualités** via Finnhub News API
- **Analyse de sentiment** simple (Phase 2 level)
- **Recommandations automatiques** (BUY, SELL, HOLD, MONITOR)
- **Alertes email** pour les meilleures opportunités
- **Widget frontend** intégré au dashboard

## Architecture

### Backend (Nouveaux fichiers)

1. **`news_service.py`** - Récupération des actualités
   - `get_news_for_symbol()` - Actualités pour un symbole
   - `get_news_for_portfolio()` - Actualités pour le portefeuille
   - `filter_recent_news()` - Filtrer par date
   - `get_article_details()` - Formater les articles

2. **`recommendation_engine.py`** - Génération des recommandations
   - `SentimentAnalyzer` - Analyse de sentiment par mots-clés
   - `RecommendationEngine` - Génération et classement des recommandations
   - Scoring: Confiance 0-100%, Sentiment -1 à +1

3. **`email_service.py`** - Envoi des emails
   - `send_recommendation_email()` - Envoyer les recommandations
   - `test_email_config()` - Tester la configuration SMTP
   - HTML email avec résumé et détails des recommandations

4. **`schemas_news.py`** - Modèles Pydantic
   - `NewsArticle` - Article d'actualité
   - `Recommendation` - Recommandation unique
   - `RecommendationResponse` - Réponse avec résumé

5. **`routes_news.py`** - Endpoints API
   - `GET /api/news/recommendations` - Récupérer les recommandations
   - `POST /api/news/send-recommendations` - Envoyer par email
   - `POST /api/news/test-email` - Tester email

### Frontend (Nouveaux fichiers)

1. **`components/NewsRecommendations.jsx`**
   - Affichage des actualités et recommandations
   - Cartes avec sentiment, score, source
   - Filtre par type (BUY/SELL/HOLD/MONITOR)
   - Lien direct vers les articles
   - Section newsletter pour configuration email

## Configuration

### Prérequis

1. **Finnhub API Key** (déjà configurée en Phase 1)
   - Les actualités utilisent le même token que le prix des actions
   - Déjà présent dans `backend/.env`

2. **Email Configuration** (optionnel pour cette version)
   - Pour activer les alertes email, configurer dans `backend/.env`:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-app-password  # Pas le mot de passe Gmail !
   ```
   - Pour Gmail: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

### Installation des dépendances

Aucune dépendance supplémentaire requise! Tous les modules utilisent la stdlib Python:
- `requests` ✅ Déjà installé (via yfinance)
- `smtplib`, `email` ✅ Stdlib Python
- `logging` ✅ Stdlib Python

## Utilisation

### API Endpoints

#### 1. Récupérer les recommandations
```bash
GET http://localhost:8000/api/news/recommendations?symbols=AAPL,MSFT,GOOGL&hours=24
```

Réponse:
```json
{
  "recommendations": [
    {
      "symbol": "AAPL",
      "title": "Apple Posts Record Earnings",
      "sentiment_score": 0.75,
      "sentiment_label": "Positif 📈",
      "recommendation_type": "BUY 🟢",
      "confidence": 75,
      "in_portfolio": true,
      "url": "..."
    }
  ],
  "count": 15,
  "summary": {
    "buy": 5,
    "sell": 2,
    "hold": 8,
    "monitor": 0
  }
}
```

#### 2. Envoyer les recommandations par email
```bash
POST http://localhost:8000/api/news/send-recommendations
Content-Type: application/json

{
  "email": "user@example.com",
  "include_all": false
}
```

#### 3. Tester la configuration email
```bash
POST http://localhost:8000/api/news/test-email?email=user@example.com
```

### Frontend

Le composant `NewsRecommendations` s'intègre automatiquement au dashboard:

```jsx
<NewsRecommendations symbols={["AAPL", "MSFT", "GOOGL"]} />
```

- 🟢 **À acheter** - Sentiment positif + actualités favorables
- 🔴 **À vendre** - Sentiment négatif + risques identifiés
- ⚪ **À tenir** - Sentiment neutre + maintien position
- 🟡 **À surveiller** - Peu d'actualités ou risques à surveiller

## Analyse de Sentiment

### Algorithme (Phase 2 - Simple)

1. **Mots-clés positifs** (80 mots)
   - growth, rise, beat, surge, partnership, innovation, etc.

2. **Mots-clés négatifs** (60 mots)
   - loss, fall, crash, lawsuit, scandal, bankruptcy, etc.

3. **Scoring**
   ```
   score = (positive_count - negative_count) / (positive_count + negative_count)
   score_final = (title_score * 0.6 + summary_score * 0.4)
   ```

4. **Confiance**
   - Basée sur la force du sentiment (0-100%)
   - Articles sans sentiment clair = 0%

### Limitations et Future Improvements

- ✅ Phase 2: Keyword-based (simple et rapide)
- 📋 Phase 3: ML-based sentiment (VADER, TextBlob, ou transformer models)
- 📋 Phase 4: NLP avancé avec context local des actualités

## Exemple d'Usage Complet

### 1. Backend démarre avec nouvelles routes
```bash
cd backend
python main.py
# ✅ Routes news & recommandations chargées
```

### 2. Frontend affiche les actualités
- Dashboard charge automatiquement les recommandations
- Actualise toutes les minutes
- Lien direct vers chaque article

### 3. Configuration email (optionnel)
```python
# Dans backend/.env:
SMTP_SERVER=smtp.gmail.com
SENDER_EMAIL=alerts@yourdomain.com
SENDER_PASSWORD=xxxx

# Puis via API:
POST /api/news/test-email?email=user@example.com
```

### 4. Alertes email
```python
# Récupérer les recommandations fortes (confiance > 60%)
# Envoyer email avec résumé et détails
```

## Monitoring & Debugging

### Logs

Tous les services log leurs actions:
```
📰 Récupération des actualités pour AAPL...
✅ 15 actualités trouvées pour AAPL
📊 Analyse des recommandations pour: ['AAPL', 'MSFT']
✅ 42 recommandations générées
📧 Email envoyé à user@example.com
```

### Endpoints de santé

```bash
# Vérifier la configuration Finnhub
GET /api/settings/test-finnhub

# Vérifier la configuration email
POST /api/news/test-email?email=test@example.com

# Health check global
GET /health
```

## Prochaines Étapes (Phase 3+)

1. **Persévérance des recommandations** 
   - Stocker dans la DB: `Recommendation` table
   - Historique complet des recommandations

2. **Recommandations personnalisées** 
   - ML-based scoring
   - Préférences utilisateur
   - Backtesting

3. **Intégration IA avancée**
   - Anthropic Claude API pour analyse nuancée
   - Recommandations d'actions automatiques

4. **Portfolio optimization**
   - Rebalancing suggestions
   - Risk assessment
   - Diversification analysis

## Fichiers créés

```
backend/
  news_service.py           ✅ Récupération des actualités
  recommendation_engine.py  ✅ Analyse et scoring
  email_service.py          ✅ Envoi des emails
  schemas_news.py           ✅ Modèles Pydantic
  routes_news.py            ✅ Endpoints API
  main.py                   ✏️ Import du routeur

frontend/
  components/
    NewsRecommendations.jsx ✅ Composant React
  app/
    page.jsx                ✏️ Intégration du composant
```

## Tests

### Test manuel - curl
```bash
# 1. Vérifier la santé de l'API
curl http://localhost:8000/health

# 2. Récupérer les recommandations
curl "http://localhost:8000/api/news/recommendations?symbols=AAPL,MSFT&hours=24"

# 3. Tester l'email
curl -X POST "http://localhost:8000/api/news/test-email?email=test@example.com"
```

### Test dans le frontend
1. Ajouter des positions au portefeuille
2. Actualiser le dashboard
3. Section "Actualités & Recommandations" doit s'afficher
4. Les actualités chargent automatiquement

## Support & Troubleshooting

### Pas d'actualités affichées
- ✅ Vérifier que `FINNHUB_API_KEY` est configuré
- ✅ Vérifier les logs: `[FINNHUB]` tags
- ✅ Vérifier le rate limit Finnhub (429 errors)

### Erreurs d'email
- ✅ Configurer les variables d'environnement SMTP
- ✅ Pour Gmail, utiliser "App Password" pas le vrai mot de passe
- ✅ Tester avec `/api/news/test-email`

### Performance
- Les appels API sont en cache (TODO: ajouter caching)
- Envisager rate limiting côté frontend si beaucoup de requêtes
- Déplacer les requêtes lourdes en background jobs (Phase 3)

---

**Phase 2 Status**: ✅ COMPLET - Actualités, recommandations & email configurés
**Next**: Phase 3 - Intégration IA Claude & optimisations
