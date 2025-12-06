# 🚀 Quick Start Guide

## Starting the Application

You have **3 options** to start the servers:

### Option 1: Start Everything at Once (Easiest) ⭐

```bash
./start-all.sh
```

This will:
- Start the backend server (port 8000)
- Start the frontend server (port 3000)
- Open both in separate terminal windows

Then open: **http://localhost:3000**

---

### Option 2: Start Servers Separately

**Terminal 1 - Backend:**
```bash
./start-backend.sh
```

**Terminal 2 - Frontend:**
```bash
./start-frontend.sh
```

Then open: **http://localhost:3000**

---

### Option 3: Manual Start

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## ✅ Verify Everything is Running

1. **Backend Health Check:** http://localhost:8000/health
   - Should return: `{"status": "healthy", ...}`

2. **Frontend:** http://localhost:3000
   - Should show the dashboard

3. **API Docs:** http://localhost:8000/docs
   - Interactive API documentation

---

## 🛑 Stopping the Servers

- Press `Ctrl+C` in each terminal window
- Or close the terminal windows

---

## ❓ Troubleshooting

### "Port already in use"
- Backend (8000): Another process is using port 8000
  ```bash
  lsof -ti:8000 | xargs kill -9  # Kill process on port 8000
  ```
- Frontend (3000): Another process is using port 3000
  ```bash
  lsof -ti:3000 | xargs kill -9  # Kill process on port 3000
  ```

### "Command not found: ./start-all.sh"
- Make scripts executable:
  ```bash
  chmod +x start-*.sh
  ```

### Frontend can't connect to backend
- Make sure backend is running: http://localhost:8000/health
- Check browser console (F12) for errors
- Verify both are on correct ports

### "Module not found" errors
- Backend: `cd backend && pip install -r requirements.txt`
- Frontend: `cd frontend && npm install`

---

## 📝 Notes

- **First time setup:** Scripts will automatically install dependencies
- **Keep servers running:** Don't close terminal windows while using the app
- **Auto-reload:** Both servers auto-reload when you change code
- **Data caching:** Backend caches data for 30 minutes

---

## 🎯 Next Steps

Once both servers are running:
1. Open http://localhost:3000
2. Select a universe (try `sp50` first)
3. Choose a model
4. Click "Run Model"
5. View results!

---

**Need help?** Check the main [README.md](./README.md) for more details.

