# 🎯 VOTRE AGENT AI FINANCIER - GUIDE COMPLET & DÉTAILLÉ

## 📌 Ce qui a été créé pour vous

J'ai construit une **application complète** de suivi d'investissements avec IA. Elle comprend:

- ✅ **Backend API** (Python/FastAPI) - Gère vos investissements
- ✅ **Frontend Dashboard** (React/Next.js) - Interface web moderne
- ✅ **Base de données** (SQLite) - Stocke vos données localement
- ✅ **Integration Yahoo Finance** - Récupère les prix en temps réel
- ✅ **Documentation complète** - Tous les détails et exemples

**Coût: 0€ pour démarrer. Optionnel: 5-20€/mois si vous voulez les recommandations IA**

---

## 🚀 ÉTAPE 1: PRÉPARATION (5 minutes)

### 1.1 Vérifier que vous avez les prérequis

**Vérifier Python:**
```bash
python3 --version
# Devrait afficher: Python 3.8 ou plus récent
```

**Vérifier Node.js:**
```bash
node --version
npm --version
# Devraient afficher les versions (ex: v18.0.0, 9.0.0)
```

**Si manquant:**
- **Python**: https://www.python.org/downloads/
- **Node.js**: https://nodejs.org/ (choisir LTS)

### 1.2 Naviguer dans le dossier du projet

```bash
cd "Investor AI"
```

**Note:** Remplacez `"Investor AI"` par le chemin exact si dans un dossier différent.

---

## 🛠️ ÉTAPE 2: SETUP AUTOMATIQUE (2 minutes)

Le folder contient un script `setup.sh` qui automatise tout. Exécutez:

```bash
bash setup.sh
```

**Cela va faire:**
1. ✅ Créer un environnement Python virtuel (`backend/venv/`)
2. ✅ Installer toutes les dépendances Python listées dans `backend/requirements.txt`
3. ✅ Installer toutes les dépendances Node.js (`frontend/node_modules/`)
4. ✅ Générer les fichiers de configuration `.env`

**Vous verrez:**
```
🔧 Configuration chargée | DEBUG: True | DB: sqlite:///./investments.db
✅ Dépendances installées
✅ Setup terminé !
```

---

## ▶️ ÉTAPE 3: LANCER L'APPLICATION (1 minute)

### Option A: Automatique (Recommandé)

```bash
bash start.sh
```

Cela démarre le backend ET le frontend dans la même commande.

### Option B: Manuel (Flexibilité)

**Terminal 1 - Backend:**
```bash
cd "Investor AI/backend"
source venv/bin/activate  # Activer l'environnement Python
python main.py
```

Vous verrez:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
📚 Docs disponibles à: http://localhost:8000/docs
```

**Terminal 2 - Frontend:**
```bash
cd "Investor AI/frontend"
npm run dev
```

Vous verrez:
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
```

---

## 🌐 ÉTAPE 4: ACCÉDER AU DASHBOARD (30 secondes)

### Ouvrir dans votre navigateur:

1. **Dashboard Principal**: http://localhost:3000
   - C'est ici que vous gérez votre portefeuille

2. **Documentation API**: http://localhost:8000/docs
   - Documentation interactive pour tous les endpoints API

3. **Vérifier l'API**: http://localhost:8000/health
   - Confirme que le backend fonctionne

---

## 💻 ÉTAPE 5: UTILISER LE DASHBOARD (Détaillé)

### 5.1 Première page - Accueil

Vous voyez:
```
💰 Investor AI
Votre analyste financier personnel

[➕ Ajouter des Actifs] [📊 Ajouter une Position] [🔄 Actualiser]
```

### 5.2 Ajouter des Actifs à Suivre

**Qu'est-ce qu'un actif?**
- Une action: AAPL (Apple)
- Une cryptomonnaie: BTC-USD (Bitcoin)
- Un ETF: VFV (Fonds indiciel)
- Une devise: EUR=X (Taux EUR/USD)

**Comment ajouter:**

1. Cliquez sur **"➕ Ajouter des Actifs"**
2. Une fenêtre s'ouvre
3. Entrez les symboles (séparés par des virgules):
   ```
   AAPL, BTC-USD, VFV.TO
   ```
4. Cliquez **"Ajouter"**

**Symboles populaires:**

| Catégorie | Exemples |
|-----------|----------|
| **Actions USA** | AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA |
| **Actions Canada** | RY.TO, TD.TO, CM.TO, BMO.TO |
| **Actions Europe** | SAP, ASML, MC.PA, SIE.DE |
| **Cryptos** | BTC-USD, ETH-USD, DOGE-USD |
| **ETFs USA** | SPY, QQQ, VOO, VTI |
| **ETFs Canada** | XUU.TO, XUU, XIC.TO, VFV |
| **Devises** | EUR=X, GBP=X, CAD=X |
| **Indices** | ^GSPC (S&P 500), ^DJI (Dow) |

