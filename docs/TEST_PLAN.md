# Test Plan (TEST_PLAN)

**Project**: QuantStack  
**Version**: 2.1.0  
**Last Updated**: 2025-12-26

---

## Auth Smoke Test

### Test: Sign Up Flow

```
1. Open http://localhost:3000
2. Click "Get Started Free"
3. Should redirect to /sign-up
4. ✅ PASS: Clerk sign-up form renders
5. Enter email + password
6. ✅ PASS: Redirects to /dashboard after sign-up
```

### Test: Sign In Flow

```
1. Open http://localhost:3000/sign-in
2. ✅ PASS: Clerk sign-in form renders
3. Enter valid credentials
4. ✅ PASS: Redirects to /dashboard
5. ✅ PASS: Navbar shows user avatar
```

### Test: Sign Out Flow

```
1. While logged in, click user avatar
2. Click "Sign Out"
3. ✅ PASS: Redirects to /
4. ✅ PASS: Navbar shows "Sign In" button
```

### Test: Auth-less Mode

```
1. Remove CLERK_* env vars from .env.local
2. Restart frontend (npm run dev)
3. ✅ PASS: App loads without errors
4. ✅ PASS: Dashboard accessible
5. ✅ PASS: No auth prompts
```

---

## Core Flow Smoke Tests

### Test: Run Screening Model

```
1. Open /dashboard
2. Select universe: "S&P 50"
3. Select model: "CANSLIM"
4. Click "Run Model"
5. Wait for results (1-3 min)
6. ✅ PASS: Results table shows buy/sell signals
7. ✅ PASS: Each signal has ticker, score, price
```

### Test: Run Backtest

```
1. After running a model with results
2. Click "Run Backtest"
3. Set parameters (period: 1Y, capital: $10,000)
4. Click "Start Backtest"
5. Wait for results (30-60s)
6. ✅ PASS: Performance metrics display
7. ✅ PASS: Total return, Sharpe ratio, max drawdown shown
8. ✅ PASS: Trade list with P&L
```

### Test: Stock Analysis

```
1. Open /dashboard
2. Switch to "Analyze Stock" tab
3. Enter ticker: "AAPL"
4. Click "Analyze"
5. ✅ PASS: Stock data loads
6. ✅ PASS: Fundamental metrics display
7. ✅ PASS: Technical indicators display
8. ✅ PASS: Recommendation score shown
```

### Test: PDF Download

```
1. After analyzing a stock
2. Click "Download PDF"
3. ✅ PASS: PDF file downloads
4. ✅ PASS: PDF opens correctly
5. ✅ PASS: Contains stock analysis data
```

### Test: Pricing Toggle

```
1. Open http://localhost:3000
2. Scroll to pricing section
3. ✅ PASS: Default is "Yearly" selected
4. ✅ PASS: "2 MONTHS FREE" badge visible
5. Click toggle to "Monthly"
6. ✅ PASS: Pro price changes $41 → $49
7. ✅ PASS: Unlimited price changes $82 → $99
8. ✅ PASS: Badge disappears
```

### Test: Admin Dashboard

```
1. Open /admin
2. ✅ PASS: Admin dashboard loads
3. ✅ PASS: Users tab shows table
4. Click "Usage" tab
5. ✅ PASS: Usage logs display
6. Click "Analytics" tab
7. ✅ PASS: Model usage charts display
```

---

## Edge Cases to Verify

### Data Edge Cases

| Case | Test | Expected |
|------|------|----------|
| Invalid ticker | Analyze "XXXXX" | Error message, no crash |
| Empty universe | Run on empty custom universe | "No stocks" message |
| Thai stock | Analyze "PTT.BK" | Data loads (may be partial) |
| Rate limited | Run 10 models rapidly | Graceful slowdown |

### UI Edge Cases

| Case | Test | Expected |
|------|------|----------|
| Mobile viewport | Set width to 375px | Tables scroll horizontally |
| Long stock name | Stock with 50+ char name | Text truncates |
| No results | Model with 0 signals | "No signals found" message |
| Slow network | Throttle to 3G | Loading states show |

---

## Error Checks

### Console Errors to Watch For

```
❌ "Cannot read property of undefined"
❌ "Clerk: Missing Publishable Key" (in production)
❌ "CORS error"
❌ "Failed to fetch"
❌ "Unhandled Runtime Error"
```

### Network Errors to Watch For

```
❌ 500 Internal Server Error
❌ 502 Bad Gateway (Railway)
❌ 504 Gateway Timeout
❌ CORS preflight failures
```

---

## Pre-Deploy Checklist

### Before Deploying Frontend

- [ ] `npm run build` succeeds
- [ ] No TypeScript errors
- [ ] CLERK keys set in Vercel
- [ ] NEXT_PUBLIC_API_URL points to Railway
- [ ] All smoke tests pass

### Before Deploying Backend

- [ ] `python -c "from app.main import app"` works
- [ ] `/health` endpoint returns 200
- [ ] CORS_ORIGINS includes production frontend URL
- [ ] All API routes respond

---

## Must Pass Before Shipping

### P0 Gate: Blocking Release

- [ ] Landing page loads
- [ ] Pricing toggle works
- [ ] At least 1 model runs successfully
- [ ] Backtest completes without error
- [ ] PDF downloads work
- [ ] No console errors in production

### P1 Gate: Important but Not Blocking

- [ ] All 27 models return results
- [ ] Thai stocks load data
- [ ] Auth flow completes
- [ ] Admin dashboard loads
