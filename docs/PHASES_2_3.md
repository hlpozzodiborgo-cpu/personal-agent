# 🔮 Feuille de Route - Phases 2 & 3

## Phase 2: Analyse des Actualités Financières (À venir)

### Objectifs
- Récupérer les actualités pertinentes pour vos actifs
- Évaluer l'impact des actualités sur votre portefeuille
- Afficher les actualités dans le dashboard avec contexte

### Architecture

```
Dashboard
├── News Feed (par actif)
├── Sentiment Analysis (bullish/bearish)
├── Impact Score (0-100)
└── Timeline historique
```

### Implémentation

**Fichiers à créer:**
```
backend/
├── news_service.py        # Service pour récupérer les actualités
├── sentiment_analysis.py  # Analyse du sentiment des actualités
└── models.py (ajouter)    # Modèle NewsArticle
```

**API Endpoints:**
```
GET /api/news/{symbol}           # Actualités pour un actif
GET /api/portfolio/news           # Toutes les actualités du portfolio
GET /api/news/sentiment/{symbol}  # Analyse sentiment
POST /api/news/alerts/setup       # Configuration des alertes
```

**Frontend:**
- Page `/news` avec feed d'actualités
- Widget d'actualités dans le dashboard principal
- Filtrage par actif, date, sentiment

### Dépendances à ajouter
```
newsapi                    # NewsAPI.org API
nltk                      # Natural Language Processing
textblob                  # Sentiment analysis
```

### Estimé: 2-3 jours de travail

---

## Phase 3: Agent IA avec Recommandations

### Objectifs
- Analyser automatiquement votre portefeuille
- Générer des recommandations d'achat/vente
- Chat IA interactif pour répondre à vos questions
- Analyse de risque et diversification

### Architecture

```
Agent IA (Claude)
├── Portfolio Analysis
│   ├── Risk Assessment
│   ├── Diversification Check
│   └── Performance Analysis
│
├── Recommendations Engine
│   ├── Buy Signals
│   ├── Sell Signals
│   └── Rebalancing Suggestions
│
└── Chat Interface
    ├── Natural Language Q&A
    ├── Strategy Discussions
    └── Educational Content
```

### Implémentation

**Fichiers à créer:**
```
backend/
├── llm_service.py         # Integration Claude API
├── analysis_service.py    # Analyse du portfolio
└── recommendations.py     # Moteur de recommandations
```

**API Endpoints:**
```
POST /api/recommendations      # Générer recommandations
POST /api/analysis            # Analyser le portfolio
POST /api/chat               # Chat IA
GET  /api/recommendations/status  # Status des recommandations
```

**Frontend:**
- Page `/recommendations` avec suggestions
- Widget de recommandations dans le dashboard
- `/chat` pour l'interface de chat
- Panel d'analyse détaillée

### Dépendances à ajouter
```
anthropic                  # Claude API
openai                     # Alternative: GPT-4
langchain                  # LLM Framework
```

### Flux d'une session de recommandations:

1. **Collecte des données:**
   - Positions actuelles
   - Prix et performance
   - Historique récent
   - Actualités pertinentes

2. **Analyse par l'IA:**
   - Risk score du portfolio
   - Diversification metrics
   - Opportunités identifiées
   - Secteurs sous/sur-pondérés

3. **Génération de recommandations:**
   - Actions spécifiques à acheter/vendre
   - Justification avec contexte
   - Confiance/Risque associé
   - Timeline suggérée

4. **Chat interactif:**
   - Poser des questions sur les recommandations
   - Discuter de stratégies
   - Éducation financière

### Exemple de recommandation:

```
{
  "id": "rec_001",
  "timestamp": "2026-05-04T10:30:00",
  "recommendation": "buy",
  "asset": "VGRO",
  "quantity": "50",
  "price_target": "32.50",
  "confidence": 0.75,
  "reason": "ETF diversifié avec bon rendement historique, profite de la baisse des taux",
  "risk_level": "medium",
  "horizon": "12 months",
  "alternative": "XGRO si vous préférez Canadian-based"
}
```

### Estimé: 3-4 jours de travail

---

## Étapes Détaillées pour Implémenter Phase 2

### Étape 1: Setuper NewsAPI

```bash
# 1. Créer un compte gratuit
# https://newsapi.org/register

# 2. Ajouter votre clé à .env
NEWSAPI_KEY=votre_clé_ici
```

### Étape 2: Créer le service d'actualités

```python
# backend/news_service.py

import requests
from datetime import datetime, timedelta
from config import NEWSAPI_KEY

class NewsService:
    BASE_URL = "https://newsapi.org/v2"
    
    @staticmethod
    def get_news(symbol, language="en"):
        """Récupère les actualités pour un symbole"""
        query = f"{symbol} stock OR bitcoin OR cryptocurrency"
        
        params = {
            "q": query,
            "sortBy": "publishedAt",
            "language": language,
            "apiKey": NEWSAPI_KEY
        }
        
        response = requests.get(f"{NewsService.BASE_URL}/everything", params=params)
        return response.json()
    
    @staticmethod
    def analyze_sentiment(title, description):
        """Analyse le sentiment d'une actualité"""
        from textblob import TextBlob
        
        text = f"{title} {description}"
        blob = TextBlob(text)
        
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            return "bullish"
        elif polarity < -0.1:
            return "bearish"
        else:
            return "neutral"
```

