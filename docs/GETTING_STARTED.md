# 🚀 Guide de Démarrage - Investor AI

## Vue d'ensemble du projet

**Investor AI** est un agent IA personnel qui agit comme votre analyste financier personnel pour:
1. **Phase 1 (EN COURS)**: Suivre vos investissements via un dashboard
2. **Phase 2**: Analyser les actualités financières 
3. **Phase 3**: Générer des recommandations IA

## Architecture

```
Investor AI/
├── backend/          # API FastAPI (Python)
│   ├── main.py       # Application principale
│   ├── models.py     # Modèles SQLAlchemy
│   ├── crud.py       # Operations base de données
│   ├── schemas.py    # Schemas Pydantic
│   ├── finance_service.py  # Integration Yahoo Finance
│   ├── config.py     # Configuration
│   └── requirements.txt
│
├── frontend/         # Dashboard Next.js (React)
│   ├── app/          # Pages de l'application
│   ├── components/   # Composants React
│   ├── lib/          # Utilitaires
│   └── package.json
│
└── docs/            # Documentation
```

## Installation - Étape par Étape

### **ÉTAPE 1: Configuration de l'environnement Python**

```bash
cd "Investor AI/backend"

# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate  # Sur macOS/Linux
# OU
venv\Scripts\activate      # Sur Windows

# Installer les dépendances
pip install -r requirements.txt
```

### **ÉTAPE 2: Configurer le Backend**

```bash
cd "Investor AI/backend"

# Copier le fichier .env
cp .env.example .env

# L'éditer avec vos clés API (optionnel pour phase 1)
# nano .env
```

### **ÉTAPE 3: Lancer le Backend**

```bash
cd "Investor AI/backend"
source venv/bin/activate  # S'assurer que l'env est actif

# Lancer l'API
python main.py

# Ou directement avec uvicorn:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ L'API est accessible à: **http://localhost:8000**  
📚 Documentation: **http://localhost:8000/docs** (Swagger UI)

### **ÉTAPE 4: Installation du Frontend**

```bash
cd "Investor AI/frontend"

# Installer les dépendances Node.js
npm install
# ou
yarn install
```

### **ÉTAPE 5: Lancer le Frontend**

```bash
cd "Investor AI/frontend"

# Démarrer le serveur de développement
npm run dev
```

✅ Dashboard accessible à: **http://localhost:3000**

## Utilisation du Dashboard

### **Ajouter des Actifs à Suivre**

1. Cliquez sur **"➕ Ajouter des Actifs"**
2. Entrez les symboles Yahoo Finance (ex: `AAPL, BTC-USD, EUR=X`)
3. Les prix se mettront à jour automatiquement

**Symboles courants:**
- Actions: `AAPL`, `GOOGL`, `MSFT`, `AMZN`
- Crypto: `BTC-USD`, `ETH-USD`
- Devises: `EUR=X`, `GBP=X`
- ETFs: `SPY`, `VOO`, `VTI`

### **Ajouter des Positions (Holdings)**

1. Cliquez sur **"📊 Ajouter une Position"**
2. Sélectionnez l'actif
3. Entrez:
   - **Quantité**: Nombre de parts/pièces
   - **Prix moyen**: Votre prix d'achat moyen (€)
   - **Notes** (optionnel): Stratégie d'investissement

### **Consulter votre Portefeuille**

- **Vue d'ensemble**: Total investi, valeur actuelle, gain/perte
- **Tableau détaillé**: Toutes les positions avec performance
- **Top performers**: Meilleur investissement et pire performance

## API REST - Points d'accès

### **Health Check**
```bash
GET /health
```

### **Assets (Actifs)**
```bash
# Lister tous les actifs
GET /api/assets

# Ajouter un actif
POST /api/assets/add?symbol=AAPL&name=Apple&asset_type=stock

# Infos détaillées d'un actif
GET /api/assets/{symbol}/info

# Historique des prix
GET /api/assets/{symbol}/history?period=1mo&interval=1d
```

### **Portfolio (Portefeuille)**
```bash
# Vue d'ensemble du portefeuille
GET /api/portfolio
```

### **Holdings (Positions)**
```bash
# Ajouter une position
POST /api/holdings/add?asset_id=1&quantity=10&avgPrice=150.50

# Supprimer une position
DELETE /api/holdings/{holding_id}
```

## Configuration Avancée

### **Utiliser PostgreSQL au lieu de SQLite**

1. Installer PostgreSQL
2. Créer une base de données:
   ```sql
   CREATE DATABASE investor_ai;
   ```
3. Modifier `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost/investor_ai
   ```
4. Installer le driver:
   ```bash
   pip install psycopg2-binary
   ```

### **Ajouter des clés API (Phase 2 & 3)**

Pour la phase 2 (actualités) et phase 3 (recommandations IA):

1. **NewsAPI**: https://newsapi.org/ (500 requêtes/mois gratuit)
2. **Anthropic Claude**: https://console.anthropic.com/ (5$ de crédit gratuit)

Ajoutez vos clés à `.env`:
```
NEWSAPI_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

## Troubleshooting

### **"Impossible de se connecter à l'API"**
- Vérifiez que le backend est en cours d'exécution: `http://localhost:8000/health`
- Vérifiez le port 8000 n'est pas utilisé: `lsof -i :8000`

### **"Module not found" en Python**
- Assurez-vous d'avoir activé l'environnement virtuel: `source venv/bin/activate`
- Réinstallez les dépendances: `pip install -r requirements.txt`

### **"Port 3000 déjà utilisé"**
```bash
# Lancer sur un autre port
npm run dev -- -p 3001
```

### **Problèmes de CORS**
- Le backend autorise déjà toutes les origines en dev
- En production, configurez `ALLOWED_ORIGINS` dans `config.py`

## Étapes Suivantes

### **Phase 2: Intégration des Actualités** (À venir)
- Récupérer les actualités financières relatives à vos actifs
- Afficher l'actualité dans le dashboard
- Analyser l'impact sur votre portefeuille

### **Phase 3: Agent IA avec Recommandations** (À venir)
- Analyser vos positions et l'actualité
- Générer des recommandations d'achat/vente
- Chat IA pour poser des questions financières

## Déploiement (Production)

### **Frontend - Déployer sur Vercel (Gratuit)**
```bash
npm install -g vercel
vercel
```

### **Backend - Déployer sur Render/Railway (Gratuit tier)**
1. Pushez le code sur GitHub
2. Connectez le repo à Render/Railway
3. Configurez les variables d'environnement

## Support et Contribution

Pour les questions ou problèmes, consultez la documentation FastAPI swagger: `http://localhost:8000/docs`

---

**Made with ❤️ for personal financial analysis**
