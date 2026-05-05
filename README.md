# 💰 Investor AI - Personal Financial Analyst

Un agent IA gratuit et open-source pour suivre vos investissements et analyser vos données financières.

## ✨ Fonctionnalités - Phase 1 (Actuellement en place)

### Dashboard de Suivi d'Investissements
- ✅ **Ajouter des actifs** (Actions, Cryptos, ETFs, Devises)
- ✅ **Gérer un portefeuille** avec prix en temps réel via Yahoo Finance
- ✅ **Vue globale** du portefeuille (valeur, gain/perte, performance)
- ✅ **Analyse des positions** avec meilleur/pire performer
- ✅ **Historique des transactions** et des prix
- ✅ **Interface web moderne** (React + Tailwind CSS)

## 🗓️ Phases à Venir

### Phase 2: Analyse Actualités Financières (À venir)
- Récupération des actualités pertinentes pour vos actifs
- Score d'impact/risque par actualité
- Historique des actualités par actif
- Alertes sur les actifs clés

### Phase 3: Agent IA avec Recommandations (À venir)
- Analyse automatique de votre portefeuille
- Recommandations d'achat/vente basées sur l'IA
- Chat interactif pour vos questions financières
- Analyse de risque et diversification
- Stratégies d'investissement personnalisées

## 🛠️ Stack Technique (100% Gratuit)

```
Backend:       FastAPI (Python)
Frontend:      Next.js + React + Tailwind CSS
Database:      SQLite (local) ou PostgreSQL (scalable)
Finance Data:  Yahoo Finance API (gratuit)
LLM:           Claude API (phase 3)
Hosting:       Vercel (frontend) + Render/Railway (backend)
```

## 📊 Structure du Projet

```
Investor AI/
├── backend/
│   ├── main.py              # API FastAPI
│   ├── models.py            # Modèles de données
│   ├── crud.py              # Opérations DB
│   ├── schemas.py           # Validation Pydantic
│   ├── finance_service.py   # Integration Yahoo Finance
│   ├── config.py            # Configuration
│   ├── requirements.txt     # Dépendances Python
│   └── investments.db       # Base de données SQLite
│
├── frontend/
│   ├── app/
│   │   ├── page.jsx         # Dashboard principal
│   │   ├── layout.jsx       # Layout React
│   │   └── globals.css      # Styles globaux
│   ├── components/
│   │   ├── PortfolioComponents.jsx  # Composants du portfolio
│   │   └── Modals.jsx        # Modales d'ajout
│   ├── lib/
│   │   ├── api.js           # Client API
│   │   └── utils.js         # Utilitaires
│   ├── package.json         # Dépendances Node
│   └── tailwind.config.js   # Configuration Tailwind
│
└── docs/
    ├── GETTING_STARTED.md   # Guide complet
    └── README.md            # Ce fichier
```

## 🚀 Démarrage Rapide (5 minutes)

### 1️⃣ Backend
```bash
cd "Investor AI/backend"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
# API disponible à http://localhost:8000
```

### 2️⃣ Frontend
```bash
cd "Investor AI/frontend"
npm install
npm run dev
# Dashboard disponible à http://localhost:3000
```

### 3️⃣ C'est prêt! 🎉
- Ouvrez http://localhost:3000
- Ajoutez vos premiers actifs (ex: AAPL, BTC-USD)
- Enregistrez vos positions d'investissement

## 📖 Documentation

- **[🚀 Guide de Démarrage Complet](docs/GETTING_STARTED.md)** - Instructions détaillées
- **[📚 API Swagger](http://localhost:8000/docs)** - Documentation API interactive
- **[💡 Exemples d'Utilisation](docs/EXAMPLES.md)** - Cas d'usage pratiques

## 💰 Coûts

| Service | Phase | Coût |
|---------|-------|------|
| Yahoo Finance API | 1-3 | **Gratuit** ✅ |
| NewsAPI | 2 | **Gratuit** (500 requêtes/mois) |
| Anthropic Claude API | 3 | **5$ gratuit** + paiement à l'usage |
| Vercel (Frontend) | 1-3 | **Gratuit** ✅ |
| Render/Railway (Backend) | 1-3 | **Gratuit**tier limité |

**Coût total pour démarrer: 0€**  
**Coût estimé pour production avec recommandations IA: 5-20€/mois**

## 🔒 Sécurité

- Données stockées en local (vous possédez vos données)
- Pas de surveillance de vos transactions
- Pas de partage de données avec des tiers
- Vous pouvez auto-héberger

## 📱 Roadmap

- [x] Phase 1: Dashboard de suivi
- [x] Integration Yahoo Finance
- [ ] Phase 2: Actualités financières
- [ ] Phase 3: Agent IA avec recommandations
- [ ] Mobile app (PWA)
- [ ] Export rapports PDF
- [ ] Multi-compte utilisateurs
- [ ] Intégrations brokers (API)
- [ ] Alertes automatiques
- [ ] Backtesting de stratégies

## 🤝 Contribution

Contributions bienvenues! N'hésitez pas à:
- Ouvrir des issues pour les bugs
- Proposer des nouvelles fonctionnalités
- Améliorer la documentation
- Partager vos idées

## 📄 Licence

MIT License - Libre d'utilisation à titre personnel et commercial

## 🙏 Crédits

- [FastAPI](https://fastapi.tiangolo.com/) - Framework API
- [Next.js](https://nextjs.org/) - Framework React
- [Tailwind CSS](https://tailwindcss.com/) - CSS Utilities
- [Yahoo Finance](https://finance.yahoo.com/) - Données financières
- [Anthropic Claude](https://www.anthropic.com/) - LLM pour recommandations

---

**Créé avec ❤️ pour votre liberté financière**

Pour les questions: consultez la documentation ou les issues GitHub.
