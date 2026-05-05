FROM node:18-alpine

WORKDIR /app

# Copier package.json
COPY frontend/package*.json ./

# Installer les dépendances
RUN npm ci

# Copier le code du frontend
COPY frontend/ .

# Build
RUN npm run build

# Exposer le port
EXPOSE 3000

# Commande de démarrage
CMD ["npm", "start"]
