# ✅ Fixed: CORS_ORIGINS Parsing Error

## Problem
Backend was crashing with:
```
pydantic_settings.exceptions.SettingsError: error parsing value for field "cors_origins"
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

## Root Cause
The `CORS_ORIGINS` environment variable in Railway was either:
- Empty
- Invalid JSON format
- Not set correctly

## ✅ Fix Applied

1. **Updated `config.py`** to handle empty/invalid CORS_ORIGINS better
2. **Pushed to GitHub** - Railway will auto-deploy

## 🔧 Action Required: Set CORS_ORIGINS in Railway

**You MUST set the CORS_ORIGINS environment variable in Railway:**

### Step 1: Go to Railway Dashboard
https://railway.com/project/a54028cf-667f-4889-989c-7574b61ae6e4

### Step 2: Backend Service → Variables

### Step 3: Add/Update CORS_ORIGINS

**Key:** `CORS_ORIGINS`
**Value:** `["https://nutquant.vercel.app"]`

**Important:** 
- ✅ Must be valid JSON format
- ✅ Use square brackets `[]`
- ✅ Use double quotes `"`
- ❌ Don't add extra quotes around the JSON

### Step 4: Also Set DEBUG

**Key:** `DEBUG`
**Value:** `false`

### Step 5: Save and Wait

Railway will auto-redeploy (2-3 minutes)

---

## ✅ Verify Fix

After Railway redeploys:

1. **Check Backend Health:**
   ```bash
   curl https://quant-stocks-backend-production.up.railway.app/health
   ```
   Should return: `{"status": "healthy", ...}`

2. **Test Frontend:**
   - Visit: https://nutquant.vercel.app
   - Should connect to backend
   - No "Failed to fetch" errors

---

## 📋 Complete Environment Variables List

Set these in Railway → Backend → Variables:

```
DEBUG=false
CORS_ORIGINS=["https://nutquant.vercel.app"]
```

Optional:
```
DATA_CACHE_MINUTES=120
MAX_WORKERS=10
DEFAULT_UNIVERSE=sp500
```

---

## 🔄 Future Changes

**Always push to GitHub after making changes:**

```bash
# Option 1: Use the script
./push-changes.sh "Your commit message"

# Option 2: Manual
git add .
git commit -m "Your commit message"
git push
```

Railway will automatically deploy when you push to GitHub (if connected)!

---

## ✅ Status

- ✅ Code fixed and pushed to GitHub
- ⏳ Waiting for Railway to redeploy
- ⏳ Need to set CORS_ORIGINS in Railway dashboard

**Next step:** Set CORS_ORIGINS in Railway dashboard (see above)

