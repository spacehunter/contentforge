# ContentForge

AI-powered content generation SaaS for brands.

## Architecture
- **Frontend**: Next.js 15 (standalone), React 19, Tailwind CSS 4, Zustand, NextAuth v5
- **Backend**: FastAPI + SQLAlchemy, SQLite, Stripe, Pinterest API, WordPress REST
- **AI**: Local LLM via LM Studio (localhost:1234), Image gen via ComfyUI (localhost:8188)
- **Auth**: JWT (backend) + NextAuth (frontend)

## Quick Start

### Prerequisites
- Python 3.11+ with `uv`
- Node.js 22+
- LM Studio running on port 1234
- ComfyUI running on port 8188 (optional, for image gen)

### 1. Backend
```bash
cd backend
uv sync  # or pip install -e .
python scripts/seed.py
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev  # localhost:3000
```

### 3. Stripe (optional, for billing)
```bash
# Set env vars
export STRIPE_SECRET_KEY=sk_test_...
export STRIPE_WEBHOOK_SECRET=whsec_...
export STRIPE_PRICE_STARTER=price_...
export STRIPE_PRICE_PRO=price_...
```

### 4. Demo Login
```
Email: demo@contentforge.local
Password: demo123
```

## Docker Compose
```bash
# Copy .env and fill in your keys
cp .env.example .env
# Build and run
docker-compose up --build
```

## Revenue Model
- **Free**: Trial only
- **Starter**: $49/mo — 5 brands, 100 pieces/mo
- **Pro**: $149/mo — Unlimited brands + AI images
- **Enterprise**: Custom white-label

## Roadmap
See [ROADMAP.md](./ROADMAP.md) for hour-by-hour build plan.

## License
MIT