**⚠️ Astuces:**
- Les prix se téléchargent **automatiquement** via Yahoo Finance
- Vous voyez un message ✅ ou ❌ si l'ajout a fonctionné
- Si un symbole ne fonctionne pas, cherchez le bon sur Yahoo Finance

### 5.3 Ajouter des Positions (vos investissements)

**Qu'est-ce qu'une position?**
- Vous possédez des actions AAPL = 1 position dans AAPL
- Vous possédez du BTC = 1 position dans BTC

**Comment ajouter:**

1. Cliquez sur **"📊 Ajouter une Position"**
2. Une fenêtre s'ouvre avec trois champs:

   | Champ | Exemple | Explication |
   |-------|---------|-------------|
   | **Actif** | AAPL | Choisir dans la liste des actifs |
   | **Quantité** | 10 | Nombre de parts (ex: 10 actions) |
   | **Prix Moyen (€)** | 143.50 | Votre prix d'achat moyen |
   | **Notes** | Long terme | Optionnel: votre stratégie |

3. **Exemple concret:**
   - Vous avez acheté: 10 actions AAPL à 140€ chacune = 1,400€ investi
   - Vous avez acheté: 5 actions AAPL à 145€ chacune = 725€ investi
   - **Prix moyen**: (1,400 + 725) / 15 = 141.67€
   - **Entrer**: Quantité=15, Prix Moyen=141.67

4. Cliquez **"Ajouter"**

### 5.4 Consulter votre Portefeuille

Après avoir ajouté des positions, vous voyez:

**Section 1 - Statistiques Globales:**
```
┌─────────────────┬─────────────────┬─────────────────┬──────────────┐
│ Total Investi   │ Valeur Actuelle │  Gain/Perte     │ Positions    │
│ 10,000€         │ 10,450€         │ +450€ (+4.5%)   │ 4            │
└─────────────────┴─────────────────┴─────────────────┴──────────────┘
```

**Section 2 - Tableau Détaillé:**
```
Actif | Quantité | Prix Moyen | Prix Actuel | Investi | Valeur Actuelle | Gain/Perte
────┼────────────┼────────────┼─────────────┼─────────┼─────────────────┼────────────
AAPL |    10     |   143.50€  |   148.50€   | 1,435€  |    1,485€       | +50€ (+3.5%)
BTC  |   0.023   |  45,000€   |  46,500€    | 1,035€  |    1,069.50€    | +34.50€
```

**Section 3 - Top Performers:**
```
🚀 Meilleur Performer: BTC (+3.5%)
📉 Moins Bon: AAPL (1.2%)
```

---

## 📈 ÉTAPES PROCHAINES

### Phase 1 (Actuellement en place ✅)
✅ Suivre vos investissements
✅ Voir gains/pertes en temps réel
✅ Vue d'ensemble du portfolio

### Phase 2 (À venir - 2-3 jours)
📰 Ajouter les actualités financières pertinentes
📊 Voir l'impact des nouvelles sur votre portfolio
⚠️ Alertes automatiques sur vos actifs

**Coût:** 0€ (NewsAPI gratuit)

### Phase 3 (À venir - 3-4 jours)
🤖 Agent IA avec recommandations
💡 "Achetez VGRO, c'est un bon moment"
💬 Chat interactif pour vos questions

**Coût:** 5€ (crédit gratuit Claude) + petit usage après

---

## 🔧 CONFIGURATION AVANCÉE

### Utiliser PostgreSQL (au lieu de SQLite)

**Pourquoi?** SQLite c'est simple, PostgreSQL c'est plus robuste pour le multi-utilisateurs.

**Comment:**
1. Installer PostgreSQL: https://www.postgresql.org/download/
2. Créer une base de données:
   ```bash
   psql -U postgres
   CREATE DATABASE investor_ai;
   \q
   ```
3. Éditer `backend/.env`:
   ```
   DATABASE_URL=postgresql://postgres:password@localhost/investor_ai
   ```
4. Redémarrer le backend

### Ajouter des clés API (Phase 2 & 3)

**Pour les actualités (Phase 2):**
1. Allez sur: https://newsapi.org/
2. S'inscrire (gratuit, 500 requêtes/mois)
3. Copier votre clé API
4. Éditer `backend/.env`:
   ```
   NEWSAPI_KEY=abc123xyz789
   ```

