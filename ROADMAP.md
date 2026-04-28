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

## HOUR 4: Image Generation Pipeline
tasks:
- [ ] Add `generate_image()` to `backend/llm_service.py` that POSTs a JSON prompt to ComfyUI at `http://localhost:8188/prompt`, waits via `/history`, and returns the output image path.
- [ ] Add `POST /content/generate-image` endpoint in `backend/main.py` accepting `brand_id`, `prompt`, `template_type` ("pinterest", "hero", "before_after").
- [ ] Create backend prompt templates for each image type (Pinterest pin = vertical 2:3 + text overlay prompt, hero = wide landscape, before_after = split frame).
- [ ] Add image storage: save generated images to `backend/static/images/` and serve static files via FastAPI `app.mount("/images", StaticFiles(...), ...)`. Create the static/images dir.
- [ ] Add an image generation page to the frontend at `frontend/app/dashboard/generate-image/page.tsx` with a form: brand picker, prompt textbox, template selector, and a submit button that displays the returned image URL.

## HOUR 5: Publishing & Scheduling
tasks:
- [ ] Pinterest API v5 integration (OAuth, publish pin)
- [ ] Blog publishing to WordPress via REST API
- [ ] Email draft to Mailchimp/SendGrid (optional)
- [ ] Scheduler: cron-like job queuing (APScheduler or custom)

## HOUR 6: Stripe Billing
tasks:
- [ ] Stripe Checkout: Starter ($49/mo) + Pro ($149/mo)
- [ ] Webhook endpoint for subscription events
- [ ] Subscription guards on API endpoints
- [ ] Upgrade/downgrade flow in Settings

## HOUR 7: Analytics Dashboard
tasks:
- [ ] ContentPiece aggregation by type, brand, status
- [ ] Engagement mock data (or real if publishers exist)
- [ ] Charts: bar (content by type), line (over time), pie (status)
- [ ] Export to CSV

## HOUR 8: Polish & Deploy
tasks:
- [ ] Docker Compose: backend (FastAPI + uvicorn), frontend (Next.js standalone), nginx
- [ ] Environment config: .env for API keys, Stripe, DB URL
- [ ] Frontend build fixes (eslint, types, bundling)
- [ ] Seed script: demo user + demo brand
- [ ] GitHub repo push + README for reproducibility

## HOUR 9+: Growth / Monetization
tasks:
- [ ] Waitlist landing page (public, no auth)
- [ ] Email automation: welcome + content tips
- [ ] Affiliate / referral code system
- [ ] Demo mode: generate 3 pieces free, then paywall
- [ ] Documentation site (/docs)

---

## Revenue Model
| Plan     | Price     | Limits                        |
|----------|-----------|------------------------------|
| Free     | $0        | 3 pieces total (trial)      |
| Starter  | $49/mo    | 5 brands, 100 pieces/mo      |
| Pro      | $149/mo   | Unlimited brands + content   |
| Enterprise| Custom   | White-label + API access     |

## Next Actions (Auto-Dev)
Each hour reads ROADMAP.md top, executes next un-[ ] task, commits git.
