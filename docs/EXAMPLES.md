# 📚 Exemples d'Utilisation - Investor AI

## Cas d'Usage 1: Suivre un Portfolio Diversifié

### Scénario
Vous avez épargnéet vous avez un
- 5,000€ en AAPL (35 actions à ~142€)
- 2,000€ en VTI (ETF marché US, ~40 actions à 50€)
- 1,000€ en BTC (Bitcoin, ~0.023 BTC à ~45,000€)
- 2,000€ en EUR=X (devises, protection)

### Étapes d'implémentation

**1. Démarrer l'application**
```bash
# Terminal 1
cd backend
source venv/bin/activate
python main.py

# Terminal 2
cd frontend
npm run dev
```

**2. Ajouter les actifs**
- Ouvrir http://localhost:3000
- Cliquer "➕ Ajouter des Actifs"
- Entrer: `AAPL, VTI, BTC-USD, EUR=X`

**3. Ajouter les positions**
- Cliquer "📊 Ajouter une Position" pour chaque actif:

| Actif | Quantité | Prix Moyen | Notes |
|-------|----------|-----------|-------|
| AAPL | 35 | 142.86 | Technologie core |
| VTI | 40 | 50 | Large-cap diversifié |
| BTC-USD | 0.023 | 45000 | Allocation risquée |
| EUR=X | 2000 | 1 | Hedge devise |

**4. Suivre la performance**
- Le dashboard affiche automatiquement:
  - Valeur total: 10,000€
  - Valeur actuelle: (dépend des prix en temps réel)
  - Gain/Perte en € et %
  - Meilleur et pire performer

### Exemple de rendu

```
Total Investi: 10,000€
Valeur Actuelle: 10,450€
Gain/Perte: +450€ (+4.5%)
Positions: 4

AAPL     | 35 | 142.86€ | 148.50€ | 5,110€ | 5,197.50€ | +87.50€ (+1.7%)
VTI      | 40 | 50€     | 51.20€  | 2,000€ | 2,048€    | +48€ (+2.4%)
BTC-USD  | 0.023 | 45K€ | 46.5K€  | 1,035€ | 1,069.50€ | +34.50€ (+3.3%)
EUR=X    | 2000 | 1€    | 1€      | 2,000€ | 2,000€    | 0€ (0%)

🚀 Meilleur: BTC-USD +3.3%
📉 Moins bon: EUR=X 0%
```

---

## Cas d'Usage 2: Reconstitution de Portfolio Après Krach

### Scénario
Vous aviez un portfolio qui a chuté pendant la crise. Vous voulez reconstruire progressivement.

### Avantages de Investor AI

1. **Suivi des points d'entrée:**
   ```
   - Première position: AAPL @ 120€ (-15%)
   - Deuxième position: AAPL @ 125€ (-10%)
   - Troisième position: AAPL @ 130€ (-5%)
   ```
   Le système calcule automatiquement votre prix moyen d'achat.

2. **Visualiser la récupération:**
   - Avant: -30% global
   - Après 3 mois +15% global
   - Tendance positive=confiance

3. **Savoir quand réinvestir:**
   - Dashboard affiche le gain/perte
   - Préparez-vous pour Phase 3 (IA recommandations)

---

## Cas d'Usage 3: Gestion de Plusieurs Devises

### Scénario
Vous êtes en Suisse (CHF) mais investissez en actions US (USD) et EU (EUR)

### Mise en place

**Actifs à ajouter:**
- `USD=X` - Taux EUR/USD
- `CHF=X` - Taux EUR/CHF
- Actions US: `AAPL`, `MSFT`
- Actions EU: `SAP`, `ASML`

**Positions:**
```
AAPL   | 10 | 147.50€ (100 USD) | Technologie
MSFT   | 5  | 402€ (300 USD)    | Technologie
SAP    | 15 | 85€               | Enterprise EU
ASML   | 8  | 615€              | Semiconductors EU
USD=X  | 1  | 0.92 (1 USD→0.92€)| Hedge devise USD
```

**Avantages:**
- Suivi des pertes/gains de change
- Identifier si le USD se renforce (affecte les US stocks)
- Portfolio automatiquement pondéré par devise

---

## Cas d'Usage 4: Suivi des Cryptos et Actifs Alternatifs

### Scénario
Vous avez une allocation 80/20: 80% actifs traditionnels, 20% crypto

### Configuration

**Phase 1: Suivi basique**
```
Actifs traditionnels: AAPL, VFV, XIC (80%)
├─ AAPL: 3,000€
├─ VFV (S&P500): 2,000€
└─ XIC (Canada): 1,000€

Cryptos (20%):
├─ BTC-USD: 500€
├─ ETH-USD: 500€
└─ DOGE-USD: 100€
```

**Rendus du dashboard:**
```
Secteur | Allocation | Performance
Stocks | 80% | +5.2%
Crypto | 20% | +12.3%
Global | 100% | +6.1%

Les cryptos tirent vers le haut!
```

**Phase 2: Avec actualités (à venir)**
- Voir les actualités crypto: "Bitcoin touche $50K"
- Évaluer l'impact sur votre allocation

**Phase 3: Recommandations IA (à venir)**
- "Augmentez allocation crypto à 25% selon les tendances"
- "Rebalancer si crypto > 30% (risque)"

---

## API Usage - Scripts Python

### Script 1: Exporter le Portfolio