**Pour l'IA Recommandations (Phase 3):**
1. Allez sur: https://console.anthropic.com/
2. S'inscrire (5$ gratuit de créanciers)
3. Copier votre clé API
4. Éditer `backend/.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

---

## 🆘 DÉPANNAGE

### "API not found" dans le frontend

**Symptôme:** ❌ Déconnectée (écrit dans l'interface)

**Cause:** Le backend n'est pas en cours d'exécution

**Solution:**
```bash
# Terminal 1: Lancer le backend
cd backend
source venv/bin/activate
python main.py

# Attendre le message:
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### "Cannot find module 'yfinance'"

**Symptôme:** ModuleNotFoundError en lançant le backend

**Cause:** Les dépendances ne sont pas installées ou l'env n'est pas activé

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### "Port 3000 already in use"

**Cause:** Un autre processus utilise le port 3000

**Solution:**
```bash
# Trouver le processus
lsof -i :3000

# Tuer le processus
kill -9 <PID>

# OU démarrer sur un autre port
npm run dev -- -p 3001
# Puis ouvrir http://localhost:3001
```

### "Symbole non trouvé" (ex: AAPL-USD)

**Cause:** Le symbole n'existe pas exactement comme ça

**Solution:**
1. Cherchez le bon symbole sur Yahoo Finance: https://finance.yahoo.com/
2. Essayez sans le `-USD` (généralement pas nécessaire pour les US stocks)
3. Utilisez: `AAPL` au lieu de `AAPL-USD`

---

## 📊 EXEMPLES CONCRETS

### Exemple 1: Portfolio Diversifié

```
Investissements:
- AAPL: 5,000€ (35 actions @ 142.86€)
- VTI: 2,000€ (40 parts @ 50€)
- BTC-USD: 1,000€ (0.023 BTC @ 45,000€)
- EUR=X: 2,000€ (2000€ @ 1€/taux)
TOTAL: 10,000€

Dashboard affiche:
Total Investi: 10,000€
Valeur Actuelle: 10,450€ (prix du marché maintenant)
Gain: +450€ (+4.5%)

AAPL gagne +3.5%, BTC gagne +3.3%, EUR stable
```

### Exemple 2: Suivre différentes devises

```
Si vous êtes en Suisse (CHF)
Actifs:
- AAPL: 100 USD (~91 CHF avec taux 0.91)
- CHF=X: Taux CHF/EUR
- EUR=X: Taux EUR/USD

Dashboard montre automatiquement:
"Vos gains US stocks sont influencés par la force du USD"
```

---

## 📱 DÉPLOIEMENT (En ligne)

### Déployer le Frontend (Gratuit sur Vercel)

```bash
npm install -g vercel
cd frontend
vercel
# Suivre les instructions
```

### Déployer le Backend (Gratuit tier sur Render)

1. Créer compte: https://render.com
2. New → Web Service
3. Connecter votre GitHub
4. Configuration:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port 8000`
5. Deploy!

---

## ✅ CHECKLIST FINALE

- [ ] `bash setup.sh` a fonctionné sans erreurs
- [ ] Backend tourne: `http://localhost:8000/health` retourne ✅
- [ ] Frontend accessible: `http://localhost:3000` fonctionne
- [ ] J'ai ajouté au moins 3 actifs
- [ ] J'ai la notion de "quantité" vs "prix moyen" OK
- [ ] Le dashboard montre mes positions et gains/pertes
- [ ] Documentation API: `http://localhost:8000/docs` accessible

---

## 🎓 POUR ALLER PLUS LOIN

### Lire la documentation compléte:

- **QUICKSTART.md** - Plan d'action rapide
- **docs/GETTING_STARTED.md** - Guide approfondi
- **docs/EXAMPLES.md** - Cas d'usage et scripts
- **docs/PHASES_2_3.md** - Roadmap des prochaines phases

### Documentation API:

Allez directement à: **http://localhost:8000/docs**

Vous verrez tous les endpoints avec des exemples interactifs!

---

## 🎉 VOUS ÊTES PRÊT!

Votre agent IA financier personnel est en place et fonctionnel. Vous avez:

✅ **Dashboard en temps réel** - Suivre vos investissements
✅ **API complète** - Extensible pour vos besoins
✅ **Architecture scalable** - Déployable en production facilement
✅ **Préparation pour l'IA** - Prêt pour les recommandations

**Prochaines étapes:**
1. Commencez à ajouter vos vrais investissements
2. Testez avec différents types d'actifs
3. Envisagez le déploiement en ligne (Vercel + Render)
4. Planifiez les phases 2 & 3

---

**Besoin d'aide? Consultez la documentation ou explorez le code!**

**Happy investing! 🚀📊💰**
