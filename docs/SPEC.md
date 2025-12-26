# Technical Specification (SPEC)

**Project**: QuantStack  
**Version**: 2.1.0  
**Last Updated**: 2025-12-26

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │   Vercel    │  │   Next.js    │  │    Clerk Auth SDK       │ │
│  │   (Host)    │  │   14.2.25    │  │    (Conditional)        │ │
│  └─────────────┘  └──────────────┘  └─────────────────────────┘ │
│         │                │                      │                │
│         └────────────────┼──────────────────────┘                │
│                          │                                       │
│                    ┌─────▼─────┐                                │
│                    │  API_URL  │ (env var)                      │
│                    └─────┬─────┘                                │
└──────────────────────────┼──────────────────────────────────────┘
                           │ HTTP/JSON
┌──────────────────────────▼──────────────────────────────────────┐
│                         BACKEND                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │   Railway   │  │   FastAPI    │  │    In-Memory Cache      │ │
│  │   (Host)    │  │   Python     │  │    (30 min TTL)         │ │
│  └─────────────┘  └──────────────┘  └─────────────────────────┘ │
│         │                │                      │                │
│         │         ┌──────┴──────┐               │                │
│         │         │             │               │                │
│  ┌──────▼─────┐  ┌▼───────┐  ┌──▼─────┐  ┌─────▼────┐          │
│  │   Models   │  │ Routes │  │Services│  │  Data    │          │
│  │  (27)      │  │  (10)  │  │  (14)  │  │ Fetcher  │          │
│  └────────────┘  └────────┘  └────────┘  └─────┬────┘          │
└──────────────────────────────────────────────────┼──────────────┘
                                                   │
                    ┌──────────────────────────────┼───────────────┐
                    │        EXTERNAL APIS         │               │
                    │  ┌──────────────┐  ┌─────────▼─────────┐    │
                    │  │  SET Smart   │  │   Yahoo Finance   │    │
                    │  │  (Thai)      │  │   (US + Global)   │    │
                    │  └──────────────┘  └───────────────────┘    │
                    └──────────────────────────────────────────────┘
```

---

## System Layers & Responsibilities

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **Presentation** | `frontend/src/app/` | UI rendering, user interaction |
| **API Gateway** | `backend/app/api/routes/` | HTTP endpoints, request validation |
| **Business Logic** | `backend/app/models/` | Screening algorithms, signal generation |
| **Services** | `backend/app/services/` | Backtesting, PDF, reports |
| **Data Access** | `backend/app/data/` | Price/fundamental data fetching |
| **Config** | `backend/app/config.py` | Environment settings |

---

## Data Entities

### Core Entities

| Entity | Owner | Storage | Persistence |
|--------|-------|---------|-------------|
| **Stock Data** | Yahoo Finance | In-memory cache | 30 min TTL |
| **User Session** | Clerk | Clerk servers | Clerk-managed |
| **Model Results** | Backend | None | Request-scoped |
| **Backtest Results** | Backend | None | Request-scoped |
| **Custom Universe** | Backend | In-memory | Session only |

### Ownership Rules

1. **Stock data** - fetched on demand, cached 30 min
2. **User identity** - Clerk owns, we read via SDK
3. **Screening results** - ephemeral, not stored
4. **PDF reports** - generated on demand, not stored

---

## Auth Strategy

### Current Implementation

```
┌─────────────────────────────────────────────────┐
│               AUTH DECISION TREE                 │
├─────────────────────────────────────────────────┤
│                                                  │
│  1. Check: CLERK_PUBLISHABLE_KEY exists?         │
│     ├─ NO  → App runs WITHOUT auth               │
│     └─ YES → ClerkProvider wraps app             │
│                                                  │
│  2. Middleware checks path:                      │
│     ├─ /sign-in, /sign-up, / → Public            │
│     └─ /dashboard, /admin → Should be protected  │
│                                                  │
│  3. Admin check (current):                       │
│     └─ Hardcoded email list in admin/page.tsx    │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Session Model

| Aspect | Implementation |
|--------|---------------|
| **Session Storage** | Clerk-managed cookies |
| **Token Type** | JWT (Clerk) |
| **Refresh** | Automatic by Clerk SDK |
| **Logout** | Clerk's `signOut()` |

---

## Access Control Rules

| Route | Auth Required | Additional Check |
|-------|---------------|------------------|
| `/` | No | - |
| `/sign-in` | No | - |
| `/sign-up` | No | - |
| `/dashboard` | Conditional* | - |
| `/admin` | Yes | Email in admin list |
| `/api/*` | No | CORS only |

*Conditional = depends on Clerk keys being configured

---

## Auth Contract (DO NOT CHANGE)

> ⚠️ **These behaviors must remain stable:**

1. **App must work without Clerk keys** - conditional provider
2. **Admin emails** checked against hardcoded list
3. **Public routes**: `/`, `/sign-in`, `/sign-up`
4. **Clerk SDK** handles all session management
5. **No custom JWT logic** - rely on Clerk

---

## API Routes

### Models API (`/api/models/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all 27 models |
| POST | `/run` | Run model on universe |
| GET | `/run-quick/{id}` | Quick run with defaults |

### Universe API (`/api/universe/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List available universes |
| GET | `/{id}` | Get universe details |

### Backtest API (`/api/backtest/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/run` | Run VectorBT backtest |
| GET | `/results/{id}` | Get backtest results |

### Analysis API (`/api/analysis/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/stock/{ticker}` | Analyze single stock |
| GET | `/pdf/{ticker}` | Download PDF report |

### Status API (`/api/status/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/test-connection` | Connection test |
| GET | `/logs` | Recent error logs |

---

## Failure Assumptions

| Failure Mode | Expected Behavior |
|--------------|-------------------|
| Yahoo Finance rate limited | Retry with backoff, use cache |
| Yahoo Finance down | Return cached data if available |
| Clerk unavailable | App works in "no-auth" mode |
| Model returns no results | Display "no signals found" |
| Backtest timeout | Show error after 5 min |

---

## One-Source-of-Truth Rules

| Data | Source of Truth |
|------|-----------------|
| User identity | Clerk |
| Stock prices | Yahoo Finance |
| Model definitions | `backend/app/models/` |
| Universe lists | `backend/app/data/universe.py` |
| Frontend routes | `frontend/src/app/` folder structure |
| Environment config | `.env` files |
