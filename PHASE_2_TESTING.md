# 🧪 Phase 2 - Testing Guide

## Quick Test (5 minutes)

### Setup
```bash
# Terminal 1: Backend
cd backend
python test_phase2.py

# Should show:
# ✅ API accessible
# ✅ Settings accessible
# ✅ Endpoint accessible
# ✅ All tests passed
```

### If tests fail

**"❌ API accessible"**
- Backend not running: `python main.py`
- Wrong port: Check PORT=8000

**"❌ Finnhub configuré"**
- Missing `.env` file
- `FINNHUB_API_KEY` not set
- Create `backend/.env`: `FINNHUB_API_KEY=your_key`

**"❌ Recommendations endpoint"**
- Check logs: `grep FINNHUB backend.log`
- Test Finnhub directly: `curl "http://localhost:8000/api/settings/test-finnhub"`

## Manual Testing (15 minutes)

### Step 1: Verify Backend

```bash
# Check Finnhub configuration
curl http://localhost:8000/api/settings
# Should return: {"finnhub_configured": true}

# Test Finnhub connection
curl http://localhost:8000/api/settings/test-finnhub
# Should return: {"success": true, "message": "Cle valide — AAPL: $..."}
```

### Step 2: Test Recommendations

```bash
# Get recommendations for Apple
curl "http://localhost:8000/api/news/recommendations?symbols=AAPL&hours=24"

# Should return JSON with:
# - recommendations array
# - count > 0
# - summary with buy/sell/hold counts

# Example response:
{
  "recommendations": [
    {
      "symbol": "AAPL",
      "title": "Apple Reports Strong Q4 Earnings",
      "sentiment_score": 0.65,
      "sentiment_label": "Positif 📈",
      "recommendation_type": "BUY 🟢",
      "confidence": 65,
      "in_portfolio": false,
      "url": "https://...",
      "published_at": "2024-01-15 10:30:00"
    }
  ],
  "count": 5,
  "summary": {
    "buy": 2,
    "sell": 1,
    "hold": 2,
    "monitor": 0
  }
}
```

### Step 3: Test Frontend Integration

```bash
# Terminal 1: Backend
cd backend && python main.py

# Terminal 2: Frontend
cd frontend && npm run dev

# Browser: http://localhost:3000
```

### Step 4: Add Portfolio

1. Click "➕ Ajouter des Actifs"
2. Add symbols: `AAPL`, `MSFT`, `GOOGL`
3. Click "📊 Ajouter une Position"
4. Add quantities and dates
5. Scroll down → See "📰 Actualités & Recommandations"

### Step 5: Verify Display

Expected output:
```
📰 Actualités & Recommandations

Summary cards:
  🟢 À acheter: 3
  🔴 À vendre: 1
  ⚪ À tenir: 4
  🟡 À surveiller: 2

Recommendations:
  🟢 BUY AAPL - Positif 📈 (75%)
    Titre: Apple beats on revenue
    Source: Reuters | ⏰ 2024-01-15
    [Lire l'article →]
```

## Component Testing

### NewsRecommendations.jsx Props

```jsx
// Props passed from parent
<NewsRecommendations 
  symbols={["AAPL", "MSFT", "GOOGL"]}
/>

// Component validates:
✅ symbols is array
✅ non-empty array
✅ calls API with correct params
✅ displays results
```

### API Integration Points

```javascript
// Frontend calls:
GET ${API_URL}/api/news/recommendations?symbols=AAPL,MSFT&hours=24

// Frontend expects:
{
  recommendations: Array,
  count: Number,
  summary: { buy, sell, hold, monitor }
}
```

## Edge Cases

### No recommendations
```bash
# Test with small cap that might not have news
curl "http://localhost:8000/api/news/recommendations?symbols=UNKNOWN&hours=24"

# Expected: count: 0, recommendations: []
# Frontend should show: "✨ Aucune actualité récente"
```

### Invalid symbols
```bash
curl "http://localhost:8000/api/news/recommendations?symbols=INVALID,NOTREAL"

# API should handle gracefully
# Frontend shows empty state with message
```

### Rate limiting
```bash
# Finnhub has free tier limits
# Multiple rapid calls might hit 429

# Expected in logs:
# ⚠️ Finnhub rate limit atteint pour SYMBOL
```

## Email Testing (Optional)

### Configuration
```env
# backend/.env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

### Test
```bash
# Test email configuration
curl -X POST "http://localhost:8000/api/news/test-email?email=test@example.com"

