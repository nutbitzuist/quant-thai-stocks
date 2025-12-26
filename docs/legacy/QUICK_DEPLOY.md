# Quick Deployment Guide

## 🎯 Recommendation: **Both on Railway/Vercel** (Option 2)

This is the easiest and most reliable option.

---

## Option 2: Deploy Both (Recommended) ⭐

### Step 1: Deploy Backend to Railway (5 minutes)

1. Go to [railway.app](https://railway.app) → Sign up with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect it's Python
5. **Set Root Directory:** `backend`
6. **Add Environment Variables:**
   ```
   DEBUG=false
   CORS_ORIGINS=["https://your-frontend.vercel.app"]
   ```
7. Railway will deploy automatically
8. **Copy your backend URL** (e.g., `https://your-backend.railway.app`)

### Step 2: Deploy Frontend to Vercel (3 minutes)

1. Go to [vercel.com](https://vercel.com) → Sign up with GitHub
2. Click "Add New Project" → Import your repo
3. **Set Root Directory:** `frontend`
4. **Add Environment Variable:**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```
   (Use the URL from Step 1)
5. Click "Deploy"
6. Done! Your app is live 🎉

---

## Option 1: Frontend on Vercel + Backend on Mac Mini

### Step 1: Expose Your Mac Mini Backend

**Option A: Use ngrok (Easiest)**
```bash
# Install ngrok
brew install ngrok

# Start your backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# In another terminal, expose it
ngrok http 8000
# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

**Option B: Use Cloudflare Tunnel (Free, Permanent)**
```bash
# Install cloudflared
brew install cloudflare/cloudflare/cloudflared

# Create tunnel
cloudflared tunnel create quant-backend
cloudflared tunnel route dns quant-backend your-domain.com
cloudflared tunnel run quant-backend
```

### Step 2: Update Backend CORS

Create `backend/.env`:
```env
DEBUG=false
CORS_ORIGINS=["https://your-frontend.vercel.app"]
```

### Step 3: Deploy Frontend to Vercel

1. Same as Option 2, Step 2
2. But set `NEXT_PUBLIC_API_URL` to your ngrok/Cloudflare URL

---

## 🔧 Environment Variables Reference

### Backend (Railway or .env file):
```env
DEBUG=false
CORS_ORIGINS=["https://your-frontend.vercel.app"]
DATA_CACHE_MINUTES=30
MAX_WORKERS=10
DEFAULT_UNIVERSE=sp500
```

### Frontend (Vercel or .env.local):
```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

---

## ✅ Testing After Deployment

1. **Test Backend:** Visit `https://your-backend.railway.app/health`
2. **Test Frontend:** Visit your Vercel URL
3. **Check Connection:** Open browser console, should see "Connected" in logs

---

## 💰 Cost

- **Vercel:** Free (Hobby plan)
- **Railway:** Free tier (500 hours/month) or $5/month
- **Total:** $0-5/month

---

## 🆘 Troubleshooting

**CORS Errors:**
- Make sure `CORS_ORIGINS` includes your exact frontend URL
- No trailing slashes
- Check browser console for exact error

**API Not Connecting:**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Test backend health endpoint directly
- Check Railway logs

**Build Fails:**
- Check Node.js version (Vercel uses 18.x)
- Check Python version (Railway uses 3.11+)
- Review build logs

---

For detailed instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md)

