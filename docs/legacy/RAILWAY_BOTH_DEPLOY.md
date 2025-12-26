# 🚂 Deploy Both Frontend & Backend on Railway

## ✅ Yes, It's Possible!

You can host **both frontend and backend on Railway**. This guide will walk you through the complete setup.

---

## 📋 Prerequisites

1. **GitHub Account** - [github.com](https://github.com)
2. **Railway Account** - [railway.app](https://railway.app) (sign up with GitHub)
3. **Railway CLI** - We'll install this together

---

## 🚀 Step-by-Step Deployment

### Step 1: Prepare GitHub Repository

The project is already set up. We just need to:

1. **Initialize Git** (if not done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Quant Stock Analysis Platform"
   ```

2. **Create GitHub Repository:**
   - Go to [github.com/new](https://github.com/new)
   - Repository name: `quant-thai-stocks` (or any name you like)
   - Description: "Quantitative Stock Analysis Platform for US and Thai Stocks"
   - Choose: **Public** or **Private**
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
   - Click "Create repository"

3. **Push to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/quant-thai-stocks.git
   git branch -M main
   git push -u origin main
   ```
   (Replace `YOUR_USERNAME` with your GitHub username)

---

### Step 2: Install Railway CLI

```bash
# Install Railway CLI globally
npm install -g @railway/cli

# Or using Homebrew (macOS)
brew install railway

# Login to Railway
railway login
```

This will open your browser to authenticate with Railway.

---

### Step 3: Deploy Backend to Railway

1. **Create Railway Project:**
   ```bash
   cd backend
   railway init
   ```
   - Select "Create a new project"
   - Project name: `quant-stocks-backend` (or any name)

2. **Link to GitHub (Optional but Recommended):**
   - Go to Railway dashboard
   - Click on your project
   - Click "Settings" → "Connect GitHub Repo"
   - Select your repository
   - Set **Root Directory:** `backend`

3. **Set Environment Variables:**
   ```bash
   railway variables set DEBUG=false
   railway variables set CORS_ORIGINS='["*"]'
   ```
   
   Or in Railway dashboard:
   - Go to your backend service
   - Click "Variables" tab
   - Add:
     - `DEBUG=false`
     - `CORS_ORIGINS=["*"]` (we'll update this after frontend deploys)

4. **Deploy:**
   ```bash
   railway up
   ```
   
   Or if connected to GitHub, just push:
   ```bash
   git push
   ```

5. **Get Backend URL:**
   - Railway will generate a URL like: `https://your-backend.up.railway.app`
   - Copy this URL - you'll need it for the frontend

6. **Test Backend:**
   - Visit: `https://your-backend.up.railway.app/health`
   - Should return: `{"status": "healthy", ...}`

---

### Step 4: Deploy Frontend to Railway

1. **Create New Service:**
   ```bash
   cd ../frontend
   railway link
   ```
   - Select your existing project (same one as backend)
   - This creates a new service in the same project

2. **Or Create via Dashboard:**
   - Go to Railway dashboard
   - Click on your project
   - Click "+ New" → "GitHub Repo"
   - Select the same repository
   - Set **Root Directory:** `frontend`

3. **Set Environment Variables:**
   ```bash
   railway variables set NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
   ```
   
   Or in Railway dashboard:
   - Go to your frontend service
   - Click "Variables" tab
   - Add:
     - `NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app`
     - (Use the backend URL from Step 3)

4. **Deploy:**
   ```bash
   railway up
   ```

5. **Get Frontend URL:**
   - Railway will generate a URL like: `https://your-frontend.up.railway.app`
   - Copy this URL

6. **Update Backend CORS:**
   - Go back to backend service → Variables
   - Update `CORS_ORIGINS`:
     ```
     CORS_ORIGINS=["https://your-frontend.up.railway.app"]
     ```
   - Railway will auto-redeploy

7. **Test Frontend:**
   - Visit: `https://your-frontend.up.railway.app`
   - Should see your app!

---

## 🔧 Railway CLI Commands Reference

```bash
# Login
railway login

# Initialize project
railway init

# Link to existing project
railway link

# Deploy
railway up

# View logs
railway logs

# Open in browser
railway open

# Set environment variable
railway variables set KEY=value

# List variables
railway variables

# View service status
railway status
```

---

## 📊 Project Structure on Railway

Your Railway project will have **2 services**:

```
Railway Project: quant-stocks
├── Service 1: Backend
│   ├── Root: backend/
│   ├── Port: $PORT (auto-assigned)
│   └── URL: https://backend-xxx.up.railway.app
│
└── Service 2: Frontend
    ├── Root: frontend/
    ├── Port: $PORT (auto-assigned)
    └── URL: https://frontend-xxx.up.railway.app
```

---

## 💰 Cost Estimate

**Railway Free Tier:**
- 500 hours/month per service
- $5 credit/month
- **2 services = 2x usage**

**For this project:**
- **Free tier:** Usually enough for light usage
- **If exceeded:** ~$5/month per service = **$10/month total**

**Tip:** If you want to save, use Vercel for frontend (free) and Railway for backend ($0-5/month).

---

## 🔄 Updating Your App

### Automatic Deployments (Recommended)

1. **Connect to GitHub:**
   - In Railway dashboard, connect your GitHub repo
   - Railway will auto-deploy on every push

2. **Push changes:**
   ```bash
   git add .
   git commit -m "Update app"
   git push
   ```
   - Railway automatically deploys both services

### Manual Deployments

```bash
# Deploy backend
cd backend
railway up

# Deploy frontend
cd frontend
railway up
```

---

## 🛠 Troubleshooting

### Backend won't start

1. **Check logs:**
   ```bash
   railway logs --service backend
   ```

2. **Check Root Directory:**
   - Must be set to `backend` in Railway settings

3. **Check Python version:**
   - Railway uses Python 3.11+ by default
   - Add to `backend/runtime.txt` if needed:
     ```
     python-3.11
     ```

### Frontend won't start

1. **Check logs:**
   ```bash
   railway logs --service frontend
   ```

2. **Check Root Directory:**
   - Must be set to `frontend` in Railway settings

3. **Check Node version:**
   - Railway uses Node 18+ by default
   - Add to `frontend/.nvmrc` if needed:
     ```
     18
     ```

4. **Check environment variables:**
   - `NEXT_PUBLIC_API_URL` must be set
   - Must point to your backend URL

### CORS Errors

1. **Check CORS_ORIGINS:**
   - Must include your frontend URL exactly
   - No trailing slashes
   - Use JSON array format: `["https://your-frontend.up.railway.app"]`

2. **Check browser console:**
   - Look for exact CORS error message

### Build Fails

1. **Check build logs:**
   - Railway dashboard → Service → Deployments → View logs

2. **Common issues:**
   - Missing dependencies in `requirements.txt` or `package.json`
   - Wrong Python/Node version
   - Build timeout (increase in Railway settings)

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Backend health check works: `https://your-backend.up.railway.app/health`
- [ ] Frontend loads: `https://your-frontend.up.railway.app`
- [ ] Frontend can connect to backend (check browser console)
- [ ] No CORS errors in browser console
- [ ] Models can run successfully
- [ ] Data fetching works

---

## 🎉 Success!

Once everything is deployed:

- **Backend URL:** `https://your-backend.up.railway.app`
- **Frontend URL:** `https://your-frontend.up.railway.app`
- **Access from anywhere:** Yes! Any computer can access these URLs
- **HTTPS:** Included automatically
- **Auto-deploy:** Enabled (if connected to GitHub)

---

## 📝 Quick Reference

**Backend Service:**
- Root: `backend/`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Env vars: `DEBUG`, `CORS_ORIGINS`

**Frontend Service:**
- Root: `frontend/`
- Start: `npm start`
- Env vars: `NEXT_PUBLIC_API_URL`

---

Need help? Check Railway logs or the main [README.md](./README.md)

