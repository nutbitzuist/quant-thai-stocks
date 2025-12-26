# 🔄 Vercel Auto-Deployment Setup

## Problem
Changes pushed to GitHub but Vercel didn't auto-deploy.

## Solution: Connect Vercel to GitHub

### Step 1: Check Current Status

1. Go to: https://vercel.com/dashboard
2. Click on your **"frontend"** project
3. Go to **"Settings"** → **"Git"**

### Step 2: Connect GitHub (If Not Connected)

If GitHub is not connected:

1. Click **"Connect Git Repository"**
2. Select **"GitHub"**
3. Authorize Vercel to access your GitHub
4. Select repository: `nutbitzuist/quant-thai-stocks`
5. Configure:
   - **Root Directory:** `frontend`
   - **Framework Preset:** Next.js
   - **Build Command:** `npm run build` (default)
   - **Output Directory:** `.next` (default)
6. Click **"Deploy"**

### Step 3: Verify Auto-Deployment

After connecting:

1. Make a small change
2. Push to GitHub:
   ```bash
   git add .
   git commit -m "Test auto-deploy"
   git push
   ```
3. Check Vercel dashboard - should see deployment starting automatically

---

## Manual Deployment (Current Method)

If auto-deployment isn't working, you can deploy manually:

```bash
cd frontend
vercel --prod
```

This will deploy the latest code from your local directory.

---

## Why Auto-Deployment Might Not Work

1. **Not Connected to GitHub** - Vercel needs to be connected to your repo
2. **Wrong Branch** - Vercel might be watching a different branch
3. **Root Directory** - Must be set to `frontend`
4. **Build Settings** - Must be configured correctly

---

## Quick Fix: Manual Deploy

I just deployed manually for you. The latest deployment is:
- **URL:** https://frontend-qucg2yb7x-nutbitzuists-projects.vercel.app
- **Status:** ✅ Ready

Your production domain should update automatically: https://nutquant.vercel.app

---

## Verify Deployment

1. Visit: https://nutquant.vercel.app
2. Check if dashboard tab is removed
3. Should start on "Models" tab now

---

## Future: Enable Auto-Deployment

To avoid manual deployments:

1. Connect Vercel to GitHub (see Step 2 above)
2. Every `git push` will trigger auto-deployment
3. Check Vercel dashboard for deployment status

---

**Current Status:** ✅ Manually deployed - changes are live!

