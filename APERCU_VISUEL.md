# 📺 APERÇU VISUEL - Ce Que Vous Verrez

## Page d'Accueil du Dashboard

```
════════════════════════════════════════════════════════════════════════════
                                                                              
                            💰 Investor AI                                  
                    Votre analyste financier personnel                        
                                                                              
════════════════════════════════════════════════════════════════════════════

[➕ Ajouter des Actifs]  [📊 Ajouter une Position]  [🔄 Actualiser]

API Connectée ✅

════════════════════════════════════════════════════════════════════════════
```

---

## Zone de Statistiques Globales

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│  Total Investi          Valeur Actuelle       Gain/Perte          Positions
│  10,000€                10,450€               +450€ (+4.5%)        4        
│  ───────────────────────────────────────────────────────────────────────  
│  Montant total investi | Valeur actuelle      | En vert si positif  │ Nombre de positions
│                        | au prix marchéaujourd'hui        │        
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Tableau Détaillé des Positions

```
┌─────────────┬──────────┬────────────┬─────────────┬──────────┬────────────┬──────────────┐
│ CRYPTO/NOM  │ QUANTITÉ │ PX MOYEN   │ PX ACTUEL   │ INVESTI  │ VAL. ACT.  │ GAIN/PERTE   │
├─────────────┼──────────┼────────────┼─────────────┼──────────┼────────────┼──────────────┤
│ AAPL        │          │            │             │          │            │              │
│ Apple Inc.  │  10.00   │ 143.50€    │ 148.50€     │ 1,435€   │ 1,485€     │ +50€ (+3.5%) │
├─────────────┼──────────┼────────────┼─────────────┼──────────┼────────────┼──────────────┤
│ BTC-USD     │          │            │             │          │            │              │
│ Bitcoin     │ 0.023    │ 45,000€    │ 46,500€     │ 1,035€   │ 1,069.50€  │ +34.50€ (+3%) │
├─────────────┼──────────┼────────────┼─────────────┼──────────┼────────────┼──────────────┤
│ VFV         │          │            │             │          │            │              │
│ S&P 500 ETF │  40.00   │ 50€        │ 51.20€      │ 2,000€   │ 2,048€     │ +48€ (+2.4%) │
├─────────────┼──────────┼────────────┼─────────────┼──────────┼────────────┼──────────────┤
│ EUR=X       │          │            │             │          │            │              │
│ EUR/USD     │ 2,000    │ 1€         │ 1€          │ 2,000€   │ 2,000€     │ 0€ (0%)      │
└─────────────┴──────────┴────────────┴─────────────┴──────────┴────────────┴──────────────┘
```

**Code couleur:**
- 🟢 Vert = Gain (positif)
- 🔴 Rouge = Perte (négatif)
- ⚪ Gris = Pas de changement

---

## Meilleur et Pire Performer

```
┌──────────────────────────────────────────────┬──────────────────────────────────────────────┐
│                                              │                                              │
│          🚀 MEILLEUR PERFORMER                │          📉 MOINS BON PERFORMER             │
│                                              │                                              │
│  BTC-USD (Bitcoin)                           │  EUR=X (EUR/USD)                             │
│  +34.50€ (+3.3%)                             │  0€ (0%)                                      │
│                                              │                                              │
│  Quantité: 0.023                             │  Quantité: 2,000                             │
│  Prix actuel: 46,500€                        │  Prix actuel: 1€                             │
│  Valeur: 1,069.50€                           │  Valeur: 2,000€                              │
│                                              │                                              │
└──────────────────────────────────────────────┴──────────────────────────────────────────────┘
```

---

## Modales (Fenêtres Popup)

### Modal 1: Ajouter des Actifs

