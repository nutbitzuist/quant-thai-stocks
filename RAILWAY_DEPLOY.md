# 🚂 Deploy to Railway - Complete Guide

## ✅ Yes, You Can Host on Railway!

**Short Answer:**
- ✅ **Backend on Railway** - Works perfectly
- ✅ **Frontend on Vercel** (Recommended) - Free, optimized for Next.js
- ✅ **OR Frontend on Railway** - Also possible, but Vercel is better for Next.js
- ✅ **Access from any computer** - Yes! You'll get a public URL
- ✅ **Cost: $0-5/month** - Free tier available

---

## 💰 Cost Breakdown

### Option 1: Backend on Railway + Frontend on Vercel (Recommended) ⭐

| Service | Cost | Details |
|---------|------|---------|
| **Backend (Railway)** | **$0-5/month** | Free tier: 500 hours/month<br>Paid: $5/month for unlimited |
| **Frontend (Vercel)** | **$0/month** | Free forever (Hobby plan) |
| **Total** | **$0-5/month** | Depends on backend usage |

**Free Tier Limits:**
- Railway: 500 hours/month (enough for ~16 hours/day)
- Vercel: Unlimited (free tier is generous)

### Option 2: Both on Railway

| Service | Cost | Details |
|---------|------|---------|
| **Backend (Railway)** | **$0-5/month** | Free tier: 500 hours/month |
| **Frontend (Railway)** | **$0-5/month** | Free tier: 500 hours/month |
| **Total** | **$0-10/month** | If both exceed free tier |

**Recommendation:** Use Option 1 (Vercel for frontend) - it's free and better optimized for Next.js.

---

## 🚀 Quick Deploy (Recommended Setup)

### Step 1: Deploy Backend to Railway (5 minutes)

