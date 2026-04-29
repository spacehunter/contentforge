# ContentForge — AI Content That Sounds Like Your Brand

> Stop sounding generic. Generate blogs, social posts, Pinterest pins, and full campaign assets that carry your brand voice — not a chatbot's.

## What is ContentForge?

ContentForge is an on-device AI content generation platform that lets you create marketing assets for your brands without losing your voice. Unlike ChatGPT or Jasper, where every result sounds the same, ContentForge trains on **your** brand voice, industry, and target audience — then generates content that sounds like you wrote it.

It runs entirely on your own hardware (NVIDIA DGX Spark / local GPU). **No API keys. No token costs. No cloud dependency.** Everything from text generation (via LM Studio) to image creation (via ComfyUI/Flux) happens locally.

## Who is it for?

- **Solo marketers & creators** who manage multiple brands and hate rewriting the same voice prompts over and over
- **Agencies** who need consistent output across client accounts
- **Bootstrapped SaaS founders** who want a Stripe-ready content engine they can white-label
- **Privacy-conscious teams** who can't send customer data to OpenAI or Anthropic

## What problem does it solve?

| Before ContentForge | After ContentForge |
|---------------------|---------------------|
| Copy-paste ChatGPT outputs that sound like everyone else | Every piece reads in your brand's exact tone and style |
| Manually rewriting AI drafts for hours | Hit generate, publish, done |
| Switching between Jasper, Canva, and Pinterest separately | One dashboard: text + image + publish to WordPress/Pinterest |
| Burning $$$ on API tokens every month | Runs 100% on your hardware — zero per-token costs |
| Scattered brand guidelines in Google Docs | Brand voice profiles saved permanently, injected into every prompt |

## Key Features

- **Brand Voice Training** — Define your tone, industry, target audience once. The AI remembers it for every generation.
- **Multi-Content Generation** — Blogs, social posts, email sequences, Pinterest pins, hero banners, before/after visuals.
- **AI Image Generation** — Integrated ComfyUI/Flux pipeline for Pinterest-optimized, hero banner, and marketing visuals.
- **One-Click Publishing** — Push content directly to WordPress blogs and Pinterest boards without leaving the app.
- **Analytics Dashboard** — Track content output by type, brand, and time period. Monthly trends and usage stats built-in.
- **Built-in Monetization** — Stripe Checkout pre-wired with Starter ($49/mo) and Pro ($149/mo) plans. Subscription limits enforced at the API level.
- **Waitlist System** — Public landing page with email capture and admin dashboard for managing early access.
- **On-Device AI** — All LLM inference via LM Studio, all image gen via ComfyUI. No cloud AI bills.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          ContentForge                                │
├──────────────────────┬──────────────────────────────────────────────┤
│  Frontend (Next.js)  │  Backend (FastAPI)                           │
│  ├─ React 19         │  ├─ Auth (JWT + NextAuth v5)                 │
│  ├─ Tailwind CSS 4   │  ├─ Brand & Content CRUD                     │
│  ├─ Zustand state    │  ├─ Plan limits & billing guards             │
│  ├─ Waitlist landing │  ├─ Stripe webhooks                          │
│  ├─ Dashboard        │  └─ SQLite database                          │
│  └─ Analytics        │                                              │
│                      │  Integrations                                  │
│                      │  ├─ LM Studio (localhost:1234) — LLM text    │
│                      │  ├─ ComfyUI (localhost:8188) — AI images     │
│                      │  ├─ Pinterest API v5 — pin publishing        │
│                      │  └─ WordPress REST API — blog posts          │
└──────────────────────┴──────────────────────────────────────────────┘
```

- **Frontend**: Next.js 15 (standalone), React 19, Tailwind CSS 4, Zustand, NextAuth v5
- **Backend**: FastAPI + SQLAlchemy, SQLite, Stripe, Pinterest API, WordPress REST
- **AI**: Local LLM via LM Studio (localhost:1234), Image gen via ComfyUI (localhost:8188)
- **Auth**: JWT (backend) + NextAuth (frontend)

## Quick Start

### Prerequisites

- Python 3.11+ with `uv`
- Node.js 22+
- LM Studio running on port 1234 (or set `LM_STUDIO_URL`)
- ComfyUI running on port 8188 (optional, for image gen)

### 1. Clone & Backend Setup

```bash
cd contentforge/backend
uv sync
python scripts/seed.py
uvicorn main:app --host 0.0.0.0 --port 8000
```

The seed script creates a demo user and brand so you can explore immediately.

### 2. Frontend Setup

```bash
cd contentforge/frontend
npm install
npm run dev  # starts on http://localhost:3000
```

### 3. Demo Login

```
Email: demo@contentforge.local
Password: demo123
```

Visit `http://localhost:3000`, sign in with the demo credentials, and start generating content.

### 4. Environment Variables (optional)

Create `backend/.env`:

```bash
# Required for billing
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_STARTER=price_...
STRIPE_PRICE_PRO=price_...

# Optional: override default endpoints
LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
COMFYUI_URL=http://localhost:8188

# Optional: Pinterest publishing
PINTEREST_APP_ID=your_app_id
PINTEREST_APP_SECRET=your_app_secret

# Optional: WordPress publishing
WP_BASE_URL=https://yourblog.com
WP_USERNAME=your_username
WP_APP_PASSWORD=your_app_password
```

### 5. Docker Compose (Production)

```bash
# Copy .env and fill in your keys
cp .env.example .env

# Build and run entire stack
docker-compose up --build
```

Serves the frontend via nginx, backend via uvicorn, and mounts the images directory for persistent storage.

## Your First 5 Minutes

1. **Sign in** with the demo account (`demo@contentforge.local` / `demo123`)
2. **Go to Brands** — see the "Demo Brand" already created with a voice profile
3. **Click "Generate"** — choose "Blog Post", enter a topic, hit generate. The AI injects the brand voice automatically.
4. **Try Image Generation** — switch to the "Generate Image" tab, pick "Pinterest Pin", describe your visual, and create.
5. **Check Analytics** — see your first content piece counted in the dashboard stats.

## Pricing & Monetization

ContentForge is built to be monetized out of the box.

| Plan | Price | What's Included |
|------|-------|-----------------|
| **Free** | $0 | 1 brand, 3 content pieces total. Perfect for trying it out. |
| **Starter** | $49/mo | 5 brands, 100 pieces/month, AI image generation, Pinterest + WordPress publishing |
| **Pro** | $149/mo | Unlimited brands, unlimited pieces, all integrations, priority support |
| **Enterprise** | Custom | White-label deployment, custom models, dedicated support |

Subscription limits are enforced at the API level — free users hit a hard cap after 3 pieces, with a clear upgrade prompt in the UI.

## Roadmap

See [`ROADMAP.md`](./ROADMAP.md) for the hour-by-hour build plan. Currently building Hour 9: email automation, affiliate codes, demo mode enforcement, and a documentation site.

## Built With

- **Next.js 15** — Frontend framework with App Router
- **FastAPI** — Python backend with automatic OpenAPI docs
- **LM Studio** — Local LLM inference server (no cloud LLM costs)
- **ComfyUI** — Image generation with Flux/Stable Diffusion workflows
- **Stripe** — Checkout, billing, and subscription management
- **Zustand** — Lightweight state management
- **Tailwind CSS** — Utility-first styling

## License

MIT
