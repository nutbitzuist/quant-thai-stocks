# ✅ Railway Deployment - Almost Complete!

## 🎉 What's Been Done

✅ **GitHub Repository Created:**
- Repository: https://github.com/nutbitzuist/quant-thai-stocks
- All code pushed successfully

✅ **Railway Backend Deployed:**
- Project: quant-stocks-backend
- URL: https://quant-stocks-backend-production.up.railway.app
- Status: Deploying (wait 2-3 minutes)

---

## 🔧 Final Steps (2 minutes)

### Step 1: Set Backend Environment Variables

Go to Railway Dashboard:
1. Visit: https://railway.com/project/a54028cf-667f-4889-989c-7574b61ae6e4
2. Click on your backend service
3. Go to "Variables" tab
4. Add these variables:
   ```
   DEBUG=false
   CORS_ORIGINS=["*"]
   ```
   (We'll update CORS_ORIGINS after frontend deploys)

### Step 2: Deploy Frontend

**Option A: Via Railway Dashboard (Easiest)**

1. Go to: https://railway.com/project/a54028cf-667f-4889-989c-7574b61ae6e4
2. Click "+ New" → "GitHub Repo"
3. Select: `nutbitzuist/quant-thai-stocks`
4. Set **Root Directory:** `frontend`
5. Click "Deploy"
6. Go to "Variables" tab
7. Add:
   ```
   NEXT_PUBLIC_API_URL=https://quant-stocks-backend-production.up.railway.app
   ```
8. Wait for deployment (2-3 minutes)
9. Click "Settings" → "Generate Domain" to get your frontend URL

**Option B: Via Railway CLI**

```bash
cd frontend
railway link
# Select the same project: quant-stocks-backend
railway service
# Create new service for frontend
railway variables --set NEXT_PUBLIC_API_URL=https://quant-stocks-backend-production.up.railway.app
railway up
```

### Step 3: Update Backend CORS

After frontend is deployed:
1. Go to backend service → Variables
2. Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS=["https://your-frontend-url.up.railway.app"]
   ```
   (Use your actual frontend URL)

---

## ✅ Verify Everything Works

1. **Test Backend:**
   - Visit: https://quant-stocks-backend-production.up.railway.app/health
   - Should return: `{"status": "healthy", ...}`

2. **Test Frontend:**
   - Visit your frontend URL
   - Should see the dashboard
   - Check browser console (F12) - should see "Connected"

---

## 🎯 Your URLs

- **Backend:** https://quant-stocks-backend-production.up.railway.app
- **Frontend:** (will be available after Step 2)
- **GitHub:** https://github.com/nutbitzuist/quant-thai-stocks

---

## 🔄 Future Updates

Just push to GitHub:
```bash
git add .
git commit -m "Update app"
git push
```

Railway will auto-deploy if connected to GitHub!

---

## 💰 Cost

- **Free tier:** 500 hours/month per service
- **2 services:** Usually stays within free tier
- **If exceeded:** ~$10/month total

---

**Almost done! Just complete the 3 steps above and you're live!** 🚀

