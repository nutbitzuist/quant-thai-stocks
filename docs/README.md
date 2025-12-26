# QuantStack

**Professional Stock Screening for Retail Traders**

Screen US and Thai stocks using 27 institutional-grade quantitative models including CANSLIM, Minervini, Piotroski, and more.

---

## What This App Does

- **Screen stocks** using 27 pre-built models (technical, fundamental, quantitative)
- **Backtest strategies** with VectorBT to validate performance
- **Analyze individual stocks** with comprehensive metrics
- **Generate PDF reports** with QuantStats analytics
- **Cover multiple markets** (S&P 500, SET100)

---

## Quick Start

### Option 1: Use startup script (Recommended)

```bash
./start-all.sh
```

Then open: **http://localhost:3000**

### Option 2: Manual start

```bash
# Terminal 1 - Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

---

## Environment Variables

### Frontend (`frontend/.env.local`)

```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
CLERK_SECRET_KEY
NEXT_PUBLIC_CLERK_SIGN_IN_URL
NEXT_PUBLIC_CLERK_SIGN_UP_URL
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL
NEXT_PUBLIC_API_URL
```

### Backend (`backend/.env`)

```
DEBUG
CORS_ORIGINS
DATA_CACHE_MINUTES
MAX_WORKERS
DEFAULT_UNIVERSE
DATA_PROVIDERS
```

> **Note**: App works without Clerk keys (auth disabled in dev mode)

---

## Project Structure

```
quant-thai-stocks/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── api/routes/     # 10 API route modules
│   │   ├── models/         # 27 screening models
│   │   ├── services/       # Backtest, PDF, reports
│   │   └── data/           # Data fetching
│   └── requirements.txt
├── frontend/               # Next.js React frontend
│   └── src/app/
│       ├── dashboard/      # Main dashboard
│       ├── admin/          # Admin panel
│       └── components/     # Shared components
└── docs/                   # Documentation
```

---

## How to Run Locally

1. **Clone the repo**
   ```bash
   git clone https://github.com/nutbitzuist/quant-thai-stocks.git
   cd quant-thai-stocks
   ```

2. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

4. **Start both servers**
   ```bash
   ./start-all.sh
   # Or manually in separate terminals
   ```

5. **Open in browser**: http://localhost:3000

---

## How to Deploy

### Frontend → Vercel

```bash
cd frontend
vercel --prod
```

### Backend → Railway

```bash
cd backend
railway link
railway up --detach
```

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /api/models/` | List all models |
| `POST /api/models/run` | Run a model |
| `POST /api/backtest/run` | Run backtest |
| `GET /api/analysis/stock/{ticker}` | Analyze stock |
| `GET /api/universe/` | List universes |

Full API docs: http://localhost:8000/docs

---

## Important Notes

- **Data Source**: Yahoo Finance (15-20 min delay)
- **Thai Stocks**: Use `.BK` suffix (e.g., `PTT.BK`)
- **Cache**: Data cached for 30 minutes
- **Requirements**: Python 3.10+, Node.js 18+
- **First Run**: May take 1-3 min to fetch data

---

## Documentation

- [PRD.md](./docs/PRD.md) - Product requirements
- [SPEC.md](./docs/SPEC.md) - Technical specification
- [TASKS.md](./docs/TASKS.md) - Task tracker
- [DECISIONS.md](./docs/DECISIONS.md) - Architecture decisions
- [TEST_PLAN.md](./docs/TEST_PLAN.md) - Test plan
- [ENGINEERING_STANDARD.md](./docs/ENGINEERING_STANDARD.md) - Engineering standards