```
╔════════════════════════════════════════════════════════════╗
║                   Ajouter des Actifs                       ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  Symboles (séparés par des virgules)                       ║
║  ┌──────────────────────────────────────────────────────┐ ║
║  │ Ex: AAPL, GOOGL, BTC-USD, EUR=X                    │ ║
║  └──────────────────────────────────────────────────────┘ ║
║                                                            ║
║  💡 Utilisez les symboles Yahoo Finance                   ║
║                                                            ║
║  [         Ajouter         ]  [      Annuler      ]        ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

### Modal 2: Ajouter une Position

```
╔════════════════════════════════════════════════════════════╗
║                  Ajouter une Position                      ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  Actif *                                                   ║
║  ┌──────────────────────────────────────────────────────┐ ║
║  │ Sélectionnez un actif                              ▼ │ ║
║  │ ▶ AAPL - Apple Inc.                                  │ ║
║  └──────────────────────────────────────────────────────┘ ║
║                                                            ║
║  Quantité *              │ Prix Moyen (€) *               ║
║  ┌────────────────────┐  │ ┌────────────────────┐         ║
║  │ Ex: 10            │  │ │ Ex: 150.50        │         ║
║  └────────────────────┘  │ └────────────────────┘         ║
║                                                            ║
║  Notes (optionnel)                                         ║
║  ┌──────────────────────────────────────────────────────┐ ║
║  │ Ex: Investissement long terme                      │ ║
║  └──────────────────────────────────────────────────────┘ ║
║                                                            ║
║  [         Ajouter         ]  [      Annuler      ]        ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

---

## Dashboard Vide (Au Démarrage)

```
════════════════════════════════════════════════════════════════════════════

                            💰 Investor AI
                    Votre analyste financier personnel

════════════════════════════════════════════════════════════════════════════

[➕ Ajouter des Actifs]  [📊 Ajouter une Position]  [🔄 Actualiser]

API Désactivée ❌

════════════════════════════════════════════════════════════════════════════

                      Aucun portefeuille encore. 
                Commencez par ajouter des actifs et des positions!

════════════════════════════════════════════════════════════════════════════
```

---

## Affichage Après Liaison (Données Réelles)

```
════════════════════════════════════════════════════════════════════════════

                            💰 Investor AI
                    Votre analyste financier personnel

════════════════════════════════════════════════════════════════════════════

[➕ Ajouter des Actifs]  [📊 Ajouter une Position]  [🔄 Actualiser]

API Connectée ✅

⏱️ Dernière actualisation: 14:30:45

════════════════════════════════════════════════════════════════════════════
STATISTIQUES GLOBALES
════════════════════════════════════════════════════════════════════════════

← Total Investi: 10,000€ →  ← Valeur Actuelle: 10,450€ →  ← Gain: +450€ (+4.5%) →

════════════════════════════════════════════════════════════════════════════
MES POSITIONS
════════════════════════════════════════════════════════════════════════════

[Tableau avec toutes les positions comme montré plus haut]

════════════════════════════════════════════════════════════════════════════
MEILLEUR/PIRE PERFORMER
════════════════════════════════════════════════════════════════════════════

[🚀 Meilleur] [📉 Pire Performer]

════════════════════════════════════════════════════════════════════════════
💡 Phase 1 en place: Dashboard de suivi. Phase 2: Actualités & Recommandations IA à venir
════════════════════════════════════════════════════════════════════════════
```

---

## Documentation API (Swagger)