### Étape 3: Ajouter les endpoints

```python
# In main.py

@app.get("/api/news/{symbol}")
def get_asset_news(symbol: str):
    news = NewsService.get_news(symbol)
    
    articles = []
    for article in news.get("articles", [])[:10]:
        sentiment = NewsService.analyze_sentiment(
            article["title"],
            article["description"] or ""
        )
        
        articles.append({
            "title": article["title"],
            "description": article["description"],
            "url": article["url"],
            "source": article["source"]["name"],
            "published_at": article["publishedAt"],
            "sentiment": sentiment,
            "image": article.get("urlToImage")
        })
    
    return {"symbol": symbol, "articles": articles}
```

---

## Étapes Détaillées pour Implémenter Phase 3

### Étape 1: Setuper Claude API

```bash
# 1. Créer un compte Anthropic
# https://console.anthropic.com/

# 2. Obtenir une clé API (5$ gratuit)
# 3. Ajouter à .env
ANTHROPIC_API_KEY=sk-ant-...
```

### Étape 2: Créer le service LLM

```python
# backend/llm_service.py

from anthropic import Anthropic

client = Anthropic()

class InvestmentAdvisor:
    def __init__(self):
        self.conversation_history = []
    
    def analyze_portfolio(self, portfolio_data):
        """Analyse le portfolio et génère des recommandations"""
        
        prompt = f"""
        Analyse ce portfolio d'investissement et génère 3-5 recommandations:
        
        {portfolio_data}
        
        Inclus:
        1. Risques identifiés
        2. Opportunités de diversification
        3. Actions recommandées (achat/vente)
        4. Horizon d'investissement suggéré
        5. Alternatives à considérer
        """
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    
    def chat(self, user_message):
        """Chat interactif avec l'advisor"""
        
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system="Tu es un advisor financier expert. Fournis des conseils pratiques et éducatifs.",
            messages=self.conversation_history
        )
        
        assistant_message = response.content[0].text
        
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
```

### Étape 3: Ajouter les endpoints

```python
# In main.py

@app.post("/api/recommendations")
def get_recommendations(db: Session = Depends(get_db)):
    """Génère des recommandations pour le portfolio"""
    
    # Récupère les données du portfolio
    holdings = HoldingCRUD.get_all_active(db)
    portfolio_data = prepare_portfolio_data(holdings)
    
    # Génère les recommandations via Claude
    advisor = InvestmentAdvisor()
    recommendations = advisor.analyze_portfolio(portfolio_data)
    
    return {
        "recommendations": recommendations,
        "generated_at": datetime.utcnow().isoformat()
    }

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket pour chat temps réel"""
    await websocket.accept()
    advisor = InvestmentAdvisor()
    
    while True:
        data = await websocket.receive_text()
        response = advisor.chat(data)
        await websocket.send_text(response)
```

---

## Checklist de Déploiement

### Avant Production

- [ ] Tester avec 50+ actifs différents
- [ ] Vérifier les limites d'API (rate limits)
- [ ] Setup monitoring et alertes
- [ ] Tests de charge du backend
- [ ] Optimiser les requêtes DB
- [ ] Compresser/cachaner les réponses
- [ ] Implémenter la pagination

### Infrastructure

- [ ] Configurer auto-scaling (Render/Railway)
- [ ] Setup CDN pour le frontend (Vercel)
- [ ] Configurer les logs (Sentry ou DataDog)
- [ ] Backup automatique de la DB
- [ ] SSL/HTTPS partout

### Sécurité

- [ ] Authentification utilisateur (OAuth2)
- [ ] Rate limiting sur les endpoints
- [ ] Validation stricte des inputs
- [ ] Secrets management (env vars chiffrées)
- [ ] CORS restrictif en production

---

## Ressources Utiles

### Documentation
- [OpenWeather API](https://openweathermap.org/api) - Pour données météo financières
- [Finnhub API](https://finnhub.io/) - Alternative à Yahoo Finance (gratuit 250 requêtes/mois)
- [Polygon.io](https://polygon.io/) - Données de marché gratuites
- [Alpha Vantage](https://www.alphavantage.co/) - Données technique gratuites

### Librairies Python
- `yfinance` - Déjà utilisé ✅
- `pandas` - Analyse de données
- `numpy` - Calculs numériques
- `scikit-learn` - Machine learning optionnel
- `plotly` - Graphiques interactifs

### Librairies JavaScript
- `recharts` - Graphiques (déjà dans package.json)
- `chart.js` - Alternative
- `ws` - WebSocket client

---

**Bonne chance pour le développement! 🚀**
