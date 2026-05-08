# 🧪 Quick Verification Checklist

## ✅ Before You Test

### Prerequisites
- [ ] Backend Python 3.12+
- [ ] Frontend Node.js 18+
- [ ] `FINNHUB_API_KEY` in `backend/.env`
- [ ] Port 3000 & 8000 available

## 🚀 Start Services

### Terminal 1: Backend
```bash
cd backend
python main.py

# Expected output:
# ✅ Routes news & recommandations chargées
# 🚀 Démarrage de l'API Investor AI...
# 📚 Docs disponibles à: http://localhost:8000/docs
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev

# Expected output:
# ▲ Next.js 14.2.35
# 📁 Local: http://localhost:3000
```

## 🎯 Test Checklist

### Part 1: Interface Loads
- [ ] Go to http://localhost:3000
- [ ] Dashboard loads without errors
- [ ] Scroll down to "📰 Actualités & Recommandations"
- [ ] See 4 colored cards (BUY/SELL/HOLD/MONITOR)

### Part 2: Email Configuration
- [ ] See email input field (gradient purple-pink)
- [ ] Input field is clickable
- [ ] Type an email: `test@example.com`
- [ ] Click "📧 Envoyer" button
- [ ] See message: ✅ or ❌ (depends on SMTP config)

### Part 3: Category Exploration
- [ ] Click on "🟢 À acheter: X" card
- [ ] Card changes color (darker shade)
- [ ] Modale pops up with investissements
- [ ] See list of symbols with confidence %
- [ ] Click on one symbol (e.g., "AAPL")
- [ ] See detailed view with:
  - [ ] Title of article
  - [ ] Summary text
  - [ ] Sentiment score
  - [ ] Source and date
  - [ ] "Lire l'article →" link
- [ ] Click "← Retour" button
- [ ] Back to category list
- [ ] Click "← Retour" again
- [ ] Back to main view with 4 cards

### Part 4: Refresh Button
- [ ] Click "🔄 Actualiser"
- [ ] See "⏳ Chargement..." message
- [ ] Wait 2-5 seconds
- [ ] Results update
- [ ] Cards refresh with new data

### Part 5: Browser Console
- [ ] Press F12 (or right-click → Inspect)
- [ ] Go to "Console" tab
- [ ] **No red errors** 🎯
- [ ] Warnings OK (in yellow)
- [ ] Check "Network" tab:
  - [ ] `GET /api/news/recommendations` = 200 ✅
  - [ ] `POST /api/news/send-recommendations` = 200 ✅

## 🔍 Debug Checks (If Issues)

### No Recommendations Appearing?
```bash
# Check Finnhub status
curl "http://localhost:8000/api/settings/test-finnhub"
# Should return: {"success": true, "message": "..."}

# Test debug endpoint
curl "http://localhost:8000/api/news/debug/symbols?symbols=AAPL,MSFT,GOOGL"
# Should show articles count per symbol
```

### Email Not Sending?
```bash
# Test email endpoint
curl -X POST "http://localhost:8000/api/news/test-email?email=test@example.com"

# Response:
# {"status": "success", "message": "..."}
# or
# {"status": "error", "message": "..."}
```

### Component Not Loading?
```bash
# Check frontend logs
# In Terminal 2, should see:
# ✅ Routes news & recommandations chargées (from backend)

# Browser console (F12):
# No import errors
# No "module not found"
```

## ✨ Success Criteria

✅ **All of these should be true:**

- [ ] Dashboard loads at http://localhost:3000
- [ ] "Actualités & Recommandations" section visible
- [ ] 4 category cards clickable and responsive
- [ ] Email input accepts text and sends
- [ ] Category modale opens when clicking cards
- [ ] Detail view shows article information
- [ ] "🔄 Actualiser" refreshes data
- [ ] No console errors (F12)
- [ ] Network requests succeed (200 status)
- [ ] "← Retour" buttons navigate correctly

## 📊 Expected Performance

- Initial page load: 2-3 seconds
- "🔄 Actualiser" click: 2-5 seconds (Finnhub delay)
- Modal open/close: < 300ms
- Category switching: < 100ms

## 🎓 What to Look For

### Good Signs ✅
- Smooth animations
- Cards respond to clicks
- Messages display
- Data refreshes
- No console errors

### Bad Signs ❌
- Page doesn't load
- Red errors in console
- Buttons don't respond
- Email always fails
- Infinite loading

## 🚨 Common Issues & Fixes

| Problem | Fix |
|---------|-----|
| "Cannot GET /api/news/recommendations" | Backend not running |
| No recommendations showing | Rate limit - wait 60s |
| Email button unresponsive | Browser console error? Check F12 |
| Cards don't click | Refresh page (Ctrl+R) |
| Modale doesn't open | Check console errors |

## 📝 Test Report Template

```markdown
# Phase 2 Improvements - Test Report

Date: [TODAY]
Tester: [YOUR NAME]

## Interface
- [ ] Loads correctly
- [ ] Email field visible
- [ ] 4 category cards visible
- [ ] Refresh button works

## Email
- [ ] Input accepts text
- [ ] Send button responsive
- [ ] Feedback message shows
- [ ] Email received (if SMTP configured)

## Categories
- [ ] Cards clickable
- [ ] Modale opens
- [ ] List shows investissements
- [ ] Detail view works

## Console
- [ ] No red errors
- [ ] No 404s
- [ ] Requests succeed

## Status
[ ] PASS
[ ] FAIL

## Notes
[Any issues found]
```

## 🎉 Final Check

Once everything works:
1. ✅ Take a screenshot of the new interface
2. ✅ Try the email (if SMTP configured)
3. ✅ Test with different symbols
4. ✅ Verify no console errors
5. ✅ Document any issues

---

**Ready?** Start the services and run through the checklist above!

**Issues?** Check `DIAGNOSTIC_RECOMMENDATIONS.md` or run the curl commands above.

**All Good?** You're ready for Phase 3! 🚀