```
http://localhost:8000/docs

╔═══════════════════════════════════════════════════════════════════════════╗
║                  INVESTOR AI - API DOCUMENTATION                         ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║ GET  /health                    ✅ Vérifier la santé de l'API            ║
║ GET  /api/assets                📊 Lister tous les actifs                ║
║ POST /api/assets/add            ➕ Ajouter un actif                      ║
║ GET  /api/assets/{symbol}/info  ℹ️  Infos détaillées d'un actif         ║
║ GET  /api/portfolio             📈 Vue d'ensemble du portfolio           ║
║ POST /api/holdings/add          📊 Ajouter une position                 ║
║ DELETE /api/holdings/{id}       ❌ Supprimer une position               ║
║ GET  /api/assets/{symbol}/history  📉 Historique des prix              ║
║                                                                           ║
║ Tous les endpoints ont des exemples interactifs!                        ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

---

## Exemple de Réponse API

### Requête: GET /api/portfolio

```json
{
  "stats": {
    "total_invested": 10000,
    "total_current_value": 10450,
    "total_gain_loss": 450,
    "gain_loss_percent": 4.5,
    "number_of_holdings": 4,
    "last_updated": "2026-05-04T14:30:45.123456"
  },
  "holdings": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "quantity": 10,
      "avg_price": 143.50,
      "current_price": 148.50,
      "invested": 1435,
      "current_value": 1485,
      "gain_loss": 50,
      "gain_loss_percent": 3.49
    },
    {
      "symbol": "BTC-USD",
      "name": "Bitcoin",
      "quantity": 0.023,
      "avg_price": 45000,
      "current_price": 46500,
      "invested": 1035,
      "current_value": 1069.50,
      "gain_loss": 34.50,
      "gain_loss_percent": 3.33
    }
  ],
  "top_gainer": {
    "symbol": "BTC-USD",
    "gain_loss_percent": 3.33
  },
  "top_loser": {
    "symbol": "EUR=X",
    "gain_loss_percent": 0
  }
}
```

---

## Console du Backend (Logs)

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
🔧 Configuration chargée | DEBUG: True | DB: sqlite:///./investments.db
📊 Récupération des infos pour AAPL...
INFO:     127.0.0.1:54321 - "POST /api/assets/add HTTP/1.1" 200 OK
✅ Asset AAPL ajouté
📈 Récupération de l'historique 1mo pour AAPL...
INFO:     127.0.0.1:54322 - "GET /api/assets/AAPL/history HTTP/1.1" 200 OK
✅ Historique récupéré
```

---

## Console du Frontend (Logs)

```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
- event compiled client and server successfully (1234 modules)
- 📊 Chargement des données...
- API connectée
- 4 positions chargées
- Portfolio rendu avec succès
```

---

## Saisie d'Exemple - Pas à Pas

### Étape 1: Ajouter des actifs

```
[Cliquer ➕ Ajouter des Actifs]
  ↓
Entrer: "AAPL, BTC-USD, VFV.TO"
  ↓
[Cliquer Ajouter]
  ↓
Voir messages:
  ✅ AAPL ajouté - Apple Inc. @ 148.50€
  ✅ BTC-USD ajouté - Bitcoin @ 46,500€
  ✅ VFV.TO ajouté - Vanguard S&P 500 @ 51.20€
```

### Étape 2: Ajouter position 1

```
[Cliquer 📊 Ajouter une Position]
  ↓
Sélectionner: AAPL
Quantité: 10
Prix Moyen: 143.50
Notes: Technologie core
  ↓
[Cliquer Ajouter]
  ↓
Dashboard met à jour:
  Total Investi: 1,435€
  Valeur Actuelle: 1,485€ (10 × 148.50€)
  Gain/Perte: +50€ (+3.5%)
```

### Étape 3: Ajouter position 2

```
[Cliquer 📊 Ajouter une Position]
  ↓
Sélectionner: BTC-USD
Quantité: 0.023
Prix Moyen: 45000
Notes: Allocation risquée
  ↓
[Cliquer Ajouter]
  ↓
Dashboard met à jour:
  Total Portefeuille: 10,000€
  Gain Total: +84.50€ (+0.85%)
```

### Résultat Final

```
Le dashboard affiche le portefeuille complet:
- 4 positions
- Gain de +450€ au total
- Vue d'ensemble complète
```

---

## États de Chargement

### Pendant le chargement:

```
⏳ Chargement des données...

⟳⟲⟳⟲⟳⟲ [Animation de rotation]

(Environ 2-3 secondes)
```

### Après succès:

```
✅ Dashboard chargé
📊 4 positions affichées
💹 Gain/Perte calculé
🏆 Top performer identifié
```

### En cas d'erreur:

```
❌ Impossible de se connecter à l'API. 
   Vérifiez que le backend est en cours d'exécution.

[Ouvrir http://localhost:8000/health pour diagnostiquer]
```

---

**Voilà ce que vous verrez en lançant l'application! 🎉**
