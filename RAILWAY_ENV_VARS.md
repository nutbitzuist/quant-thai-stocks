# 🔧 Railway Environment Variables Setup

## Required Environment Variables

### Backend Service Variables

Go to Railway Dashboard → Backend Service → Variables tab and set:

```
DEBUG=false
CORS_ORIGINS=["https://nutquant.vercel.app"]
```

**Important:** The `CORS_ORIGINS` must be valid JSON format:
- ✅ Correct: `["https://nutquant.vercel.app"]`
- ✅ Correct: `["https://nutquant.vercel.app","http://localhost:3000"]`
- ❌ Wrong: `https://nutquant.vercel.app` (missing brackets)
- ❌ Wrong: `'["https://nutquant.vercel.app"]'` (extra quotes)

### Optional Variables

```
DATA_CACHE_MINUTES=120
MAX_WORKERS=10
DEFAULT_UNIVERSE=sp500
DATA_PROVIDERS=yfinance
DATA_FALLBACK_ENABLED=true
```

---

## How to Set in Railway Dashboard

1. Go to: https://railway.com/project/a54028cf-667f-4889-989c-7574b61ae6e4
2. Click on **backend service**
3. Go to **"Variables"** tab
4. Click **"+ New Variable"**
5. Add:
   - **Key:** `CORS_ORIGINS`
   - **Value:** `["https://nutquant.vercel.app"]`
6. Click **"Add"**
7. Railway will auto-redeploy

---

## Verification

After setting variables, check:
1. Backend logs show no errors
2. `/health` endpoint works
3. Frontend can connect (no CORS errors)

---

## Troubleshooting

### Error: "error parsing value for field cors_origins"

**Cause:** Invalid JSON format in `CORS_ORIGINS`

**Fix:**
- Make sure it's valid JSON: `["https://nutquant.vercel.app"]`
- No extra quotes around the JSON
- Use square brackets `[]` for array
- Use double quotes `"` for strings

### Error: "Expecting value: line 1 column 1"

**Cause:** Empty or whitespace-only value

**Fix:**
- Make sure `CORS_ORIGINS` has a value
- Don't leave it empty
- Use: `["https://nutquant.vercel.app"]`

---

## Current Configuration

**Frontend URL:** https://nutquant.vercel.app
**Backend URL:** https://quant-stocks-backend-production.up.railway.app

**Required CORS_ORIGINS:**
```
["https://nutquant.vercel.app"]
```

