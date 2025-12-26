# 🔧 Fix Backend 502 Error - "Failed to fetch"

## Problem

Your backend is returning **502 "Application failed to respond"**, which causes the frontend "Failed to fetch" errors.

## Root Cause

The backend service on Railway is either:
1. **Crashed** - Application error
2. **Not starting** - Build/deployment issue
3. **Missing dependencies** - Requirements not installed
4. **Port misconfiguration** - Wrong port binding

---

## 🔍 Step 1: Check Railway Logs

1. Go to Railway Dashboard:
   ```
   https://railway.com/project/a54028cf-667f-4889-989c-7574b61ae6e4
   ```

2. Click on your **backend service**

3. Go to **"Deployments"** tab

4. Click on the latest deployment → **"View Logs"**

5. Look for errors like:
   - `ModuleNotFoundError`
   - `ImportError`
   - `Port already in use`
   - `Application startup failed`

---

## 🛠 Step 2: Common Fixes

### Fix 1: Check Environment Variables

Make sure these are set in Railway:

**Backend Variables:**
```
DEBUG=false
CORS_ORIGINS=["https://nutquant.vercel.app"]
PORT=$PORT
```

**Important:** Railway automatically sets `$PORT`, but make sure your app uses it!

### Fix 2: Verify Procfile

Check `backend/Procfile`:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Fix 3: Check Requirements

Make sure `backend/requirements.txt` has all dependencies:
```bash
cd backend
pip install -r requirements.txt
# Should install without errors
```

### Fix 4: Test Locally First

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# Should start without errors
```

---

## 🚀 Step 3: Redeploy Backend

### Option A: Via Railway Dashboard

1. Go to backend service
2. Click **"Redeploy"** or **"Deploy"**
3. Watch the logs for errors

### Option B: Via Railway CLI

```bash
cd backend
railway up --detach
railway logs --tail 100
```

### Option C: Push to GitHub (if connected)

```bash
git add .
git commit -m "Fix backend deployment"
git push
# Railway will auto-deploy
```

---

## 🔍 Step 4: Check Specific Issues

### Issue: Missing Dependencies

**Symptoms:** `ModuleNotFoundError` in logs

**Fix:**
1. Check `requirements.txt` has all packages
2. Make sure versions are compatible
3. Redeploy

### Issue: Port Binding

**Symptoms:** `Address already in use` or `Port not found`

**Fix:**
- Railway uses `$PORT` environment variable
- Make sure Procfile uses `--port $PORT`
- Don't hardcode port numbers

### Issue: Import Errors

**Symptoms:** `ImportError` or `ModuleNotFoundError`

**Fix:**
1. Check all imports in `app/main.py`
2. Verify `__init__.py` files exist
3. Test locally first

### Issue: Application Crash

**Symptoms:** App starts then crashes

**Fix:**
1. Check Railway logs for Python traceback
2. Look for unhandled exceptions
3. Add error handling

---

## ✅ Step 5: Verify Backend is Running

After redeploying, test:

```bash
curl https://quant-stocks-backend-production.up.railway.app/health
```

Should return:
```json
{"status": "healthy", ...}
```

If still 502, check logs again.

---

## 🔧 Step 6: Update CORS (After Backend is Fixed)

Once backend is running, update CORS:

**Railway Dashboard → Backend → Variables:**
```
CORS_ORIGINS=["https://nutquant.vercel.app"]
```

Or via CLI:
```bash
cd backend
railway variables --set CORS_ORIGINS='["https://nutquant.vercel.app"]'
```

---

## 🎯 Quick Checklist

- [ ] Check Railway logs for errors
- [ ] Verify environment variables are set
- [ ] Check Procfile is correct
- [ ] Test backend locally
- [ ] Redeploy backend
- [ ] Verify `/health` endpoint works
- [ ] Update CORS with new frontend URL
- [ ] Test frontend connection

---

## 🆘 Still Not Working?

1. **Check Railway Status Page:** https://status.railway.app
2. **Check Service Limits:** Hobby plan has limits
3. **Review Logs:** Look for specific error messages
4. **Test Locally:** Make sure it works locally first
5. **Contact Support:** Railway support if needed

---

## 💡 Prevention

1. **Test locally first** before deploying
2. **Monitor logs** regularly
3. **Set up alerts** for deployment failures
4. **Use staging environment** for testing
5. **Keep dependencies updated**

---

**The main issue is the backend is down (502). Fix the backend first, then update CORS!**