# Expected response:
{
  "status": "success",
  "message": "Email de test envoyé à test@example.com"
}
```

### Send Recommendations
```bash
curl -X POST "http://localhost:8000/api/news/send-recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "include_all": false
  }'
```

## Performance Testing

### Response Times

**Expected**:
- API response: 2-5 seconds
- Frontend rendering: < 1 second
- Total UI update: 3-6 seconds

**If slow**:
- Check Finnhub rate limit (logs)
- Check network latency
- Verify Finnhub API key validity

### Load Testing

```bash
# Test multiple symbols simultaneously
for symbol in AAPL MSFT GOOGL TSLA AMZN; do
  curl "http://localhost:8000/api/news/recommendations?symbols=$symbol" &
done
wait

# Should handle 5 parallel requests fine
```

## Debug Logging

### Enable Verbose Logging
```env
# backend/.env
DEBUG=True
LOG_LEVEL=DEBUG
```

### What to look for
```
[FINNHUB] - API calls to Finnhub
[NEWS] - Article processing
[SENTIMENT] - Sentiment analysis
[RECOMMENDATION] - Recommendation generation
[EMAIL] - Email sending
[ERROR] ❌ - Any errors
```

### Check logs
```bash
# From backend output
tail -f backend.log | grep "FINNHUB\|ERROR"

# Or direct in backend output when running:
python main.py 2>&1 | grep "\[FINNHUB\]"
```

## Validation Checklist

After Phase 2 implementation:

### Backend ✅
- [ ] `news_service.py` exists and imports without error
- [ ] `recommendation_engine.py` works (test sentiment analysis)
- [ ] `email_service.py` loads (email config optional)
- [ ] `routes_news.py` registered in main.py
- [ ] All endpoints respond (200 OK)
- [ ] Finnhub API key validated

### Frontend ✅
- [ ] `NewsRecommendations.jsx` imports without error
- [ ] Renders in dashboard when portfolio has holdings
- [ ] Shows summary cards with counts
- [ ] Lists recommendations with sentiment
- [ ] Links to articles work
- [ ] Refresh button works
- [ ] Loading state visible

### Integration ✅
- [ ] Backend + Frontend communicate
- [ ] Recommendations load on dashboard load
- [ ] Adding positions updates news
- [ ] Sentiment colors correct (green/red/gray)
- [ ] Emoji display correct (🟢🔴⚪🟡)
- [ ] Error handling graceful

### API ✅
- [ ] `/api/news/recommendations` works
- [ ] `/api/news/send-recommendations` accessible
- [ ] `/api/news/test-email` accessible
- [ ] Swagger docs `/docs` show all routes
- [ ] CORS enabled (frontend can call)

## Known Issues & Solutions

| Issue | Solution |
|-------|----------|
| "No module named 'routes_news'" | Check file path in backend/ |
| "Finnhub rate limit" | Wait 1 minute, limited API quota |
| "Email not sending" | Configure SMTP vars, not needed for Phase 2 |
| "Empty recommendations" | Some symbols may lack news, try AAPL/MSFT |
| "Slow initial load" | Normal (Finnhub API takes 2-5s) |

## Success Criteria

✅ Phase 2 is successful when:

1. Backend starts: `python main.py` ✅
2. Test passes: `python test_phase2.py` ✅
3. Frontend loads: http://localhost:3000 ✅
4. Dashboard shows "Actualités & Recommandations" ✅
5. Recommendations appear (1-5 seconds) ✅
6. Clicking article link works ✅
7. Refresh button updates recommendations ✅

## Troubleshooting Checklist

If something breaks:

1. **Backend crashes on start**
   - Check Python 3.12+
   - Check all imports work
   - Check `.env` file exists

2. **No recommendations in frontend**
   - Verify Finnhub API key
   - Check backend logs for [FINNHUB] tags
   - Test endpoint directly with curl

3. **Frontend shows error**
   - Check browser console (F12)
   - Check Network tab for failed requests
   - Verify API_URL is correct

4. **Performance issues**
   - Finnhub is slow? Expected (external API)
   - Check network bandwidth
   - Monitor CPU/RAM usage

## Next Steps

After successful testing:

1. ✅ Verify all endpoints work
2. ✅ Test with 5-10 different symbols
3. ✅ Test email (optional)
4. ✅ Check error handling
5. 📝 Document any issues
6. 🎉 Ready for Phase 3!

---

**Test Status**: Ready for manual verification
**Expected Result**: All 5 tests pass + UI displays recommendations