1. **Sign up for Railway:**
   - Go to [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Sign up with GitHub (easiest)

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your repository
   - Select the repository

3. **Configure Backend:**
   - Railway will auto-detect Python
   - Click on the service → Settings
   - **Set Root Directory:** `backend`
   - **Set Start Command:** (leave default, or use from Procfile)

4. **Add Environment Variables:**
   - Go to Variables tab
   - Add these:
     ```
     DEBUG=false
     CORS_ORIGINS=["https://your-frontend.vercel.app"]
     ```
     (We'll update CORS_ORIGINS after deploying frontend)

5. **Deploy:**
   - Railway will automatically deploy
   - Wait 2-3 minutes for build to complete
   - **Copy your backend URL** (e.g., `https://your-backend.up.railway.app`)
   - Test it: Visit `https://your-backend.up.railway.app/health`

### Step 2: Deploy Frontend to Vercel (3 minutes)

1. **Sign up for Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "Sign Up"
   - Sign up with GitHub

2. **Import Project:**
   - Click "Add New Project"
   - Import your GitHub repository
   - Select the repository

3. **Configure:**
   - **Framework Preset:** Next.js (auto-detected)
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build` (default)
   - **Output Directory:** `.next` (default)

4. **Add Environment Variable:**
   - Click "Environment Variables"
   - Add:
     ```
     Name: NEXT_PUBLIC_API_URL
     Value: https://your-backend.up.railway.app
     ```
     (Use the Railway backend URL from Step 1)

5. **Deploy:**
   - Click "Deploy"
   - Wait 1-2 minutes
   - **Copy your frontend URL** (e.g., `https://your-app.vercel.app`)

6. **Update Backend CORS:**
   - Go back to Railway → Your backend service → Variables
   - Update `CORS_ORIGINS`:
     ```
     CORS_ORIGINS=["https://your-app.vercel.app"]
     ```
   - Railway will auto-redeploy

### Step 3: Test Everything

1. **Test Backend:** `https://your-backend.up.railway.app/health`
2. **Test Frontend:** `https://your-app.vercel.app`
3. **Test Connection:** Open browser console on frontend, should see "Connected"

**🎉 Done! Your app is live and accessible from anywhere!**

---

## 🚂 Alternative: Both on Railway

If you prefer to host both on Railway:

### Backend Service (Same as above)

### Frontend Service (Additional)

1. **Add New Service:**
   - In your Railway project, click "+ New"
   - Select "GitHub Repo"
   - Select the same repository

2. **Configure:**
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Start Command:** `npm start`

3. **Environment Variables:**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
   PORT=$PORT
   ```

4. **Generate Domain:**
   - Railway will give you a URL like `https://your-frontend.up.railway.app`

**Note:** Railway charges per service, so this will use 2x the free tier hours.

---

## 🔧 Environment Variables Reference

### Backend (Railway)

```env
DEBUG=false
CORS_ORIGINS=["https://your-frontend.vercel.app"]
DATA_CACHE_MINUTES=30
MAX_WORKERS=10
DEFAULT_UNIVERSE=sp500
```

### Frontend (Vercel or Railway)

```env
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
```

---

## 📊 Railway Free Tier Details

**What you get for FREE:**
- ✅ 500 hours/month of compute time
- ✅ $5 credit/month (covers light usage)
- ✅ Automatic HTTPS
- ✅ Custom domains
- ✅ Environment variables
- ✅ Logs and monitoring

**When you might need to pay ($5/month):**
- If you exceed 500 hours/month
- If you need more resources (RAM/CPU)
- If you want faster builds

**For this project:** Free tier is usually enough unless you have very heavy traffic.

---

## 🌐 Accessing from Any Computer

Once deployed:
- ✅ **Public URL:** Your app will have a public URL (e.g., `https://your-app.vercel.app`)
- ✅ **Access from anywhere:** Any computer with internet can access it
- ✅ **No VPN needed:** It's publicly accessible
- ✅ **HTTPS included:** Both Railway and Vercel provide free SSL certificates

---

## 🔄 Updating Your App

### Automatic Updates (Recommended)

Both Railway and Vercel support **automatic deployments**:
- Push to `main` branch → Auto-deploys
- No manual steps needed!

### Manual Updates

```bash
# Just push to GitHub
git add .
git commit -m "Update app"
git push origin main

# Railway and Vercel will auto-deploy
```

---

## 🛠 Troubleshooting

### Backend won't start on Railway

1. **Check logs:** Railway dashboard → Your service → Deployments → View logs
2. **Check Root Directory:** Must be set to `backend`
3. **Check Python version:** Railway uses Python 3.11+ by default
4. **Check requirements.txt:** Make sure all dependencies are listed

### Frontend can't connect to backend

1. **Check CORS_ORIGINS:** Must include your frontend URL exactly
2. **Check NEXT_PUBLIC_API_URL:** Must be your Railway backend URL
3. **Check backend is running:** Visit backend health endpoint
4. **Check browser console:** Look for CORS errors

### Build fails

1. **Backend:** Check Railway logs for Python errors
2. **Frontend:** Check Vercel logs for Node.js errors
3. **Dependencies:** Make sure all are in requirements.txt / package.json

---

## 💡 Pro Tips

1. **Use Railway CLI for faster deploys:**
   ```bash
   npm i -g @railway/cli
   railway login
   railway link
   railway up
   ```

2. **Monitor usage:**
   - Railway dashboard shows your usage
   - Set up billing alerts if needed

3. **Custom domains:**
   - Both Railway and Vercel support custom domains
   - Free SSL certificates included

4. **Environment-specific configs:**
   - Use different env vars for dev/prod
   - Railway and Vercel support multiple environments

---

## 📝 Summary

✅ **Yes, you can host on Railway**
✅ **Access from any computer** - Public URL provided
✅ **Cost: $0-5/month** - Free tier is generous
✅ **Recommended:** Backend on Railway + Frontend on Vercel
✅ **Automatic deployments** - Just push to GitHub

**Your app will be live at:**
- Frontend: `https://your-app.vercel.app`
- Backend: `https://your-backend.up.railway.app`

**Total setup time: ~10 minutes!**

---

Need help? Check the main [DEPLOYMENT.md](./DEPLOYMENT.md) or [QUICK_DEPLOY.md](./QUICK_DEPLOY.md)