```python
import requests
import json
from datetime import datetime

# Récupérer le portfolio
response = requests.get('http://localhost:8000/api/portfolio')
portfolio = response.json()

# Exporter en JSON
export = {
    'exported_at': datetime.now().isoformat(),
    'summary': portfolio['stats'],
    'holdings': portfolio['holdings'],
    'performers': {
        'top_gainer': portfolio['top_gainer'],
        'top_loser': portfolio['top_loser']
    }
}

with open('portfolio_export.json', 'w') as f:
    json.dump(export, f, indent=2)

print("✅ Portfolio exporté en portfolio_export.json")
```

### Script 2: Ajouter des Actifs en Batch

```python
import requests

BASE_URL = 'http://localhost:8000/api'

# Liste d'actifs à ajouter
assets = [
    ('AAPL', 'Apple Inc.', 'stock'),
    ('GOOGL', 'Alphabet Inc.', 'stock'),
    ('MSFT', 'Microsoft', 'stock'),
    ('BTC-USD', 'Bitcoin', 'crypto'),
    ('ETH-USD', 'Ethereum', 'crypto'),
    ('VFV.TO', 'US Index', 'etf'),
]

for symbol, name, asset_type in assets:
    try:
        response = requests.post(
            f'{BASE_URL}/assets/add',
            params={
                'symbol': symbol,
                'name': name,
                'asset_type': asset_type
            }
        )
        if response.status_code == 200:
            print(f"✅ {symbol} ajouté")
        else:
            print(f"❌ {symbol} erreur: {response.text}")
    except Exception as e:
        print(f"❌ {symbol} erreur: {e}")
```

### Script 3: Monitorer le Portfolio Toutes les Heures

```python
import requests
import schedule
import time
from datetime import datetime

BASE_URL = 'http://localhost:8000/api'

def check_portfolio():
    try:
        response = requests.get(f'{BASE_URL}/portfolio')
        portfolio = response.json()
        
        stats = portfolio['stats']
        print(f"\n[{datetime.now()}] Portfolio Update")
        print(f"  Total: {stats['total_current_value']:.2f}€")
        print(f"  Gain/Perte: {stats['total_gain_loss']:.2f}€ ({stats['gain_loss_percent']:.2f}%)")
        
        # Vérifier si gain/perte dépasse 5%
        if abs(stats['gain_loss_percent']) > 5:
            print(f"  ⚠️  ALERTE: Mouvement significatif!")
        
    except Exception as e:
        print(f"Erreur: {e}")

# Programmer la vérification toutes les heures
schedule.every(1).hours.do(check_portfolio)

print("📊 Monitoring du portfolio lancé...")
while True:
    schedule.run_pending()
    time.sleep(60)
```

### Script 4: Analyser la Diversification

```python
import requests
from collections import defaultdict

BASE_URL = 'http://localhost:8000/api'

def analyze_diversification():
    response = requests.get(f'{BASE_URL}/portfolio')
    portfolio = response.json()
    
    # Grouper par type
    types = defaultdict(float)
    for holding in portfolio['holdings']:
        # Vous auriez besoin du type dans la réponse
        # Pour l'instant, supputer par symbole
        if 'BTC' in holding['symbol'] or 'ETH' in holding['symbol']:
            asset_type = 'Crypto'
        else:
            asset_type = 'Stock'
        
        types[asset_type] += holding['current_value']
    
    total = sum(types.values())
    
    print("\n📊 Analyse de Diversification")
    print("=" * 40)
    for asset_type, value in sorted(types.items(), key=lambda x: -x[1]):
        percent = (value / total * 100) if total > 0 else 0
        print(f"{asset_type:15} | {value:10.2f}€ | {percent:5.1f}%")
    
    print("=" * 40)
    print(f"{'Total':15} | {total:10.2f}€ | {100.0:5.1f}%")
```

---

## Frontend Usage - JavaScript

### Exemple 1: Fetcher les données en React

```jsx
'use client'

import { useEffect, useState } from 'react'
import { getPortfolio } from '@/lib/api'

export function PortfolioWidget() {
  const [portfolio, setPortfolio] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadPortfolio = async () => {
      try {
        const res = await getPortfolio()
        setPortfolio(res.data)
      } catch (error) {
        console.error("Erreur:", error)
      } finally {
        setLoading(false)
      }
    }

    loadPortfolio()
    // Rafraîchir toutes les 5 minutes
    const interval = setInterval(loadPortfolio, 5 * 60 * 1000)
    
    return () => clearInterval(interval)
  }, [])

  if (loading) return <div>Chargement...</div>
  if (!portfolio) return <div>Erreur</div>

  const stats = portfolio.stats
  return (
    <div>
      <h2>💰 Portfolio</h2>
      <p>Valeur: {stats.total_current_value.toFixed(2)}€</p>
      <p>Gain: {stats.total_gain_loss.toFixed(2)}€ ({stats.gain_loss_percent.toFixed(2)}%)</p>
    </div>
  )
}
```

---

## Debug - Checklist de Troubleshooting

### Problème: API ne répond pas

```bash
# Vérifier que le backend tourne
curl http://localhost:8000/health

# Vérifier les logs
cd backend && python main.py

# Vérifier le port
lsof -i :8000

# Tuer le processus si bloqué
kill -9 $(lsof -t -i :8000)
```

### Problème: Les prix ne se mettent pas à jour

```bash
# Vérifier que Yahoo Finance fonctionne
curl "https://query1.finance.yahoo.com/v8/finance/chart/AAPL"

# Vérifier votre connexion internet
ping 8.8.8.8
```

### Problème: Frontend ne se connecte pas à l'API

```javascript
// Vérifier .env.local dans le frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000"

// Vérifier CORS
curl -H "Origin: http://localhost:3000" \
  -X OPTIONS \
  http://localhost:8000/health
```

---

**Happy investing! 🚀📊**
