#!/bin/bash

echo "🚀 Démarrage de Investor AI..."
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier si on est dans le bon répertoire
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Erreur: Veuillez exécuter ce script depuis le répertoire 'Investor AI'${NC}"
    exit 1
fi

# Étape 1: Backend
echo -e "${YELLOW}📦 Étape 1: Configuration du Backend...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
fi

source venv/bin/activate

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Fichier .env créé${NC}"
fi

echo "Installation des dépendances..."
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Dépendances installées${NC}"

cd ..

# Étape 2: Frontend
echo ""
echo -e "${YELLOW}📦 Étape 2: Configuration du Frontend...${NC}"
cd frontend

if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Erreur: package.json non trouvé${NC}"
    exit 1
fi

if [ ! -d "node_modules" ]; then
    echo "Installation des dépendances Node..."
    npm install -q
    echo -e "${GREEN}✅ Dépendances installées${NC}"
else
    echo -e "${GREEN}✅ Dépendances déjà installées${NC}"
fi

cd ..

# Résumé
echo ""
echo -e "${GREEN}✅ Setup terminé !${NC}"
echo ""
echo "🚀 Pour démarrer l'application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Dashboard: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
