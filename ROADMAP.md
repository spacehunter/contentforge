# ContentForge Development Roadmap

> AI-powered content generation SaaS for brands
> Target monetization: $1K-5K MRR (Starter $49/mo, Pro $149/mo, Enterprise custom)

---

## ✅ HOUR 1: Foundation (2025-04-28)
- [x] Project scaffold (Next.js 15 + FastAPI)
- [x] Database models (User, Brand, ContentPiece, Subscription)
- [x] Auth endpoints (register, login, JWT)
- [x] Brand CRUD + Content generation placeholder
- [x] Dashboard shell (sidebar, layout)
- [x] Frontend pages: Brands, Generate, Content Library, Analytics, Settings
- [x] API client layer + Zustand store
- [ ] Fix: Zustand store typing, API cors proxy, missing pages

## HOUR 2: Auth & Routing
tasks:
- [ ] Add NextAuth v5 (auth.ts) with credentials provider
- [ ] Fix Zustand hydration mismatch (useStore on server)
- [ ] Add middleware.ts for protected routes
- [ ] Build login/register page as actual route (/login)
- [ ] Fix API CORS for credentials (allow cookies)

## HOUR 3: Local LLM Integration
tasks:
- [ ] /content/generate endpoint calls LM Studio (localhost:1234/v1/chat/completions)
- [ ] Content type prompt templates (blog, social, email, pinterest)
- [ ] Brand voice injection (prepend brand.voice to prompt)
- [ ] Streaming response from LLM to frontend
- [ ] Save generated content to DB with user_id, brand_id

## HOUR 4: Image Generation Pipeline
tasks:
- [ ] /content/generate-image endpoint calls ComfyUI (localhost:8188)
- [ ] Flux/Stable Diffusion workflow for marketing images
- [ ] Pinterest pin layout generation (2:3 vertical + branded text)
- [ ] Before/after style layouts for home services
- [ ] Image storage (save to ./contentforge/static/images, serve via nginx or static)

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
