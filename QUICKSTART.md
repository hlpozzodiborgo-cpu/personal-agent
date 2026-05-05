# 🎯 Plan d'Action - Démarrage Rapide

## ✅ Étape 1: Setup Automatique (2 minutes)

### Sur macOS/Linux:

```bash
cd "Investor AI"

# Rendre les scripts exécutables
chmod +x setup.sh start.sh

# Lancer le setup
bash setup.sh
```

Cela va:
- ✅ Créer l'environnement Python virtuel
- ✅ Installer toutes les dépendances backend
- ✅ Installer toutes les dépendances frontend
- ✅ Préparer la configuration

## ✅ Étape 2: Lancer l'Application (1 minute)

### Option A: Script automatisé
```bash
cd "Investor AI"
bash start.sh
```

### Option B: Manuel (2 terminaux)

**Terminal 1 - Backend:**
```bash
cd "Investor AI/backend"
source venv/bin/activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd "Investor AI/frontend"
npm run dev
```

## ✅ Étape 3: Accéder à l'Application (30 secondes)

### Ouvrir le dashboard
- 🌐 **Dashboard**: http://localhost:3000
- 📚 **API Swagger Docs**: http://localhost:8000/docs
- 🏥 **API Health**: http://localhost:8000/health

## 🎮 Étape 4: Utiliser le Dashboard (5 minutes)

### 1. Ajouter des Actifs
- Cliquer: **➕ Ajouter des Actifs**
- Entrer des symboles: `AAPL, BTC-USD, VFV.TO`
- Les prix se téléchargent automatiquement ✨

