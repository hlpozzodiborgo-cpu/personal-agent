# 🔍 Diagnostic: Recommandations Limitées

## Symptôme
Seul AAPL et AMA apparaissent dans les recommandations, même avec d'autres investissements dans le portefeuille.

## Causes Possibles

### 1. **Portefeuille ne contient que 2 holdings**
- Vérifiez dans le dashboard: "Mes Positions"
- Si seul AAPL et AMA sont listés, c'est normal!
- Solution: Ajouter plus de positions via "📊 Ajouter une Position"

### 2. **Finnhub Rate Limit** (Plus probable)
- Finnhub a un rate limit bas sur le plan gratuit
- Après ~60 requêtes/minute, refuse les requêtes
- Les requêtes échouent silencieusement = 0 actualité

### 3. **API Key invalide**
- Clé expirant ou invalide
- Vérifier: `GET /api/settings/test-finnhub`

### 4. **Symboles mal formatés**
- Espace dans les symboles
- Minuscules au lieu de majuscules

## Étapes de Diagnostic

### Étape 1: Vérifier les holdings du portefeuille
```bash
# Accéder à http://localhost:3000
# Section "Mes Positions"
# Notez tous les symboles affichés
```

### Étape 2: Tester Finnhub API directement
```bash
curl "http://localhost:8000/api/settings/test-finnhub"

# Réponse positive:
# {"success": true, "message": "Cle valide — AAPL: $..."}

# Réponse négative:
# {"success": false, "message": "Cle invalide ou limite atteinte"}
```

### Étape 3: Tester actualités par symbole
```bash
# Remplacer X,Y,Z par vos symboles
curl "http://localhost:8000/api/news/debug/symbols?symbols=AAPL,MSFT,GOOGL"

# Réponse montrera le nombre d'actualités par symbole
# Exemple:
{
  "symbols_tested": ["AAPL", "MSFT", "GOOGL"],
  "results": {
    "AAPL": {"status": "ok", "articles_count": 5, ...},
    "MSFT": {"status": "ok", "articles_count": 3, ...},
    "GOOGL": {"status": "error", "error": "429 Too Many Requests"}
  }
}
```

### Étape 4: Tester les recommandations complètes
```bash
# Remplacer X,Y,Z par vos symboles
curl "http://localhost:8000/api/news/recommendations?symbols=AAPL,MSFT,GOOGL&hours=24"

# Compte le nombre de recommandations par type
```

## Solutions

### Solution 1: Rate Limit (Plus probable)
**Symptôme**: Après AAPL et AMA, les autres symboles retournent 0 articles

**Fix**: 
- Attendre 1 minute (reset du limit Finnhub)
- Réessayer via "🔄 Actualiser"
- Ajouter caching en Phase 3 pour éviter

```bash
# Vérifier le rate limit dans les logs backend
# Cherchez: "Finnhub rate limit atteint"
```

### Solution 2: Moins de Symboles
- Limiter à 3-5 symboles max pour éviter rate limit
- OU attendre avant de faire requête suivante

### Solution 3: Vérifier le Portefeuille
```bash
# Ajouter plus de holdings
1. Dashboard → "➕ Ajouter des Actifs"
2. Ajouter: MSFT, GOOGL, TSLA, etc.
3. "📊 Ajouter une Position"
4. Entrer quantité et date
```

### Solution 4: Clé Finnhub
```env
# backend/.env
FINNHUB_API_KEY=your_actual_key_here

# Vérifier:
curl "http://localhost:8000/api/settings/test-finnhub"
# Doit retourner {"success": true, ...}
```

## Logs à Vérifier

Dans le terminal backend, cherchez:

```
✅ {N} actualités trouvées pour SYMBOL
❌ Finnhub rate limit atteint pour SYMBOL
⚠️ Erreur Finnhub {status} pour SYMBOL
```

## Test Complet

Suivez cette procédure:

```bash
# 1. Terminal 1: Start backend
cd backend
python main.py

# 2. Terminal 2: Run diagnostic
python test_phase2.py
# Should show all 5 tests pass

# 3. Terminal 3: Test debugging endpoint
curl "http://localhost:8000/api/news/debug/symbols?symbols=AAPL,MSFT,GOOGL,TSLA,AMZN"
# Will show articles per symbol

# 4. Check logs in Terminal 1
# Look for rate limit errors

# 5. If rate limit:
# Wait 60 seconds
# Click "🔄 Actualiser" on dashboard
# Recommendations should appear
```

## Workaround Temporaire

Si rate limit persiste:

**Réduire les symboles**:
```jsx
// Dans frontend/app/page.jsx
// Limiter à 3 symboles max:
<NewsRecommendations 
  symbols={(portfolio.holdings?.map(h => h.symbol) || []).slice(0, 3)}
/>
```

**Ajouter délai**:
```javascript
// Dans components/NewsRecommendations.jsx
// Attendre avant fetch:
useEffect(() => {
  const timer = setTimeout(() => {
    if (symbols.length === 0) return;
    fetchRecommendations();
  }, 2000); // Attendre 2 secondes
  
  return () => clearTimeout(timer);
}, [symbols]);
```

## Phase 2+ Fixes

Pour Phase 2+:
1. ✅ Ajouter caching (10min TTL)
2. ✅ Rate limit aware
3. ✅ Background job pour préremplir cache
4. ✅ Queue system avec délais

## Questions Fréquentes

**Q: Pourquoi seulement 2 symboles?**
A: Probablement Finnhub rate limit. Test avec `debug/symbols` endpoint.

**Q: Comment vérifier ma clé Finnhub?**
A: `curl "http://localhost:8000/api/settings/test-finnhub"`

**Q: Combien de symboles max?**
A: Sans caching: 3-5 max. Avec caching: Illimité (Phase 3).

**Q: Comment ça fonctionne en production?**
A: Phase 3 ajoutera caching + background jobs pour éviter rate limit.

## Checklist de Résolution

- [ ] Vérifier holdings dans le portefeuille
- [ ] Tester endpoint `/api/settings/test-finnhub`
- [ ] Tester endpoint `/api/news/debug/symbols?symbols=X,Y,Z`
- [ ] Vérifier logs backend pour "rate limit"
- [ ] Attendre 60 secondes si rate limit
- [ ] Cliquer "🔄 Actualiser"
- [ ] Recommandations devraient apparaître ✅

---

**Besoin d'aide?** Contactez le support avec sortie de:
```bash
# Terminal backend output
python main.py 2>&1 | grep "FINNHUB\|rate\|ERROR"

# Debug endpoint
curl "http://localhost:8000/api/news/debug/symbols?symbols=AAPL,MSFT"
```
