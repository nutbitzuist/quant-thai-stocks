# Architecture Decisions (DECISIONS)

**Project**: QuantStack  
**Version**: 2.1.0  
**Last Updated**: 2025-12-26

---

## Decision Log

### DECISION-001: Separate Frontend/Backend Architecture

**Status**: Accepted  
**Date**: Project inception

**Context**: Need flexibility to host frontend and backend independently.

**Decision**: 
- Frontend: Next.js on Vercel
- Backend: FastAPI on Railway
- Communication via REST API

**Trade-offs**:
- ✅ Can scale independently
- ✅ Different deployment strategies
- ✅ Clear separation of concerns
- ❌ CORS complexity
- ❌ Extra network latency

**Guidance**: Keep this separation. Don't merge into monolith.

---

### DECISION-002: Yahoo Finance as Primary Data Source

**Status**: Accepted  
**Date**: Project inception

**Context**: Need free, reliable stock data for US and Thai markets.

**Decision**: Use `yfinance` library as primary data source.

**Trade-offs**:
- ✅ Free
- ✅ Good US market coverage
- ✅ Some Thai stock support (.BK suffix)
- ❌ 15-20 min delay
- ❌ Rate limited
- ❌ Occasionally unreliable

**Guidance**: Add fallback providers (Alpha Vantage, etc.) if needed. Don't pay for real-time data until profitable.

---

### DECISION-003: Clerk for Authentication

**Status**: Accepted  
**Date**: 2025-12-26

**Context**: Need auth without building from scratch.

**Decision**: Use Clerk.com as auth provider.

**Trade-offs**:
- ✅ Handles OAuth, email, MFA
- ✅ Hosted UI available
- ✅ Good Next.js integration
- ❌ Vendor lock-in
- ❌ Monthly cost at scale

**Guidance**: 
- Keep auth conditional (works without Clerk keys)
- Don't build custom session management

---

### DECISION-004: Conditional Auth (Works Without Keys)

**Status**: Accepted  
**Date**: 2025-12-26

**Context**: Development should be easy without configuring Clerk.

**Decision**: App runs in "no-auth" mode when Clerk keys missing.

**Implementation**:
```tsx
const hasClerkKeys = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
{hasClerkKeys ? <ClerkProvider>{children}</ClerkProvider> : children}
```

**Trade-offs**:
- ✅ Fast local development
- ✅ Lower barrier to contribution
- ❌ Dashboard accessible without auth in dev

**Guidance**: Keep this pattern. In production, always set Clerk keys.

---

### DECISION-005: In-Memory Cache (No Database)

**Status**: Accepted (temporary)  
**Date**: Project inception

**Context**: MVP doesn't need persistence.

**Decision**: Use Python dict for caching, no database.

**Trade-offs**:
- ✅ Simple, fast
- ✅ No database costs
- ❌ Data lost on restart
- ❌ Can't track user preferences
- ❌ Can't do usage billing

**Guidance**: This is TEMPORARY. Add database before monetization.

---

### DECISION-006: Neo-Brutalist Design

**Status**: Accepted  
**Date**: 2025-12-26

**Context**: Need distinctive, memorable visual identity.

**Decision**: Neo-Brutalist style inspired by hq0.com.

**Characteristics**:
- Hard shadows (not soft)
- Bold borders (3px solid)
- No border-radius
- High contrast colors
- Heavy typography

**Guidance**: 
- Use `var(--border)` for shadows
- Never add border-radius
- Keep shadows to 4-5px offset

---

### DECISION-007: Single Dashboard File (Technical Debt)

**Status**: Acknowledged (needs refactor)  
**Date**: Historical

**Context**: Dashboard grew organically to 4,153 lines.

**Decision**: Accept for now, refactor later.

**Why It Happened**:
- Rapid prototyping
- All state colocated
- No component library

**Guidance**: 
- DO refactor before adding more features
- Extract: types, hooks, components, styles
- Target: <500 lines per file

---

### DECISION-008: VectorBT for Backtesting

**Status**: Accepted  
**Date**: Project inception

**Context**: Need high-performance backtesting.

**Decision**: Use VectorBT library.

**Trade-offs**:
- ✅ Very fast (vectorized)
- ✅ Feature-rich
- ✅ Good Pandas integration
- ❌ Complex API
- ❌ Memory-heavy

**Guidance**: Keep VectorBT. Don't build custom backtester.

---

## Things Intentionally Avoided

| Feature | Why Avoided |
|---------|-------------|
| Real-time data | Too expensive, not needed for screening |
| WebSocket connections | HTTP polling sufficient |
| Custom auth | Clerk handles complexity |
| GraphQL | REST simpler for this use case |
| ORM | No database yet |
| Server-side rendering | Dashboard is SPA |
| Redux/Zustand | useState sufficient currently |
| Tailwind | Inline styles were faster initially |

---

## ⚠️ DO NOT CHANGE CASUALLY

These decisions are load-bearing. Changing them has cascading effects:

1. **Clerk auth pattern** - Affects all protected routes
2. **API route structure** - Frontend depends on exact paths
3. **Model interface** (base.py) - All 27 models inherit from it
4. **Data fetcher caching** - Performance depends on it
5. **CORS configuration** - Frontend/backend communication

---

## Future Decision Points

Decisions that will need to be made:

| Decision | When | Options |
|----------|------|---------|
| Database choice | Before payments | Supabase, Planetscale, Railway Postgres |
| Cache layer | At scale | Redis, Upstash |
| Payment processor | MVP done | Stripe, Lemon Squeezy |
| Error tracking | Before launch | Sentry, Rollbar |
| Analytics | Before launch | Posthog, Amplitude |
