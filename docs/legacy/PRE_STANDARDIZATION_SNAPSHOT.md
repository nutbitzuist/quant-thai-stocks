# Pre-Standardization Snapshot

**Tag**: `v2.1.0-pre-standardization`  
**Date**: 2025-12-26  
**Commit**: e88cc14

---

## Core Flows That Must Not Break

### Frontend (localhost:3000)

| # | Flow | URL | Pass Criteria |
|---|------|-----|---------------|
| 1 | Landing Page | `/` | Hero section renders, 27 models listed |
| 2 | Pricing Toggle | `/#pricing` | Monthly ↔ Yearly switch updates prices |
| 3 | Admin Dashboard | `/admin` | Users/Usage/Analytics tabs load |
| 4 | Dashboard | `/dashboard` | Stock screening UI loads |
| 5 | Sign In Page | `/sign-in` | Clerk sign-in form renders |
| 6 | Sign Up Page | `/sign-up` | Clerk sign-up form renders |

### Backend (Railway)

| # | Endpoint | Pass Criteria |
|---|----------|---------------|
| 1 | `/health` | Returns 200 OK |
| 2 | `/api/screen` | Accepts POST with model params |
| 3 | `/api/models` | Returns list of available models |

---

## Files Changed in This Version

- `frontend/src/app/components/LandingPage.tsx` - Pricing toggle
- `frontend/src/app/admin/page.tsx` - Admin dashboard (NEW)
- `frontend/src/app/components/Navbar.tsx` - Auth-aware nav
- `frontend/src/middleware.ts` - Route protection
- `frontend/src/app/layout.tsx` - ClerkProvider

---

## Restore Command

```bash
git checkout v2.1.0-pre-standardization
```
