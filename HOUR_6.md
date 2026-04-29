# Hour 6: Stripe Billing (2026-04-28)

## Completed
- [x] Stripe Checkout: Starter ($49/mo) + Pro ($149/mo)
- [x] Webhook endpoint for subscription events
- [x] Subscription guards on API endpoints
- [x] Upgrade/downgrade flow in Settings

## Files Added
- backend/stripe_service.py — Stripe client wrapper
- .env.example — Environment variable template

## Files Modified
- backend/main.py — Billing endpoints, plan gating
- frontend/lib/api.ts — billing.* API methods
- frontend/app/dashboard/settings/page.tsx — Checkout/portal UI

## API Endpoints
- POST /billing/checkout
- GET /billing/subscription
- POST /billing/portal
- POST /billing/webhook

## Plan Limits
- Free: 0 brands, 0 pieces, 0 images
- Starter: 5 brands, 100 pieces/mo (no images)
- Pro: Unlimited
