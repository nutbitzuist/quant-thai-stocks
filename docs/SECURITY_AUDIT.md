# 🔒 SECURITY AUDIT REPORT — QuantStack

> **Audit Date**: December 26, 2024  
> **Scope**: Pre-monetization security review  
> **Status**: ⚠️ Multiple issues found — requires fixes before monetization

---

## Executive Summary

| Priority | Count | Status |
|----------|-------|--------|
| **P0 (CRITICAL)** | 3 | 🔴 Must fix before any users |
| **P1 (HIGH)** | 5 | 🟠 Should fix before monetization |
| **P2 (MEDIUM)** | 4 | 🟡 Nice to have |

---

## P0 — CRITICAL (Must Fix Before Any Users)

### 🔴 SEC-001: Backend Has Zero Authentication

**Risk Level**: CRITICAL  
**Category**: Authentication & Authorization

**Problem**: The entire FastAPI backend has no authentication. Any user (or attacker) can:
- Run expensive backtests consuming server resources
- Create/delete/modify custom universes for ALL users
- Clear server cache (`/debug/clear-cache`)
- View server errors (`/debug/errors`)
- Create/delete scheduled scans for ALL users

**Locations**:
- [main.py](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/main.py) — No auth middleware
- All routes in [routes/](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/api/routes/) — No auth checks

**Fix Required**:
```python
# Option 1: Add Clerk JWT verification middleware
# backend/app/middleware/auth.py

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
import httpx

security = HTTPBearer()

async def verify_clerk_token(request: Request):
    """Verify Clerk JWT token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authentication")
    
    token = auth_header.split(" ")[1]
    # Verify with Clerk's JWKS endpoint
    # See: https://clerk.com/docs/backend-requests/handling/manual-jwt
    ...

# Option 2: Simple API key for now
API_KEY = os.getenv("API_SECRET_KEY")

async def verify_api_key(request: Request):
    key = request.headers.get("X-API-Key")
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
```

**Apply to main.py**:
```python
from app.middleware.auth import verify_api_key

# Add to all routes that need protection
app.include_router(
    models.router, 
    prefix="/api/models", 
    dependencies=[Depends(verify_api_key)]
)
```

**Verification**: 
1. Call `curl http://localhost:8000/api/models/run` without auth → should get 401
2. Call with valid `X-API-Key` header → should work

---

### 🔴 SEC-002: Debug Endpoints Exposed in Production

**Risk Level**: CRITICAL  
**Category**: API Security

**Problem**: Debug endpoints are always exposed, leaking server internals:
- `GET /debug/errors` — Shows all recent data fetching errors
- `POST /debug/clear-cache` — Anyone can clear server cache (DoS)
- `GET /debug/test-fetch/{ticker}` — Exposes internal cache state

