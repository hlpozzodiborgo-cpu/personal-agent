# 🚀 Phase 2 - Quick Start Guide

## ⚡ En 5 minutes: Activer les recommandations

### Étape 1: Démarrage
```bash
# Backend
cd backend
python main.py

# Frontend (terminal séparé)
cd frontend
npm run dev
```

### Étape 2: Vérifier l'installation
```bash
# Vérifier que les routes news sont chargées
curl http://localhost:8000/api/settings
# Doit retourner: {"finnhub_configured": true}
```

### Étape 3: Tester les recommandations
```bash
# Récupérer les recommandations pour vos actifs
curl "http://localhost:8000/api/news/recommendations?symbols=AAPL,MSFT"
```

### Étape 4: Voir dans le dashboard
1. Ouvrir http://localhost:3000
2. Ajouter des positions (ex: AAPL, MSFT, GOOGL)
3. Descendre en bas du dashboard
4. Section "📰 Actualités & Recommandations" = Phase 2 live! 🎉

## 📊 Comprendre les recommandations

| Emoji | Type | Signification | Action |
|-------|------|---------------|--------|
| 🟢 | BUY | Nombreuses actualités positives | À acheter |
| 🔴 | SELL | Actualités négatives détectées | À vendre/réduire |
| ⚪ | HOLD | Sentiment neutre, position stable | Maintenir |
| 🟡 | MONITOR | Peu de données, à surveiller | Attendre clarification |

## 🎯 Les scores

- **Sentiment Score** (-1 à +1)
  - `+0.75` = Très positif ✅
  - `+0.3` à `+0.75` = Positif 📈
  - `-0.3` à `+0.3` = Neutre ⚪
  - `-0.3` à `-0.75` = Négatif 📉
  - `< -0.75` = Très négatif ❌

- **Confidence** (0-100%)
  - Basé sur la force du sentiment
  - Plus haut = plus de certitude
  - \> 60% = Recommandation "forte"

## 🔔 Alertes Email (Optionnel)

### Configuration
```env
# backend/.env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=votre-email@gmail.com
SENDER_PASSWORD=votre-mot-de-passe-app  # ⚠️ Pas le vrai mot de passe!
```

### Pour Gmail:
1. Aller à https://myaccount.google.com/apppasswords
2. Générer "App Password"
3. Copier-coller dans `.env`

### Test
```bash
curl -X POST "http://localhost:8000/api/news/test-email?email=votre@email.com"
```

## 📈 Cas d'usage

### 1. Suivre un secteur
```bash
curl "http://localhost:8000/api/news/recommendations?symbols=AAPL,MSFT,NVDA&hours=24"
# Voir les tendances du secteur tech
```

### 2. Alertes avant market open
- Configuration email + cron job
- Recommandations frappent votre boîte chaque matin
- Vous décidez d'acheter/vendre avant l'ouverture

### 3. Suivi du portefeuille
- Dashboard mise à jour auto chaque minute
- Voyez immédiatement les actualités de vos actifs
- Sentiment analysis pour contexte

## 🔧 Troubleshooting

### "Aucune actualité affichée"
```bash
# 1. Vérifier Finnhub key
echo $FINNHUB_API_KEY

# 2. Vérifier les logs du backend
# Chercher: [FINNHUB] ou ❌ tags

# 3. Test direct
curl "http://localhost:8000/api/news/recommendations?symbols=AAPL"
```

### "Email non envoyé"
```bash
# 1. Tester la config
curl -X POST "http://localhost:8000/api/news/test-email?email=test@example.com"

# 2. Vérifier les variables d'env
python -c "import os; print(os.getenv('SENDER_EMAIL'))"

# 3. Vérifier les logs
# Chercher: ❌ ou ✅ tags
```

### Performance lente
- Actualités peuvent prendre 2-5 secondes à charger
- C'est normal (requête Finnhub)
- Frontend loader affiche l'attente

## 🎓 Comment ça marche

### Architecture
```
Frontend              Backend              Finnhub
┌─────────────────┐  ┌──────────────┐    ┌──────────┐
│ Dashboard       │──│ API Routes   │───→│ News API │
│ NewsRecommen    │  │              │    │          │
│ dations.jsx     │  │ news_service │    └──────────┘
└─────────────────┘  │ .py          │
                     │              │
                     │ recommendation_
                     │ engine.py    │
                     │              │
                     │ email_service│
                     │ .py          │
                     └──────────────┘
```

### Data Flow
1. **Frontend** demande recommandations: `GET /api/news/recommendations?symbols=AAPL`
2. **Backend news_service** appelle Finnhub
3. **recommendation_engine** analyse le sentiment
4. **Frontend** affiche les résultats
5. (Optionnel) **email_service** envoie alertes

### Sentiment Analysis
```
Article: "Apple beats earnings expectations"
↓
Mots-clés positifs trouvés: ["beat", "expectations"] = +2
Mots-clés négatifs trouvés: [] = 0
Score = +2 / 2 = +1.0 = Très positif ✅
```

## 🚨 Limites connues (à corriger en Phase 3)

- ⚠️ Sentiment analysis par mots-clés (pas de ML)
- ⚠️ Pas de cache des actualités (appel API chaque fois)
- ⚠️ Pas de persistence en DB
- ⚠️ Email peut être slow (requête SMTP bloquante)
- ⚠️ Pas de timezone awareness (UTC seulement)

## 📚 Fichiers importants

```
Phase 2 Files:
├── backend/
│   ├── news_service.py          ← Récupère les actus
│   ├── recommendation_engine.py ← Crée les recommandations
│   ├── email_service.py         ← Envoie les alertes
│   ├── schemas_news.py          ← Types Pydantic
│   ├── routes_news.py           ← Endpoints /api/news/*
│   └── main.py                  ← Intègre les routes
├── frontend/
│   ├── components/
│   │   └── NewsRecommendations.jsx ← Affichage
│   └── app/
│       └── page.jsx             ← Intègre le composant
└── PHASE_2_IMPLEMENTATION.md    ← Docs complètes
```

## ✅ Checklist de déploiement

- [ ] Backend démarre sans erreurs
- [ ] `GET /api/settings` retourne `{"finnhub_configured": true}`
- [ ] `curl /api/news/recommendations?symbols=AAPL` fonctionne
- [ ] Frontend affiche "Actualités & Recommandations"
- [ ] Ajout de positions affiche les recommandations
- [ ] (Optionnel) Email test fonctionne

## 🎉 Bravo!

Phase 2 est maintenant active! Vous avez:
- ✅ Actualités en temps réel
- ✅ Recommandations basées sur sentiment
- ✅ Alertes email (optionnel)
- ✅ Widget intégré au dashboard

**Next**: Phase 3 sera:
- Intégration Claude IA pour analyse approfondie
- Persistence en DB des recommandations
- Optimisations performance

---

Questions? Cherchez `[FINNHUB]`, `[RECOMMENDATION]`, ou `[EMAIL]` dans les logs du backend.
