# Product Requirements Document (PRD)

**Project**: QuantStack  
**Version**: 2.1.0  
**Last Updated**: 2025-12-26

---

## Product Definition

**QuantStack is a quantitative stock screening platform that enables retail traders to screen US and Thai stocks using 27 institutional-grade models like CANSLIM, Minervini, and Piotroski F-Score.**

---

## Target User Persona

| Attribute | Details |
|-----------|---------|
| **Who** | Active retail traders, self-directed investors |
| **Experience** | Intermediate - familiar with stock analysis concepts |
| **Markets** | US (S&P 500) and Thailand (SET100) |
| **Goal** | Find trading opportunities using proven institutional strategies |
| **Pain Point** | Don't have access to Bloomberg/FactSet-level screening tools |

---

## Core Problem Solved

Retail investors lack access to institutional-grade quantitative screening models. QuantStack democratizes these tools by providing:
- 27 pre-built screening models
- Backtesting capabilities
- PDF report generation
- Multiple market coverage (US + Thai)

---

## MVP Scope (Current State)

### ✅ What Currently Exists

| Feature | Status |
|---------|--------|
| 27 screening models (technical, fundamental, quantitative) | ✅ Working |
| S&P 500 + SET100 stock universes | ✅ Working |
| Run models and get buy/sell signals | ✅ Working |
| VectorBT backtesting | ✅ Working |
| PDF report generation | ✅ Working |
| Individual stock analysis | ✅ Working |
| Landing page with pricing | ✅ Working |
| Admin dashboard (mock data) | ✅ Working |
| Clerk authentication (conditional) | ✅ Working |

---

## Explicit Non-Goals

These are **intentionally** not in scope:

| Feature | Why Not |
|---------|---------|
| Real-time data | Yahoo Finance is 15-20min delayed; acceptable for screening |
| Portfolio tracking | Focus on screening, not portfolio management |
| Trade execution | No brokerage integration planned |
| Social features | Not a community platform |
| Mobile app | Web-first approach |
| Multi-language | English only for now |
| Custom model creation | Users use pre-built models only |

---

## Success Criteria

### Must Work (P0)

1. User can run any of 27 models on selected universe
2. Model returns buy/sell signals with scores
3. Backtest returns performance metrics
4. PDF report downloads successfully
5. Landing page displays and pricing toggle works

### Should Work (P1)

1. Auth flow completes (sign-up → dashboard)
2. Admin can view usage logs
3. All universes load correctly

---

## Primary User Flows

### Flow 1: Stock Screening

```
1. User lands on home page (/)
2. Clicks "Get Started Free" or "Dashboard"
3. Arrives at /dashboard
4. Selects universe (e.g., S&P 500)
5. Selects model (e.g., CANSLIM)
6. Clicks "Run Model"
7. Waits for results (1-3 min first time)
8. Views buy/sell signals with scores
9. (Optional) Downloads PDF report
```

### Flow 2: Backtesting

```
1. From dashboard, user has run results
2. Clicks "Run Backtest" on a model
3. Selects backtest parameters (period, capital)
4. Clicks "Start Backtest"
5. Views performance metrics (returns, Sharpe, drawdown)
6. Views trade list with P&L
```

### Flow 3: Individual Stock Analysis

```
1. User enters ticker in "Analyze Stock" tab
2. Clicks "Analyze"
3. Views fundamental + technical metrics
4. Views recommendation score
5. (Optional) Downloads analysis PDF
```

---

## Secondary Flows

### Sign Up

```
1. User clicks "Get Started Free"
2. Redirected to /sign-up (Clerk hosted)
3. Enters email + password (or OAuth)
4. Email verification (if configured)
5. Redirected to /dashboard
```

### Sign In

```
1. User clicks "Sign In"
2. Redirected to /sign-in (Clerk hosted)
3. Enters credentials
4. Redirected to /dashboard
```

### Sign Out

```
1. User clicks profile avatar
2. Clicks "Sign Out" in dropdown
3. Session ended, redirected to /
```

---

## Stability Assessment

### Stable (Low Change Risk)

- Model algorithms (well-tested)
- Data fetching layer
- PDF generation
- API route structure

### Likely to Change

- Admin dashboard (currently mock data)
- Pricing/billing integration
- Dashboard UI components (needs refactor)
- Auth middleware (as Clerk config solidifies)
