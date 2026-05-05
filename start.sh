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

# Libérer les ports si déjà occupés
echo "🔍 Vérification des ports..."
BACKEND_PORT_PID=$(lsof -ti:8000 2>/dev/null)
FRONTEND_PORT_PID=$(lsof -ti:3000 2>/dev/null)

if [ -n "$BACKEND_PORT_PID" ]; then
    echo "⚠️  Port 8000 occupé (PID $BACKEND_PORT_PID) — arrêt en cours..."
    kill $BACKEND_PORT_PID 2>/dev/null
    sleep 1
fi

if [ -n "$FRONTEND_PORT_PID" ]; then
    echo "⚠️  Port 3000 occupé (PID $FRONTEND_PORT_PID) — arrêt en cours..."
    kill $FRONTEND_PORT_PID 2>/dev/null
    sleep 1
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

# Déterminer l'URL d'accès
if grep -q "investor-app" /etc/hosts 2>/dev/null; then
    APP_URL="http://investor-app:3000"
else
    APP_URL="http://localhost:3000"
fi

print_header "Application Lancée!"
echo "📊 Dashboard:  $APP_URL"
echo "📚 API Docs:   http://localhost:8000/docs"
echo "🏥 API Health: http://localhost:8000/health"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter l'application"
echo ""

wait
