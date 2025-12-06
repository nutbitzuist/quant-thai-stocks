# Quant Stock Analysis Platform v2.0

A quantitative analysis platform for **US (S&P 500)** and **Thai (SET100)** stocks with **10 models** including CANSLIM, Minervini, Darvas Box, Turtle Trading, and more.

## 🚀 Quick Start

### Easiest Way (Recommended) ⭐

```bash
./start-all.sh
```

This starts both servers automatically. Then open: **http://localhost:3000**

---

### Manual Start

**Option 1: Use convenience scripts**

```bash
# Terminal 1 - Backend
./start-backend.sh

# Terminal 2 - Frontend  
./start-frontend.sh
```

**Option 2: Manual commands**

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

✅ **Check Status:** `./check-status.sh` to see if servers are running

✅ **Test Backend:** http://localhost:8000/health

✅ **Open Frontend:** http://localhost:3000

📖 **For detailed instructions, see [START_HERE.md](./START_HERE.md)**

---

## 📊 10 Models Included

### Technical Models (6)
| Model | Strategy | Best For |
|-------|----------|----------|
| **RSI Reversal** | Buy RSI < 30, Sell RSI > 70 | Mean reversion |
| **MACD Crossover** | Buy on bullish crossover | Trend following |
| **Minervini Trend** | Stage 2 uptrend criteria | Growth stocks |
| **Darvas Box** | Buy breakouts from boxes | Breakout trading |
| **Turtle Trading** | 55-day high breakout | Trend following |
| **Elder Triple Screen** | Multi-timeframe + Force Index | Pullback entries |

### Fundamental Models (4)
| Model | Strategy | Best For |
|-------|----------|----------|
| **CANSLIM** | William O'Neil's 7 criteria | Growth investing |
| **Value Composite** | P/E, P/B, P/S, Dividend | Value investing |
| **Quality Score** | ROE, ROA, margins, debt | Quality focus |
| **Piotroski F-Score** | 9-point financial strength | Deep value |

---

## 🌐 Universes

| Universe | Market | Stocks | Description |
|----------|--------|--------|-------------|
| `sp50` | US | ~35 | Mega-cap US stocks (most reliable data) |
| `sp500` | US | ~80 | Large-cap US stocks |
| `set50` | Thailand | ~35 | Thai large-cap stocks |
| `set100` | Thailand | ~60 | Thai mid-large cap stocks |

**Tip**: Start with `sp50` to test - it has the most reliable Yahoo Finance data.

---

## 🔧 Troubleshooting

### Backend won't start?
```bash
# Make sure you're in the backend folder
cd backend

# Install dependencies
pip install -r requirements.txt

# Try running with explicit python
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend can't connect to backend?
1. Check backend is running: http://localhost:8000/health
2. Check browser console for errors (F12)
3. Make sure both are on correct ports (backend: 8000, frontend: 3000)

### Model returns no results?
- Thai stocks may have limited data on Yahoo Finance
- Try S&P 50 universe first to verify everything works
- Check the **Status & Logs** tab for errors

### Data is slow?
- Yahoo Finance rate limits requests
- First run takes 1-3 minutes (fetching ~50 stocks)
- Subsequent runs use cache (30 min)

---

## 📁 Project Structure

```
quant-thai-stocks/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # API endpoints
│   │   │   ├── models.py    # Run models
│   │   │   ├── universe.py  # Stock lists
│   │   │   └── status.py    # Health/debugging
│   │   ├── data/
│   │   │   ├── fetcher.py   # Yahoo Finance data
│   │   │   └── universe.py  # Stock definitions
│   │   ├── models/
│   │   │   ├── technical/   # 6 technical models
│   │   │   └── fundamental/ # 4 fundamental models
│   │   ├── main.py          # FastAPI app
│   │   └── config.py
│   └── requirements.txt
│
└── frontend/
    └── src/app/
        └── page.tsx         # Main dashboard
```

---

## 🛠 API Endpoints

### Models
- `GET /api/models/` - List all models
- `POST /api/models/run` - Run a model
- `GET /api/models/run-quick/{model_id}?universe=sp50` - Quick run

### Status (Debugging)
- `GET /api/status/test-connection` - Check if backend works
- `GET /api/status/test-data` - Test data fetching with AAPL
- `GET /api/status/logs` - View recent errors

### Universe
- `GET /api/universe/` - List available universes
- `GET /api/universe/{id}` - Get universe details

---

## 🔮 Future Enhancements

- [ ] VectorBT integration for backtesting
- [ ] SETTRADE API for real-time Thai data
- [ ] Email/LINE alerts for signals
- [ ] Portfolio tracking
- [ ] More models (Earnings Momentum, Growth Score)
- [ ] Custom universe creation

---

## 📝 Notes

- **Data Source**: Yahoo Finance (free, 15-20 min delay)
- **Thai Stocks**: Use `.BK` suffix (e.g., `PTT.BK`)
- **Cache**: Data cached for 30 minutes
- **Python**: Requires Python 3.10+
- **Node.js**: Requires Node 18+

---

## 🙋 Need Help?

1. Check the **Status & Logs** tab in the frontend
2. Test backend directly: http://localhost:8000/docs
3. Check terminal output for errors

Built for institutional equity sales professionals.
