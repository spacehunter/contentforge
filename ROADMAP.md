# ContentForge Development Roadmap

> AI-powered content generation SaaS for brands
> Target monetization: $1K-5K MRR (Starter $49/mo, Pro $149/mo, Enterprise custom)

---

## ✅ HOUR 1: Foundation (2025-04-28)
- [x] Project scaffold (Next.js 15 + FastAPI)
- [x] Backend: database models (User, Brand, ContentPiece, Subscription)
- [x] Backend: auth endpoints (register, login, JWT)
- [x] Backend: brand CRUD + content generation placeholder + subscription plans
- [x] Frontend: dashboard shell (sidebar, layout)
- [x] Frontend: pages — Brands, Generate, Content Library, Analytics, Settings
- [x] Frontend: API client layer + Zustand store

## ✅ HOUR 2: Auth & Routing (2025-04-28)
- [x] NextAuth v5 installed (next-auth@5.0.0-beta.31)
- [x] Auth provider with credentials strategy (login + auto-register flow)
- [x] /api/auth/[...nextauth] route
- [x] middleware.ts for protected /dashboard/* routes
- [x] /login page with mode toggle (login ↔ register)
- [x] Dashboard layout rewrite with useSession integration
- [x] / page simplified to landing with CTA links
- [x] CORS extended for localhost/127.0.0.1

## ✅ HOUR 3: Local LLM Integration
- [x] /content/generate endpoint calls LM Studio (localhost:1234/v1/chat/completions)
- [x] Content type prompt templates (blog, social, email, pinterest)
- [x] Brand voice injection (prepend brand.voice to prompt)
- [o] Streaming response from LLM to frontend (deferred: sync ok for alpha)
- [x] Save generated content to DB with user_id, brand_id

## ✅ HOUR 4: Image Generation Pipeline (2026-04-28)
tasks:
- [x] Add `POST /content/generate-image` endpoint calling ComfyUI (localhost:8188)
- [x] Flux/Stable Diffusion workflow with KSampler in `comfyui_service.py`
- [x] Pinterest pin, hero banner, and before/after templates with dimension presets
- [x] Image storage: backend saves output to `/images/` static mount
- [x] Frontend `/dashboard/generate-image` page with brand picker, template selector, prompt form, and image preview
- [x] Zustand store updated for image content pieces

## ✅ HOUR 5: Publishing & Scheduling (2026-04-28)
tasks:
- [x] Pinterest API v5 integration (OAuth, publish pin)
- [x] Blog publishing to WordPress via REST API
- [ ] Email draft to Mailchimp/SendGrid (optional, deferred)
- [ ] Scheduler: cron-like job queuing (APScheduler or custom, deferred)

## ✅ HOUR 6: Stripe Billing (2026-04-29)
tasks:
- [x] Stripe Checkout: Starter ($49/mo) + Pro ($149/mo) endpoints wired
- [x] Webhook endpoint `/billing/webhook` for subscription events
- [x] Subscription guards on API endpoints (free 1 brand / 3 pieces, starter/pro limits)
- [x] Upgrade/downgrade flow in Settings page (checkout + portal buttons)
- [ ] Connect real Stripe account + configure PRICE_ID env vars (setup step)

## ✅ HOUR 7: Analytics Dashboard
tasks:
- [x] ContentPiece aggregation by type, status
- [x] Daily/monthly trend charts
- [x] Bar charts for content by type, status
- [x] Recent activity feed
- [ ] Export to CSV (deferred)

## HOUR 8: Polish & Deploy
tasks:
- [x] Docker Compose: backend (FastAPI + uvicorn), frontend (Next.js standalone), nginx
- [x] Environment config: .env for API keys, Stripe, DB URL (.env.example)
- [x] Frontend build fixes (duplicate billing export, duplicate generate_image_endpoint)
- [x] Seed script: demo user + demo brand
- [x] GitHub repo push + README for reproducibility

## ✅ HOUR 9: Growth / Monetization

tasks:
- [x] **Waitlist landing page (public, no auth)** — Rewrite `frontend/app/page.tsx` with waitlist form, features grid, pricing cards. Add `POST /waitlist`, `GET /waitlist/count`, `GET /waitlist/admin` to `backend/main.py`. Add `WaitlistEntry` model to `backend/models.py`.
- [x] **Email automation: welcome + content tips** — Add `email_service.py` using local SMTP or SendGrid. Trigger welcome email on `/auth/register`. Trigger "content tip" weekly email to all users with `is_active=True`.
- [x] **Affiliate / referral code system** — Add `referral_code` to `User` model. Create `/referral/track` endpoint. Give referrer 10 bonus pieces when referred user signs up. Frontend: settings page shows referral link + stats; login page accepts optional referral code.
- [x] **Demo mode: generate 3 pieces free, then paywall** — Check `plan_id` in `enforce_plan_limit`. Free gets 1 brand, 3 pieces. Show upgrade modal in dashboard after hitting limit.
- [ ] **Documentation site (/docs)** — Add `/docs` static route with markdown pages: Quick Start, API Reference, Brand Voice Guide. Use `rehype-remark` or plain HTML.

## BLOCKERS
- None

## Next Actions (Auto-Dev)
Each hour reads ROADMAP.md top, executes next un-[ ] task, commits git.
