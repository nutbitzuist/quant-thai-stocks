# Deployment Guide

This guide covers deploying the Quant Stock Analysis Platform to production.

## 🎯 Deployment Options

### Option 1: Frontend on Vercel + Backend on Mac Mini (Local)

**Pros:**
- Free frontend hosting
- Backend stays local (no hosting costs)
- Full control over backend

**Cons:**
- Mac Mini must be always on
- Requires public IP/domain setup
- Security considerations
- Home internet reliability

**Setup Steps:**

1. **Expose Backend Publicly:**
   - Use a service like [ngrok](https://ngrok.com/) or [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
   - Or set up port forwarding on your router
   - Get a static IP or use dynamic DNS (e.g., DuckDNS)

2. **Update Frontend API URL:**
   - Set `NEXT_PUBLIC_API_URL` environment variable in Vercel
   - Point to your public backend URL (e.g., `https://your-domain.com` or `https://your-ngrok-url.ngrok.io`)

3. **Update Backend CORS:**
   - Add your Vercel frontend URL to `CORS_ORIGINS` in backend `.env`
   - Example: `CORS_ORIGINS=["https://your-app.vercel.app"]`

---

### Option 2: Both on Railway (Recommended) ⭐

**Pros:**
- Always available
- No Mac Mini dependency
- Better reliability
- Automatic HTTPS
- Free tier available

**Setup Steps:**

#### Backend on Railway:

1. **Create Railway Account:**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your repository

3. **Configure Backend:**
   - Railway will auto-detect Python
   - Set root directory: `backend`
   - Add environment variables:
     ```
     DEBUG=false
     CORS_ORIGINS=["https://your-frontend.vercel.app"]
     ```

4. **Deploy:**
   - Railway will automatically deploy
   - Get your backend URL (e.g., `https://your-backend.railway.app`)

#### Frontend on Vercel:

1. **Create Vercel Account:**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub

2. **Import Project:**
   - Click "Add New Project"
   - Import your GitHub repository
   - Set root directory: `frontend`

3. **Configure Environment Variables:**
   - Add: `NEXT_PUBLIC_API_URL=https://your-backend.railway.app`
   - (Replace with your actual Railway backend URL)

4. **Deploy:**
   - Vercel will automatically deploy
   - Your app will be live!

---

## 🔧 Configuration Changes Needed

### Frontend Environment Variables

Create `frontend/.env.local` (for local) or set in Vercel dashboard:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production (Vercel), set:
```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

### Backend Environment Variables

Create `backend/.env`:

```env
DEBUG=false
CORS_ORIGINS=["https://your-frontend.vercel.app","http://localhost:3000"]
DATA_CACHE_MINUTES=30
MAX_WORKERS=10
DEFAULT_UNIVERSE=sp500
```

---

## 📝 Files Created for Deployment

- `railway.json` - Railway configuration
- `Procfile` - Process file for Railway
- `vercel.json` - Vercel configuration (if needed)
- `.env.example` - Example environment variables

---

## 🚀 Quick Deploy Commands

### Railway (Backend):
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

### Vercel (Frontend):
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel
```

---

## 🔒 Security Notes

1. **Never commit `.env` files** - They're in `.gitignore`
2. **Use environment variables** in Railway/Vercel dashboards
3. **Enable HTTPS** - Both platforms do this automatically
4. **Limit CORS origins** - Don't use `["*"]` in production
5. **Set DEBUG=false** in production

---

## 🐛 Troubleshooting

### CORS Errors:
- Check `CORS_ORIGINS` includes your frontend URL
- Ensure no trailing slashes in URLs
- Check browser console for exact error

### API Connection Issues:
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check backend logs in Railway dashboard
- Test backend health endpoint directly

### Build Errors:
- Check Node.js version (Vercel uses 18.x by default)
- Check Python version (Railway uses 3.11+)
- Review build logs in platform dashboards

---

## 💰 Cost Estimate

**Option 1 (Frontend Vercel + Backend Local):**
- Frontend: Free (Vercel Hobby)
- Backend: Free (your Mac Mini)
- **Total: $0/month**

**Option 2 (Both on Railway/Vercel):**
- Frontend: Free (Vercel Hobby)
- Backend: Free tier (Railway) - 500 hours/month
- **Total: $0-5/month** (depending on usage)

---

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)

