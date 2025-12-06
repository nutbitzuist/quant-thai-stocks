# 🚀 Frontend Deployment - Railway CLI

## Current Status

✅ **Backend:** Deployed and running
✅ **GitHub:** Repository created and code pushed
❌ **Frontend Service:** Needs to be created first

## Issue

Railway CLI doesn't have a direct command to create new services. The service must be created via:
1. Railway Dashboard (easiest)
2. Railway API (requires authentication token)
3. GitHub integration (auto-creates on first deploy)

## Solution: Create Service via Dashboard (2 minutes)

Since Railway CLI requires the service to exist before deploying, here's the quickest way:

### Step 1: Create Frontend Service

1. **Go to Railway Dashboard:**
   ```
   https://railway.com/project/a54028cf-667f-4889-989c-7574b61ae6e4
   ```

2. **Click "+ New" → "GitHub Repo"**

3. **Select Repository:**
   - Choose: `nutbitzuist/quant-thai-stocks`

4. **Configure:**
   - **Root Directory:** `frontend`
   - Railway will auto-detect it's a Next.js app

5. **Click "Deploy"**

6. **Wait 2-3 minutes** for initial deployment

### Step 2: Set Environment Variable

1. **Go to your frontend service** in Railway dashboard
2. **Click "Variables" tab**
3. **Add:**
   ```
   NEXT_PUBLIC_API_URL=https://quant-stocks-backend-production.up.railway.app
   ```
4. Railway will auto-redeploy

### Step 3: Get Frontend URL

1. **Go to frontend service → Settings**
2. **Click "Generate Domain"** (if not already generated)
3. **Copy your frontend URL**

### Step 4: Update Backend CORS

1. **Go to backend service → Variables**
2. **Update `CORS_ORIGINS`:**
   ```
   CORS_ORIGINS=["https://your-frontend-url.up.railway.app"]
   ```
   (Use your actual frontend URL from Step 3)

---

## Alternative: Use Railway CLI After Service Creation

Once the service is created via dashboard, you can use CLI:

```bash
cd frontend

# Link to the service
railway service link frontend

# Set environment variable
railway variables --set NEXT_PUBLIC_API_URL=https://quant-stocks-backend-production.up.railway.app

# Deploy
railway up --detach
```

---

## Why This Limitation?

Railway CLI is designed to work with existing services. Service creation requires:
- Project permissions
- Service configuration
- GitHub integration setup

These are better handled via the dashboard for the first service creation.

---

## ✅ After Service Creation

Once the frontend service exists, all future deployments can be done via CLI:

```bash
cd frontend
railway up
```

Or just push to GitHub (if connected):
```bash
git push
```

---

**Total time: ~5 minutes via dashboard, then CLI works for all future updates!**

