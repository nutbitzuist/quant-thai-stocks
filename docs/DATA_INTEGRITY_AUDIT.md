# 🗃️ DATA INTEGRITY AUDIT — QuantStack

> **Audit Date**: December 26, 2024  
> **Scope**: Data ownership, validation, persistence, destructive actions, sensitive data  
> **Status**: ⚠️ Critical data isolation issues found

---

## Executive Summary

| Priority | Count | Status |
|----------|-------|--------|
| **P0 (CRITICAL)** | 3 | 🔴 Must fix before any users |
| **P1 (HIGH)** | 4 | 🟠 Should fix before monetization |
| **P2 (MEDIUM)** | 3 | 🟡 Nice to have |

---

## 1. DATA OWNERSHIP

### Current State: 🔴 BROKEN

**Problem**: All user-generated data is globally shared. There is NO data isolation between users.

### Ownership Matrix

| Data Type | Storage | Has user_id Field | Ownership Enforced? |
|-----------|---------|-------------------|---------------------|
| Custom Universes | In-memory singleton | ❌ No | ❌ No |
| Scheduled Scans | JSON file | ❌ No | ❌ No |
| Run History | In-memory singleton | ❌ No | ❌ No |
| Usage Logs | PostgreSQL | ✅ Yes (nullable) | ❌ Not passed |
| Backtest Results | PostgreSQL | ✅ Yes (nullable) | ❌ Not passed |

### Evidence

