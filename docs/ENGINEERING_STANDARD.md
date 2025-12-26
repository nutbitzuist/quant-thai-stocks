# Engineering Standards

**Project**: QuantStack  
**Version**: 2.1.0  
**Last Updated**: 2025-12-26

---

## Core Philosophy

### 1. Boring > Clever

```
❌ "This one-liner using reduce and flatMap is elegant"
✅ "This explicit loop is readable by anyone"
```

Choose obvious solutions over clever ones. Code is read 10x more than written.

### 2. Explicit > Implicit

```
❌ Magic strings, hidden side effects, mystery meat
✅ Named constants, pure functions, clear data flow
```

If someone needs to "just know" something, document it or make it explicit.

### 3. Working > Perfect

```
❌ Refactor for 3 days before feature works
✅ Get it working, then improve incrementally
```

Ship working code, then iterate. Don't over-engineer upfront.

### 4. Delete > Deprecate

```
❌ Keep old code "just in case"
✅ Delete unused code, use git history if needed
```

Dead code is worse than no code. It misleads and confuses.

---

## How AI Is Allowed to Work on This Project

### AI Can Do

- ✅ Add new features following existing patterns
- ✅ Fix bugs with clear root cause
- ✅ Refactor with explicit approval
- ✅ Generate documentation
- ✅ Write tests

### AI Must Not Do

- ❌ Change auth patterns without explicit approval
- ❌ Delete files without confirmation
- ❌ Modify environment variable names
- ❌ Change API route paths
- ❌ Introduce new dependencies without discussion

### AI Must Always

- 🔒 Create snapshot/tag before major refactors
- 📝 Document decisions in DECISIONS.md
- ✅ Run smoke tests after changes
- 🔄 Keep changes small and reviewable

---

## Build Rules

### Vertical Slices

Each feature should be a complete vertical slice:
```
Feature = Route + Component + API Call + Backend Handler
```

Don't build "all the routes first, then all the components." Build one complete feature at a time.

### One Responsibility Per Layer

| Layer | Responsibility | NOT Responsible For |
|-------|---------------|---------------------|
| Route/Page | URL mapping, layout | Business logic |
| Component | UI rendering | Data fetching |
| Hook | State management | API calls |
| Service | API calls | UI rendering |
| API Route | HTTP handling | Database queries |
| Backend Service | Business logic | HTTP concerns |

### File Size Limits

| File Type | Max Lines | Action if Exceeded |
|-----------|-----------|-------------------|
| Component | 300 | Extract sub-components |
| Page | 500 | Extract to components |
| Service | 400 | Split by domain |
| API Route | 200 | Extract to service |

---

## Definition of "Feature Done"

A feature is complete when:

- [ ] **Works** - Happy path functions correctly
- [ ] **Handles Errors** - Errors display gracefully
- [ ] **Loads Properly** - Loading states shown
- [ ] **Tested** - Manual smoke test passed
- [ ] **Documented** - Updated relevant docs if needed
- [ ] **Reviewed** - Another human/AI reviewed changes

---

## Change Discipline Rules

### Before Making Changes

1. **Understand current state** - Read relevant code first
2. **Check for tests** - Will this break anything?
3. **Consider dependencies** - What else uses this?
4. **Small PRs** - One concern per change

### Change Size Guidelines

| Change Type | Max Files | Max Lines |
|-------------|-----------|-----------|
| Bug fix | 3 | 50 |
| Small feature | 5 | 200 |
| Medium feature | 10 | 500 |
| Large feature | 20+ | Needs design doc |

### After Making Changes

1. **Smoke test** - Verify basic flows work
2. **Check console** - No new errors
3. **Review diff** - Does it match intent?
4. **Commit message** - Clear and descriptive

---

## Auth Protection Rules

### Protected Routes (Must Enforce Auth)

```
/dashboard/*  → Requires signed-in user
/admin/*      → Requires admin role
/api/user/*   → Requires valid session (future)
```

### Public Routes (No Auth Required)

```
/             → Landing page
/sign-in      → Auth flow
/sign-up      → Auth flow
/api/health   → Health check
```

### Auth Rule: Never Bypass in Production

```typescript
// ❌ NEVER do this in production
if (isDevelopment || isLoggedIn) { ... }

// ✅ Development bypass only via env check
if (!CLERK_KEYS_EXIST) { 
  // Works without auth in dev
}
```

---

## Code Style

### TypeScript

```typescript
// ✅ Use interface for objects
interface User {
  id: string;
  email: string;
}

// ✅ Use type for unions/primitives
type Status = 'active' | 'inactive';

// ✅ Explicit return types for exported functions
export function getUser(id: string): Promise<User> { }
```

### React Components

```tsx
// ✅ Function components with explicit props
interface ButtonProps {
  onClick: () => void;
  children: React.ReactNode;
}

export function Button({ onClick, children }: ButtonProps) {
  return <button onClick={onClick}>{children}</button>;
}
```

### Python

```python
# ✅ Type hints on functions
def run_model(model_id: str, universe: str) -> ModelResult:
    pass

# ✅ Pydantic for request/response models
class RunModelRequest(BaseModel):
    model_id: str
    universe: str
```

---

## Naming Conventions

| Entity | Convention | Example |
|--------|-----------|---------|
| React Component | PascalCase | `ModelCard.tsx` |
| React Hook | camelCase with use prefix | `useModels.ts` |
| TypeScript Type | PascalCase | `ModelResult` |
| Python Function | snake_case | `run_model()` |
| Python Class | PascalCase | `ModelResult` |
| API Route | kebab-case | `/api/run-model` |
| CSS Class | kebab-case | `.model-card` |
| Env Variable | SCREAMING_SNAKE_CASE | `CLERK_SECRET_KEY` |

---

## Error Handling

### Frontend

```typescript
// ✅ Try-catch with user feedback
try {
  const result = await runModel(id);
  setResults(result);
} catch (error) {
  setError('Failed to run model. Please try again.');
  console.error('Model run failed:', error);
}
```

### Backend

```python
# ✅ HTTPException with clear message
try:
    result = run_model(request)
    return result
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error(f"Model run failed: {e}")
    raise HTTPException(status_code=500, detail="Internal error")
```

---

## Commit Message Format

```
<type>: <short description>

<optional body>

<optional footer>
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `refactor` | Code refactoring |
| `test` | Adding tests |
| `chore` | Maintenance |

### Examples

```
feat: add pricing toggle to landing page
fix: correct CORS headers for production
docs: add engineering standards document
refactor: extract dashboard components
```

---

## Red Lines (Never Cross)

1. **Never commit secrets** - Use env vars
2. **Never disable auth in production** - Only in dev
3. **Never delete without backup** - Tag first
4. **Never bypass error handling** - Always catch
5. **Never skip smoke tests** - Always verify