**Location**: [main.py:103-169](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/main.py#L103-L169)

**Fix Required**:
```python
# main.py - Only register debug endpoints in debug mode
if settings.debug:
    @app.get("/debug/errors")
    async def get_debug_errors():
        ...
    
    @app.post("/debug/clear-cache")  
    async def clear_cache():
        ...
    
    @app.get("/debug/test-fetch/{ticker}")
    async def test_fetch(ticker: str):
        ...
```

**Verification**: 
1. Set `DEBUG=false` in environment
2. Call `GET /debug/errors` → should get 404

---

### 🔴 SEC-003: CORS Allows Wildcard in Debug Mode

**Risk Level**: CRITICAL  
**Category**: API Security

**Problem**: When `DEBUG=true` (which is the default!), CORS allows `*` wildcard, enabling any website to make authenticated requests.

**Location**: [main.py:57](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/main.py#L57)
```python
cors_origins = settings.cors_origins if not settings.debug else settings.cors_origins + ["*"]
```

**Location**: [config.py:13](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/config.py#L13)
```python
debug: bool = os.getenv("DEBUG", "true").lower() == "true"  # DEFAULT IS TRUE!
```

**Fix Required**:
```python
# config.py - Change default to false
debug: bool = os.getenv("DEBUG", "false").lower() == "true"

# main.py - Never allow wildcard
cors_origins = settings.cors_origins  # Remove the wildcard addition
```

**Verification**:
1. Check `GET /health` response for `cors_origins`
2. Ensure `*` is not in the list

---

## P1 — HIGH (Fix Before Monetization)

### 🟠 SEC-004: No Data Ownership Enforcement

**Risk Level**: HIGH  
**Category**: Authorization

**Problem**: Custom universes and scheduled scans have no user ownership. Any user can:
- View/edit/delete ANY custom universe
- View/edit/delete ANY scheduled scan
They are stored globally without user association.

**Locations**:
- [custom_universe.py](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/api/routes/custom_universe.py) — No user ID in CRUD
- [scheduled_scans.py](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/api/routes/scheduled_scans.py) — File-based storage with no ACL

**Fix Required**:
```python
# Add user_id to all data models
class ScheduledScan(BaseModel):
    id: str
    user_id: str  # ADD THIS
    model_id: str
    ...

# Filter queries by user
@router.get("/")
async def list_scheduled_scans(user_id: str = Depends(get_current_user_id)):
    scans = [s for s in load_scans() if s['user_id'] == user_id]
    ...
```

**Verification**: 
1. Create scan as User A
2. Try to access scan as User B → should get 404

---

### 🟠 SEC-005: Admin Access Hardcoded

**Risk Level**: HIGH  
**Category**: Authorization

**Problem**: Admin emails are hardcoded in source code, and the admin check always passes for demo:

**Location**: [admin/page.tsx:7](file:///Users/nut/Downloads/quant-thai-stocks/frontend/src/app/admin/page.tsx#L7)
```typescript
const ADMIN_EMAILS = ['email.nutty@gmail.com'];
```

**Location**: [admin/page.tsx:49-66](file:///Users/nut/Downloads/quant-thai-stocks/frontend/src/app/admin/page.tsx#L49-L66)
```typescript
// Current code ALWAYS sets admin to true!
setIsAdmin(true);  // <-- BUG: Should verify against Clerk user
```

**Fix Required**:
```typescript
// admin/page.tsx
import { useUser } from '@clerk/nextjs';

export default function AdminPage() {
    const { user, isLoaded } = useUser();
    
    const ADMIN_EMAILS = (process.env.NEXT_PUBLIC_ADMIN_EMAILS || '').split(',');
    
    if (!isLoaded) return <Loading />;
    
    const isAdmin = user && ADMIN_EMAILS.includes(user.primaryEmailAddress?.emailAddress);
    
    if (!isAdmin) return <AccessDenied />;
    ...
}
```

**Verification**:
1. Log in as non-admin user
2. Navigate to `/admin` → should see "Access Denied"

---

### 🟠 SEC-006: No Rate Limiting

**Risk Level**: HIGH  
**Category**: API Security

**Problem**: No rate limiting on any endpoint. Attackers can:
- Brute force APIs
- DoS the server with expensive backtest requests
- Exhaust external API quotas (Yahoo Finance)

**Location**: [main.py](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/main.py) — No rate limit middleware

**Fix Required**:
```python
# Install: pip install slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to expensive endpoints
@router.post("/run")
@limiter.limit("10/minute")
async def run_backtest(request: Request, ...):
    ...
```

**Verification**:
1. Call backtest endpoint 11 times in 1 minute
2. 11th call should return 429 Too Many Requests

---

### 🟠 SEC-007: Detailed Error Messages Exposed

**Risk Level**: HIGH  
**Category**: API Security

**Problem**: Full exception details are returned to clients, leaking internal information:

**Location**: Multiple routes, e.g. [enhanced.py:254](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/api/routes/enhanced.py#L254)
```python
raise HTTPException(status_code=500, detail=str(e))  # Exposes internal error
```

**Fix Required**:
```python
# Log the real error, return generic message
except Exception as e:
    logger.error(f"Error combining signals: {e}", exc_info=True)
    raise HTTPException(
        status_code=500, 
        detail="An internal error occurred. Please try again later."
    )
```

**Verification**:
1. Trigger a 500 error
2. Response should NOT contain stack trace or internal details

---

### 🟠 SEC-008: No Input Validation on Ticker Parameter

**Risk Level**: HIGH  
**Category**: Input Validation

**Problem**: Ticker parameters are not validated. Attackers could:
- Pass extremely long strings (memory exhaustion)
- Pass special characters that break downstream systems
- Inject malicious data into file names (PDF exports)

**Locations**:
- [analysis.py:272](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/api/routes/analysis.py#L272)
- [main.py:125](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/main.py#L125)

**Fix Required**:
```python
import re
from fastapi import Path

TICKER_PATTERN = re.compile(r'^[A-Z0-9\.]{1,20}$')

def validate_ticker(ticker: str = Path(...)) -> str:
    ticker = ticker.upper().strip()
    if not TICKER_PATTERN.match(ticker):
        raise HTTPException(status_code=400, detail="Invalid ticker format")
    return ticker

@router.get("/{ticker}")
async def analyze_stock(ticker: str = Depends(validate_ticker)):
    ...
```

**Verification**:
1. Call `/api/analysis/'; DROP TABLE users; --` → should get 400
2. Call `/api/analysis/AAPL` → should work

---

## P2 — MEDIUM (Nice to Have)

### 🟡 SEC-009: Frontend Without Clerk Keys Bypasses All Auth

**Risk Level**: MEDIUM  
**Category**: Authentication

**Problem**: If Clerk keys are missing, the entire app runs without authentication:

**Location**: [middleware.ts:29](file:///Users/nut/Downloads/quant-thai-stocks/frontend/src/middleware.ts#L29)
```typescript
: simpleMiddleware;  // Just passes through everything
```

**Risk**: Accidental deployment without Clerk keys = all routes public.

**Fix Required**:
```typescript
// middleware.ts
if (!hasClerkKeys) {
    console.error("CRITICAL: Clerk keys not configured. Blocking all protected routes.");
    return NextResponse.redirect(new URL('/error?code=AUTH_NOT_CONFIGURED', request.url));
}
```

**Verification**: Remove Clerk keys, try to access `/dashboard` → should see error page

---

### 🟡 SEC-010: Secrets Not Rotated / No Expiry

**Risk Level**: MEDIUM  
**Category**: Secrets Management

**Problem**: No mechanism for rotating Clerk keys or API keys.

**Fix Required**:
1. Document key rotation procedure
2. Add key version support for graceful rotation
3. Consider using a secrets manager (AWS Secrets Manager, HashiCorp Vault)

---

### 🟡 SEC-011: Unpinned Dependency Versions

**Risk Level**: MEDIUM  
**Category**: Dependency Risks

**Problem**: Backend dependencies use `>=` constraints, not pinned versions:

**Location**: [requirements.txt](file:///Users/nut/Downloads/quant-thai-stocks/backend/requirements.txt)
```
fastapi>=0.109.0
yfinance>=0.2.36
...
```

**Risk**: A malicious or buggy update could be pulled automatically.

**Fix Required**:
```bash
# Generate lockfile
pip freeze > requirements.lock

# Use exact versions
fastapi==0.109.2
yfinance==0.2.36
```

---

### 🟡 SEC-012: File-Based Storage for Scheduled Scans

**Risk Level**: MEDIUM  
**Category**: Database Security

**Problem**: Scheduled scans stored in JSON file on disk, not database:

**Location**: [scheduled_scans.py:17](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/api/routes/scheduled_scans.py#L17)
```python
SCANS_FILE = os.path.join(..., "scheduled_scans.json")
```

**Risks**:
- No transactions / atomicity
- Data loss on server restart
- No backup/restore
- Path traversal if misconfigured

**Fix Required**: Migrate to PostgreSQL using existing database infrastructure.

---

## Summary of Required Actions

### Before ANY Users (P0):
1. ✅ Add authentication to backend APIs
2. ✅ Disable debug endpoints in production
3. ✅ Fix CORS configuration

### Before Monetization (P1):
4. Add user ownership to custom universes and scheduled scans
5. Fix admin access check to use actual Clerk user
6. Add rate limiting (especially on backtest endpoints)
7. Sanitize error messages
8. Validate ticker input format

### Nice to Have (P2):
9. Fail-safe when Clerk keys missing
10. Document secret rotation
11. Pin dependency versions
12. Migrate scheduled scans to database

---

## Verification Checklist

```bash
# After fixes, run these tests:

# 1. Auth check
curl http://localhost:8000/api/models/run -X POST → 401

# 2. Debug endpoints hidden
DEBUG=false python -m uvicorn app.main:app
curl http://localhost:8000/debug/errors → 404

# 3. CORS check
curl -H "Origin: http://evil.com" http://localhost:8000/health → No Access-Control-Allow-Origin

# 4. Rate limit check
for i in {1..15}; do curl -X POST http://localhost:8000/api/backtest/run; done
# Should see 429 after limit

# 5. Input validation
curl "http://localhost:8000/api/analysis/%3Cscript%3E" → 400

# 6. Admin access (as non-admin user)
# Navigate to /admin → Should see Access Denied
```

---

> [!CAUTION]
> **Do not monetize this application until P0 and P1 issues are resolved.**
> The current state allows anyone to access all data and consume unlimited server resources.