### 2. Créer des Positions
- Cliquer: **📊 Ajouter une Position**
- Sélectionner l'actif
- Entrer:
  - **Quantité**: ex. 10 (actions)
  - **Prix moyen**: ex. 143.50 (€ d'achat moyen)
  - **Notes**: ex. "Investissement long terme"

### 3. Voir votre Portfolio
- Dashboard affiche automatiquement:
  - 📈 **Total Investi** (ce que vous avez mis)
  - 💹 **Valeur Actuelle** (prix du marché maintenant)
  - 📊 **Gain/Perte** (€ et %)
  - 🏆 **Top Performers** (meilleur/pire)

## 📊 Architecture du Projet

```
Investor AI/
├── README.md                    ← 👈 Lire en premier
├── setup.sh                     ← 👈 Lancer le setup
├── start.sh                     ← 👈 Démarrer l'app
├── docker-compose.yml           ← Pour déploiement facile
│
├── backend/                     ← API Python (FastAPI)
│   ├── main.py                  ← Application principale
│   ├── models.py                ← Modèles de base de données
│   ├── crud.py                  ← Opérations CRUD
│   ├── schemas.py               ← Validation des données
│   ├── finance_service.py       ← Integration Yahoo Finance
│   ├── config.py                ← Configuration
│   ├── requirements.txt         ← Dépendances Python
│   ├── .env.example             ← Template config
│   └── investments.db           ← Base de données SQLite
│
├── frontend/                    ← Dashboard React
│   ├── app/
│   │   ├── page.jsx            ← Accueil du dashboard
│   │   ├── layout.jsx          ← Layout React
│   │   └── globals.css         ← Styles
│   ├── components/
│   │   ├── PortfolioComponents.jsx    ← Composants portfolio
│   │   └── Modals.jsx          ← Modales d'ajout
│   ├── lib/
│   │   ├── api.js              ← Client API
│   │   └── utils.js            ← Utilitaires
│   ├── package.json            ← Dépendances Node
│   └── tailwind.config.js      ← Config Tailwind CSS
│
└── docs/                        ← Documentation
    ├── GETTING_STARTED.md      ← Guide complet
    ├── PHASES_2_3.md           ← Roadmap futures phases
    ├── EXAMPLES.md             ← Exemples d'utilisation
    └── README.md               ← Ce fichier
```

## 🔌 API REST - Points d'accès clés

### Health Check
```bash
curl http://localhost:8000/health
# Réponse: {"status": "ok", "timestamp": "...", "debug": true}
```

### Ajouter un Actif
```bash
curl -X POST "http://localhost:8000/api/assets/add?symbol=AAPL&name=Apple&asset_type=stock"
```

### Ajouter une Position
```bash
curl -X POST "http://localhost:8000/api/holdings/add?asset_id=1&quantity=10&avgPrice=143.50"
```

### Voir votre Portfolio
```bash
curl http://localhost:8000/api/portfolio
```

**Documentation complète**: http://localhost:8000/docs

## 💡 Symboles Courants Yahoo Finance

| Type | Exemples |
|------|----------|
| Actions USA | `AAPL`, `MSFT`, `GOOGL`, `AMZN`, `TSLA` |
| Actions Canada | `RY.TO`, `TD.TO`, `CM.TO` |
| Actions Europe | `SAP`, `ASML`, `MC.PA` (LVMH) |
| Cryptos | `BTC-USD`, `ETH-USD`, `DOGE-USD` |
| ETFs USA | `SPY`, `QQQ`, `VTI`, `VOO` |
| ETFs Canada | `XUU.TO`, `XUU`, `VFV` |
| Devises | `EUR=X`, `GBP=X`, `CAD=X`, `CHF=X` |
| Indices | `^GSPC` (S&P500), `^DJI` (Dow Jones) |

## ⚠️ Problèmes Courants & Solutions

### "Cannot connect to API"
```bash
# Vérifier que le backend tourne
curl http://localhost:8000/health

# Si ça marche pas, lancer le backend
cd backend && source venv/bin/activate && python main.py
```

### "Module not found error"
```bash
# Réactiver l'environnement virtuel
cd backend
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### "Port 3000/8000 already in use"
```bash
# Voir quel processus utilise le port
lsof -i :3000
lsof -i :8000

# Tuer le processus
kill -9 <PID>

# Ou démarrer sur un autre port
npm run dev -- -p 3001
```

### "Prices not updating"
```bash
# Vérifier connexion internet
ping 8.8.8.8

# Vérifier que Yahoo Finance fonctionne
curl "https://query1.finance.yahoo.com/v10/finance/quoteSummary/AAPL"
```

## 🚀 Déploiement Simple (Production)

### Frontend sur Vercel (Gratuit & Facile)

1. Créer un compte: https://vercel.com
2. Connecter GitHub
3. Importer le projet
4. Configurer `NEXT_PUBLIC_API_URL` vers votre backend
5. Déployer! ✨

### Backend sur Render/Railway (Gratuit tier)

**Option 1: Render.com**
1. Créer: https://render.com
2. New → Web Service
3. Connecter GitHub
4. Build command: `pip install -r backend/requirements.txt`
5. Start command: `uvicorn backend.main:app --host 0.0.0.0`
6. Déployer!

**Option 2: Railway.app**
1. Créer: https://railway.app
2. Create Project
3. Deploy from GitHub
4. Configurer variables d'env
5. Déployer!

**Coût**: Gratuit tier pour démarrer (~5-10€/mois si actif)

## 📈 Phases à Venir

### Phase 2: Actualités Financières (2-3 jours)
- Récupérer les nouvelles pertinentes
- Analyser le sentiment (bullish/bearish)
- Afficher dans le dashboard

### Phase 3: Agent IA avec Recommandations (3-4 jours)
- Claude API pour analyser votre portfolio
- Générer des recommandations d'achat/vente
- Chat IA pour vos questions

**Documentation**: Voir [docs/PHASES_2_3.md](docs/PHASES_2_3.md)

## 💰 Coûts Totaux

| Service | Coût |
|---------|------|
| Stack de base (Phase 1) | **0€** ✅ |
| Avec actualités (Phase 2) | **0€** ✅ |
| Avec IA recommandations (Phase 3) | **5€** (crédit free Claude) + usage |
| **TOTAL** | **0-20€/mois** |

## ✅ Checklist - Prêt à Déployer

- [ ] Installer et lancer avec `bash setup.sh` + `bash start.sh`
- [ ] Ajouter au moins 3 actifs différents
- [ ] Créer au moins 1 position pour tester
- [ ] Vérifier que le gain/perte s'affiche correctement
- [ ] Consulter la documentation API: http://localhost:8000/docs
- [ ] Lire [docs/EXAMPLES.md](docs/EXAMPLES.md) pour cas d'usage avancés

## 🆘 Besoin d'Aide?

1. **Lire la documentation**: [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)
2. **Consulter les exemples**: [docs/EXAMPLES.md](docs/EXAMPLES.md)
3. **API Docs**: http://localhost:8000/docs (Swagger UI)
4. **Logs du backend**: Voir les messages de console

## 🎉 Prochaines Étapes

1. **Démarrer rapidement**:
   ```bash
   bash setup.sh
   bash start.sh
   ```

2. **Tester le dashboard**:
   - http://localhost:3000
   - Ajouter quelques actifs
   - Créer des positions

3. **Explorer les fonctionnalités**:
   - Consulter la doc API: http://localhost:8000/docs
   - Lire les exemples: [docs/EXAMPLES.md](docs/EXAMPLES.md)

4. **Planifier les phases 2 & 3**:
   - Lire [docs/PHASES_2_3.md](docs/PHASES_2_3.md)
   - Provisioner clés API au besoin

---

**Bon développement! 🚀📊💰**

*Si vous trouvez des bugs ou avez des questions, n'hésitez pas à Explorer le code et améliorer l'application.*
