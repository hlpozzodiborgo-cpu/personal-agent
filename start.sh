#!/bin/bash

# Script pour démarrer le backend et frontend en parallèle

cd "$(dirname "$0")"

# Fonction pour afficher les logs avec couleur
print_header() {
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "🚀 $1"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
}

# Fonction de nettoyage à la fermeture
cleanup() {
    echo ""
    echo "🛑 Arrêt de l'application..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

print_header "Démarrage de Investor AI"

# Vérifier le setup
if [ ! -d "backend/venv" ] || [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  Setup non complété. Exécutez d'abord: bash setup.sh"
    exit 1
fi

# Backend
print_header "Backend"
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# Frontend
print_header "Frontend"  
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

print_header "Application Lancée!"
echo "📊 Dashboard:  http://localhost:3000"
echo "📚 API Docs:   http://localhost:8000/docs"
echo "🏥 API Health: http://localhost:8000/health"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter l'application"
echo ""

wait
