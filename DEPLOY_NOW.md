# 🚀 Quick Deploy Guide - Both on Railway

## ✅ Everything is Ready!

Your project is configured for Railway deployment. Follow these steps:

---

## Step 1: Create GitHub Repository (2 minutes)

1. **Go to GitHub:** https://github.com/new

2. **Create Repository:**
   - Repository name: `quant-thai-stocks` (or any name)
   - Description: "Quantitative Stock Analysis Platform"
   - Choose: **Public** or **Private**
   - ⚠️ **DO NOT** check "Initialize with README" (we already have files)
   - Click "Create repository"

3. **Copy the repository URL** (you'll need it in Step 2)

---

## Step 2: Push to GitHub (1 minute)

Run these commands in your terminal:

```bash
cd "/Users/nut/Downloads/quant-thai-stocks 3"

# Add all files
git add .

# Commit
git commit -m "Initial commit: Quant Stock Analysis Platform"

# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/quant-thai-stocks.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Replace `YOUR_USERNAME`** with your actual GitHub username!

---

## Step 3: Login to Railway (1 minute)

```bash
railway login
```

This will open your browser to authenticate with Railway.

---

## Step 4: Deploy Backend (3 minutes)

```bash
# Navigate to backend
cd backend

# Initialize Railway project
railway init

# When prompted:
# - Select "Create a new project"
# - Project name: quant-stocks (or any name)

# Set environment variables
railway variables set DEBUG=false
railway variables set CORS_ORIGINS='["*"]'

# Deploy
railway up
```

**Wait for deployment to complete**, then:

```bash
# Get your backend URL
railway domain
```

**Copy the backend URL** - you'll need it for the frontend!

**Test it:** Visit `https://your-backend.up.railway.app/health`

---

## Step 5: Deploy Frontend (3 minutes)

```bash
# Navigate to frontend
cd ../frontend

# Link to the same Railway project
railway link

# Select the same project you created for backend

# Set environment variable (use your backend URL from Step 4)
railway variables set NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app

# Deploy
railway up
```

**Wait for deployment**, then:

```bash
# Get your frontend URL
railway domain
```

**Copy the frontend URL!**

---

## Step 6: Update Backend CORS (1 minute)

```bash
# Go back to backend
cd ../backend

# Update CORS to allow your frontend URL
railway variables set CORS_ORIGINS='["https://your-frontend.up.railway.app"]'
```

(Replace `your-frontend.up.railway.app` with your actual frontend URL)

---

## Step 7: Test Everything! 🎉

1. **Test Backend:** `https://your-backend.up.railway.app/health`
2. **Test Frontend:** `https://your-frontend.up.railway.app`
3. **Open browser console** (F12) - should see "Connected"

**Your app is now live and accessible from anywhere!** 🌐

---

## 🔄 Future Updates

To update your app:

```bash
# Make changes to your code
git add .
git commit -m "Update app"
git push

# Railway will auto-deploy if connected to GitHub
# Or manually deploy:
cd backend && railway up
cd ../frontend && railway up
```

---

## 🛠 Troubleshooting

### "railway: command not found"
```bash
npm install -g @railway/cli
# or
brew install railway
```

### Backend won't start
- Check logs: `railway logs` (in backend directory)
- Verify root directory is set to `backend` in Railway dashboard

### Frontend can't connect
- Check `NEXT_PUBLIC_API_URL` is set correctly
- Check backend CORS includes frontend URL
- Check browser console for errors

### Need help?
- Check detailed guide: `RAILWAY_BOTH_DEPLOY.md`
- Railway logs: `railway logs`
- Railway dashboard: https://railway.app

---

## 💰 Cost

- **Free tier:** 500 hours/month per service
- **2 services:** Usually stays within free tier
- **If exceeded:** ~$5/month per service = $10/month total

---

## ✅ Checklist

- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] Railway CLI installed and logged in
- [ ] Backend deployed and tested
- [ ] Frontend deployed and tested
- [ ] CORS updated
- [ ] App works from any computer!

---

**Total time: ~10-15 minutes**

**Need detailed instructions?** See `RAILWAY_BOTH_DEPLOY.md`

