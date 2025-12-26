# QuantStack

**Professional Stock Screening for Retail Traders**

Screen US and Thai stocks using 27 institutional-grade quantitative models including CANSLIM, Minervini, Piotroski, and more.

---

## Quick Start

```bash
./start-all.sh
```

Then open: **http://localhost:3000**

---

## Documentation

| Document | Description |
|----------|-------------|
| [PRD.md](./docs/PRD.md) | Product requirements |
| [SPEC.md](./docs/SPEC.md) | Technical architecture |
| [TASKS.md](./docs/TASKS.md) | Task tracker |
| [DECISIONS.md](./docs/DECISIONS.md) | Architecture decisions |
| [TEST_PLAN.md](./docs/TEST_PLAN.md) | Test plan |
| [ENGINEERING_STANDARD.md](./docs/ENGINEERING_STANDARD.md) | Code standards |

> Legacy docs moved to [docs/legacy](./docs/legacy/)

---

## Environment Variables

### Frontend (`frontend/.env.local`)

```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
CLERK_SECRET_KEY
NEXT_PUBLIC_API_URL
```

### Backend (`backend/.env`)

```
DEBUG
CORS_ORIGINS
```

---

## Project Structure

```
quant-thai-stocks/
├── backend/                 # FastAPI Python backend
│   └── app/
│       ├── api/routes/     # API endpoints
│       ├── models/         # 27 screening models
│       └── services/       # Backtest, PDF, reports
├── frontend/               # Next.js React frontend
│   └── src/
│       ├── types/          # TypeScript types
│       └── app/
│           ├── dashboard/  # Main app
│           ├── admin/      # Admin panel
│           └── components/ # Shared components
└── docs/                   # Documentation
```

---

## Deployment

```bash
# Frontend → Vercel
cd frontend && vercel --prod

# Backend → Railway
cd backend && railway up --detach
```

---

## Requirements

- Python 3.10+
- Node.js 18+
