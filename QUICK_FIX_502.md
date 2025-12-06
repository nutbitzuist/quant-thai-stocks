# 🚨 Quick Fix: Backend 502 Error

## Problem
Backend returns **502 "Application failed to respond"** → Frontend shows "Failed to fetch"

## Root Cause
Backend service on Railway is **down or crashed**

---

## ✅ Quick Fix (5 minutes)

### Step 1: Check Railway Dashboard

1. **Go to:** https://railway.com/project/a54028cf-667f-4889-989c-7574b61ae6e4

2. **Click on your backend service**

3. **Check "Deployments" tab:**
   - Is the latest deployment successful? (green checkmark)
   - Or is it failed/error? (red X)

4. **Click on latest deployment → "View Logs"**
   - Look for error messages
   - Common errors:
     - `ModuleNotFoundError` → Missing dependency
     - `ImportError` → Import issue
     - `Port already in use` → Port conflict
     - `Application startup failed` → Code error

### Step 2: Fix Based on Error

**If you see `ModuleNotFoundError`:**
- Check `requirements.txt` has all packages
- Redeploy

**If you see `ImportError`:**
- Check all imports in code
- Test locally first

**If deployment failed:**
- Check build logs
- Fix the error
- Redeploy

### Step 3: Redeploy Backend

**Option A: Via Dashboard (Easiest)**
1. Go to backend service
2. Click **"Redeploy"** button
3. Wait 2-3 minutes
4. Check logs

**Option B: Via CLI**
```bash
cd backend
railway service link  # Link to your backend service
railway up --detach
railway logs --tail 50
```

**Option C: Push to GitHub**
```bash
git add .
git commit -m "Fix backend"
git push
# Railway will auto-redeploy if connected
```

### Step 4: Verify Backend is Running

Test the health endpoint:
```bash
curl https://quant-stocks-backend-production.up.railway.app/health
```

Should return:
```json
{"status": "healthy", ...}
```

If still 502, check logs again.

### Step 5: Update CORS (After Backend is Fixed)

Once backend is running:

**Railway Dashboard → Backend → Variables:**
```
CORS_ORIGINS=["https://nutquant.vercel.app"]
```

This allows your frontend to connect.

---

## 🔍 Common Issues & Fixes

### Issue 1: Missing Environment Variables

**Check these are set:**
- `DEBUG=false`
- `CORS_ORIGINS=["https://nutquant.vercel.app"]`
- `PORT=$PORT` (Railway sets this automatically)

### Issue 2: Procfile Issue

**Verify `backend/Procfile`:**
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Issue 3: Python Version

Railway uses Python 3.11+ by default. If you need a specific version:
- Create `backend/runtime.txt`:
  ```
  python-3.11
  ```

### Issue 4: Dependencies

**Test locally:**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

If it works locally, the issue is Railway-specific.

---

## 🎯 Most Likely Fix

**90% of the time, it's one of these:**

1. **Backend crashed** → Check logs, fix error, redeploy
2. **Missing CORS** → Add `CORS_ORIGINS` environment variable
3. **Build failed** → Check build logs, fix dependencies
4. **Port issue** → Verify Procfile uses `$PORT`

---

## ✅ After Fixing

1. Backend `/health` endpoint works
2. Frontend can connect (no CORS errors)
3. Models can run successfully

---

## 🆘 Still Not Working?

1. **Check Railway Status:** https://status.railway.app
2. **Review Logs:** Look for specific error messages
3. **Test Locally:** Make sure it works locally first
4. **Contact Support:** Railway support if needed

---

**The backend is down (502). Fix it first, then update CORS!**

