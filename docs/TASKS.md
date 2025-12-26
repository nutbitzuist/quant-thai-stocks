# Task Tracker (TASKS)

**Project**: QuantStack  
**Version**: 2.1.0  
**Last Updated**: 2025-12-26

---

## Legend

- `[x]` Completed
- `[ ]` Not started
- `[/]` In progress
- `P0` = Must have (blocks launch)
- `P1` = Should have (important)
- `P2` = Nice to have (future)

---

## ✅ Features Completed

### Core Functionality
- [x] **P0** 27 screening models (11 technical, 13 fundamental, 4 quantitative)
- [x] **P0** Model execution with buy/sell signals
- [x] **P0** Multiple universes (S&P 500, SET100, etc.)
- [x] **P0** VectorBT backtesting integration
- [x] **P0** Individual stock analysis
- [x] **P0** PDF report generation
- [x] **P0** QuantStats performance reports

### Frontend
- [x] **P0** Dashboard with model selection
- [x] **P0** Results display with signal table
- [x] **P0** Backtest results visualization
- [x] **P1** Landing page with hero section
- [x] **P1** Pricing section with toggle
- [x] **P1** Neo-Brutalist UI design
- [x] **P1** Admin dashboard (mock data)

### Auth & Infrastructure
- [x] **P1** Clerk authentication (conditional)
- [x] **P1** Sign-in / Sign-up pages
- [x] **P1** Navbar with auth state
- [x] **P0** Vercel deployment (frontend)
- [x] **P0** Railway deployment (backend)

---

## 🐛 Known Bugs & Issues

### P0 - Critical
- [ ] **Dashboard monolith** - 4,153 lines in single file, causes slow edits
- [ ] **No error boundaries** - React crashes show blank screen

### P1 - Important
- [ ] **Admin mock data only** - No real user/usage data
- [ ] **Middleware not enforcing auth** - Dashboard accessible without login
- [ ] **Thai stock data inconsistent** - SET Smart API sometimes fails
- [ ] **PDF generation slow** - 10-20s for complex reports

### P2 - Minor
- [ ] **Console warnings** - React key warnings in some lists
- [ ] **Mobile responsiveness** - Some tables overflow on mobile
- [ ] **Backtest timeout** - No progress indicator for long backtests

---

## 🚧 Missing for Production

### Database & Persistence (P0)
- [ ] Add database (Supabase/Postgres)
- [ ] User preferences storage
- [ ] Custom universe persistence
- [ ] Usage logging for billing

### Auth Hardening (P0)
- [ ] Enforce auth on /dashboard route
- [ ] Move admin emails to database
- [ ] Add user roles (admin, pro, free)
- [ ] Rate limiting per user

### Payments (P1)
- [ ] Stripe integration
- [ ] Subscription management
- [ ] Usage metering (scan counts)
- [ ] Billing portal

### Monitoring (P1)
- [ ] Error tracking (Sentry)
- [ ] Analytics (Posthog/Mixpanel)
- [ ] Uptime monitoring
- [ ] Performance monitoring

---

## 🔧 Technical Debt

### P0 - Must Fix Soon
- [ ] **Extract dashboard components** - Break up 4,153-line file
  - [ ] Extract TypeScript interfaces to `types/`
  - [ ] Extract hooks to `hooks/`
  - [ ] Extract components to `components/`
  - [ ] Extract styles to CSS modules
- [ ] **Add React error boundaries** - Catch rendering errors
- [ ] **Consolidate 20+ markdown docs** - Into structured /docs folder

### P1 - Should Fix
- [ ] **Remove inline styles** - Move to CSS modules
- [ ] **Add loading states** - Skeleton loaders for async ops
- [ ] **Improve error messages** - User-friendly error display
- [ ] **Add TypeScript strict mode** - Catch more bugs

### P2 - Nice to Fix
- [ ] **Add ESLint/Prettier** - Code consistency
- [ ] **Add Husky pre-commit hooks** - Prevent bad commits
- [ ] **Add CI/CD pipeline** - Automated testing/deploy

---

## 🔒 Hardening Tasks

### Security
- [ ] **P0** Audit CORS settings for production
- [ ] **P0** Validate all API inputs (Pydantic)
- [ ] **P1** Add rate limiting to API
- [ ] **P1** Add request logging
- [ ] **P2** Security headers (CSP, HSTS)

### Reliability
- [ ] **P0** Add health check endpoint monitoring
- [ ] **P1** Implement retry logic for Yahoo Finance
- [ ] **P1** Add circuit breaker for external APIs
- [ ] **P2** Graceful degradation when APIs fail

### Performance
- [ ] **P1** Add Redis cache (replace in-memory)
- [ ] **P1** Lazy load dashboard components
- [ ] **P2** Add service worker for offline
- [ ] **P2** Image optimization

---

## 📋 Pre-Launch Checklist

- [ ] All P0 bugs fixed
- [ ] Database connected
- [ ] Auth enforced on protected routes
- [ ] Stripe integration working
- [ ] Error tracking enabled
- [ ] SSL certificates valid
- [ ] Environment variables set
- [ ] Backup strategy defined