**Custom Universes** — [services/custom_universe.py:33-35](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/services/custom_universe.py#L33-L35)
```python
def __init__(self):
    self._universes: Dict[str, CustomUniverse] = {}  # Global dict, no user_id
    self._load_examples()
```

**Scheduled Scans** — [routes/scheduled_scans.py:17](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/api/routes/scheduled_scans.py#L17)
```python
SCANS_FILE = os.path.join(..., "scheduled_scans.json")  # Single global file
```

**Run History** — [services/history.py:40-41](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/services/history.py#L40-L41)
```python
def __init__(self, max_records: int = 100):
    self._history: List[RunRecord] = []  # Global list, no user_id
```

### All Data Access Queries/Actions

| Endpoint | Action | User Filter? | CRITICAL? |
|----------|--------|--------------|-----------|
| `GET /api/custom-universe/` | List all universes | ❌ No | ✅ Yes |
| `GET /api/custom-universe/{id}` | Get any universe | ❌ No | ✅ Yes |
| `PUT /api/custom-universe/{id}` | Update any universe | ❌ No | ✅ Yes |
| `DELETE /api/custom-universe/{id}` | Delete any universe | ❌ No | ✅ Yes |
| `GET /api/scheduled-scans/` | List all scans | ❌ No | ✅ Yes |
| `GET /api/scheduled-scans/{id}` | Get any scan | ❌ No | ✅ Yes |
| `PUT /api/scheduled-scans/{id}/toggle` | Toggle any scan | ❌ No | ✅ Yes |
| `DELETE /api/scheduled-scans/{id}` | Delete any scan | ❌ No | ✅ Yes |
| `POST /api/scheduled-scans/{id}/run` | Run any scan | ❌ No | ⚠️ Medium |
| `GET /api/models/history` | List all run history | ❌ No | ⚠️ Medium |
| `GET /api/models/history/{id}` | Get any run details | ❌ No | ⚠️ Medium |
| `DELETE /api/models/history` | Clear ALL history | ❌ No | ✅ Yes |

---

## 2. DATA VALIDATION

### What IS Validated ✅

| Input | Validation | Location |
|-------|------------|----------|
| `model_id` | Checked against `ALL_MODELS` dict | [models.py:169](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/api/routes/models.py#L169) |
| `universe` | Checked against known universes | [models.py:186](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/api/routes/models.py#L186) |
| Pydantic models | Basic type validation | All request models |
| Ticker text parsing | Length check `<= 10` chars | [custom_universe.py:197](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/services/custom_universe.py#L197) |

### What is NOT Validated ❌

| Input | Risk | Validation Needed |
|-------|------|-------------------|
| `ticker` path parameter | Injection, DoS | `^[A-Z0-9\.]{1,20}$` regex |
| `name` for universes | XSS in exports | Alphanumeric + spaces, max 100 chars |
| `description` for universes | XSS in exports | Sanitize HTML, max 500 chars |
| `schedule_time` for scans | Invalid format | `^[0-2][0-9]:[0-5][0-9]$` regex |
| `days` array for scans | Invalid day names | Enum: `['Mon','Tue','Wed','Thu','Fri','Sat','Sun']` |
| `parameters` dict | Arbitrary code execution | Whitelist allowed keys per model |
| `top_n`, `limit` | DoS via large values | Max 100 |
| `n_simulations` for Monte Carlo | DoS via large values | Max 10000 |

### Validation Rules Needed

```python
# backend/app/validation.py
import re
from pydantic import validator, Field

# Ticker validation
TICKER_REGEX = re.compile(r'^[A-Z0-9\.]{1,20}$')

def validate_ticker(ticker: str) -> str:
    ticker = ticker.upper().strip()
    if not TICKER_REGEX.match(ticker):
        raise ValueError("Invalid ticker format")
    return ticker

# Name validation for universes/scans
def validate_name(name: str) -> str:
    name = name.strip()
    if len(name) < 1 or len(name) > 100:
        raise ValueError("Name must be 1-100 characters")
    if not re.match(r'^[\w\s\-\.]+$', name):
        raise ValueError("Name contains invalid characters")
    return name

# Schedule time validation
def validate_schedule_time(time: str) -> str:
    if not re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', time):
        raise ValueError("Time must be HH:MM format")
    return time

# Days validation
VALID_DAYS = {'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'}
def validate_days(days: List[str]) -> List[str]:
    if not days or not all(d in VALID_DAYS for d in days):
        raise ValueError("Invalid day names")
    return days
```

---

## 3. DATA PERSISTENCE

### Current State: 🟠 HIGH RISK

### Persistence Matrix

| Data Type | Storage | Survives Restart? | Backup? |
|-----------|---------|-------------------|---------|
| Custom Universes | In-memory | ❌ No | ❌ No |
| Run History | In-memory | ❌ No | ❌ No |
| Scheduled Scans | JSON file | ✅ Yes | ❌ No |
| Usage Logs | PostgreSQL | ✅ Yes | ✅ DB backup |
| Users | PostgreSQL | ✅ Yes | ✅ DB backup |

### Silent Data Loss Scenarios

| Scenario | Data Lost | User Notification |
|----------|-----------|-------------------|
| Server restart | Custom universes, run history | ❌ None |
| Process crash | Custom universes, run history | ❌ None |
| JSON file corruption | Scheduled scans | ❌ None |
| max_records limit (100) | Old run history | ❌ None — silently trimmed |

**Evidence** — [history.py:75-77](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/services/history.py#L75-L77)
```python
# Trim old records - SILENTLY DELETES DATA
if len(self._history) > self.max_records:
    self._history = self._history[:self.max_records]
```

### Transaction Handling

| Operation | Multi-Step? | Transaction? | Rollback on Failure? |
|-----------|-------------|--------------|----------------------|
| Create universe | No | N/A | N/A |
| Run model + save history | Yes | ❌ No | ❌ No |
| Update scan + save file | Yes | ❌ No | ❌ No |

**Partial Save Risk** — [models.py:221-240](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/api/routes/models.py#L221-L240)
```python
# Model runs successfully, but history save can fail silently
try:
    history_service = get_history_service()
    record = history_service.add_run(...)  # Can fail
except Exception as e:
    logger.error(f"Failed to save run to history: {str(e)}")
    # Continues anyway - user doesn't know history wasn't saved
```

---

## 4. DESTRUCTIVE ACTIONS

### Current State: 🔴 DANGEROUS

### Deletion Analysis

| Endpoint | What's Deleted | Soft Delete? | Confirmation? | Undo? |
|----------|----------------|--------------|---------------|-------|
| `DELETE /api/models/history` | **ALL run history** | ❌ Hard | ❌ No | ❌ No |
| `DELETE /api/custom-universe/{id}` | Single universe | ❌ Hard | ❌ No | ❌ No |
| `DELETE /api/scheduled-scans/{id}` | Single scan | ❌ Hard | ❌ No | ❌ No |
| `POST /debug/clear-cache` | All cached data | N/A | ❌ No | ❌ No |

### Critical Issue: Clear ALL History

**Location**: [models.py:435-440](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/api/routes/models.py#L435-L440)
```python
@router.delete("/history")
async def clear_history():
    """Clear all run history"""  # Deletes EVERYONE's history!
    history_service = get_history_service()
    count = history_service.clear()
    return {"cleared": count}
```

### Recommended Changes

1. **Add soft delete** with `deleted_at` timestamp
2. **Require confirmation parameter** for destructive actions
3. **Add user ownership check** before deletion
4. **Implement trash/recovery** period (e.g., 30 days)

```python
# Example: Safe delete with confirmation
@router.delete("/custom-universe/{universe_id}")
async def delete_custom_universe(
    universe_id: str,
    confirm: bool = Query(False, description="Set to true to confirm deletion"),
    user_id: str = Depends(get_current_user_id)
):
    if not confirm:
        raise HTTPException(
            status_code=400, 
            detail="Add ?confirm=true to confirm deletion"
        )
    
    manager = get_custom_universe_manager()
    universe = manager.get_universe(universe_id)
    
    if not universe or universe.user_id != user_id:
        raise HTTPException(status_code=404, detail="Universe not found")
    
    # Soft delete
    universe.deleted_at = datetime.now()
    return {"message": "Universe moved to trash. Will be permanently deleted in 30 days."}
```

---

## 5. SENSITIVE DATA

### PII Inventory

| Data | Location | Classification |
|------|----------|----------------|
| `email` | `users.email` (DB) | PII |
| `name` | `users.name` (DB) | PII |
| `clerk_id` | `users.clerk_id` (DB) | Internal ID |
| User's trading signals | run history | Sensitive financial |
| Custom stock lists | custom universes | Sensitive financial |

### Storage Security

| Data | Encrypted at Rest? | Encrypted in Transit? |
|------|--------------------|-----------------------|
| PostgreSQL | Depends on provider (Railway/Supabase usually yes) | ✅ TLS |
| JSON file (scans) | ❌ No | N/A (local) |
| In-memory data | ❌ No | N/A |

### Transmission Security

| Flow | Protocol | Encryption |
|------|----------|------------|
| Frontend → Backend | HTTP | ⚠️ Only HTTPS in production |
| Backend → PostgreSQL | TCP | ✅ TLS (Railway) |
| Backend → Yahoo Finance | HTTPS | ✅ TLS |

### What Should Be Encrypted

| Data | Current | Recommended |
|------|---------|-------------|
| User email | Plain | Hash for lookup, encrypt for display |
| Clerk secret key | Env var | ✅ Already secure |
| Database URL | Env var | ✅ Already secure |
| Trading signals | Plain | Consider encryption if storing long-term |

---

## P0 — CRITICAL (Must Fix Before Any Users)

### 🔴 DI-001: No User Data Isolation

**Risk**: Any user can view/edit/delete any other user's data.

**Fix Required**:
1. Add `user_id` field to CustomUniverse and ScheduledScan
2. Modify all CRUD operations to filter by current user
3. Move from in-memory to database storage

**Files to Change**:
- [services/custom_universe.py](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/services/custom_universe.py) — Add user_id to dataclass
- [routes/custom_universe.py](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/api/routes/custom_universe.py) — Filter by user_id
- [routes/scheduled_scans.py](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/api/routes/scheduled_scans.py) — Add user_id, filter

### 🔴 DI-002: DELETE /history Clears All Users' Data

**Risk**: One user can delete everyone's run history.

**Fix Required**:
- Remove global clear endpoint
- OR: Add `user_id` to RunRecord and clear only user's history
- OR: Require admin auth for global clear

**File**: [routes/models.py:435-440](file:///Users/nut/Downloads/quant-thai-stocks/backend/app/api/routes/models.py#L435-L440)

### 🔴 DI-003: Data Lost on Server Restart

**Risk**: All custom universes and run history lost silently.

**Fix Required**:
- Migrate CustomUniverseManager to use PostgreSQL `CustomUniverse` model
- Migrate HistoryService to use PostgreSQL or add file persistence

---

## P1 — HIGH (Fix Before Monetization)

### 🟠 DI-004: No Input Validation on Critical Fields

**Risk**: Injection attacks, XSS in PDF exports, DoS via large inputs.

**Fix**: Add validation rules (see Section 2).

### 🟠 DI-005: Hard Deletes With No Recovery

**Risk**: Accidental deletion is permanent.

**Fix**: Add soft delete with `deleted_at` timestamp.

### 🟠 DI-006: Silent Data Trimming

**Risk**: History silently drops records over max_records limit.

**Fix**: Either increase limit significantly, or notify user when trimming.

### 🟠 DI-007: No Confirmation on Destructive Actions

**Risk**: Accidental deletion via API call.

**Fix**: Require `?confirm=true` parameter.

---

## P2 — MEDIUM (Nice to Have)

### 🟡 DI-008: Scheduled Scans in JSON File

**Risk**: Single point of failure, no transactions.

**Fix**: Migrate to database.

### 🟡 DI-009: No Audit Log for Data Changes

**Risk**: Can't track who changed what.

**Fix**: Add audit log table tracking all CRUD operations.

### 🟡 DI-010: PII Not Encrypted

**Risk**: Data breach exposes emails.

**Fix**: Encrypt email field, use hash for lookups.

---

## Summary of Required Changes

### Database Schema Changes

```sql
-- Add ownership to custom universes (already in model, not used)
ALTER TABLE custom_universes 
  ALTER COLUMN user_id SET NOT NULL;

-- Add soft delete
ALTER TABLE custom_universes ADD COLUMN deleted_at TIMESTAMP;
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP;
```

### File-by-File Changes

| File | Changes Needed |
|------|----------------|
| `services/custom_universe.py` | Add user_id, migrate to DB |
| `routes/custom_universe.py` | Add user filter to all endpoints |
| `services/history.py` | Add user_id, add persistence |
| `routes/models.py` | Add user filter, remove global clear |
| `routes/scheduled_scans.py` | Add user_id, add confirmation |
| New: `validation.py` | Create validation utilities |
| New: `middleware/auth.py` | Extract user_id from request |

---

## Verification Checklist

```bash
# After fixes, test these scenarios:

# 1. User A cannot see User B's custom universes
curl -H "X-User-Id: user_a" /api/custom-universe/
curl -H "X-User-Id: user_b" /api/custom-universe/
# Results should be different

# 2. User A cannot delete User B's universe
curl -X DELETE -H "X-User-Id: user_a" /api/custom-universe/user_b_universe
# Should return 404

# 3. Data survives restart
# Create a universe, restart server, verify it exists

# 4. Validation rejects bad input
curl -X POST /api/analysis/%3Cscript%3E
# Should return 400

# 5. Delete requires confirmation
curl -X DELETE /api/custom-universe/test
# Should return 400 "Add ?confirm=true"
```

---

> [!CAUTION]
> **Current State**: All users share the same data pool. User A can delete User B's custom universes and scheduled scans. This is NOT suitable for a multi-user SaaS product.
