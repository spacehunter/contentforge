import os
import stripe

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_STARTER_PRICE_ID = os.getenv("STRIPE_STARTER_PRICE_ID")
STRIPE_PRO_PRICE_ID = os.getenv("STRIPE_PRO_PRICE_ID")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

PLAN_PRICES = {
    "starter": STRIPE_STARTER_PRICE_ID,
    "pro": STRIPE_PRO_PRICE_ID,
}
PLAN_HIERARCHY = {"free": 0, "starter": 1, "pro": 2, "enterprise": 3}

def ensure_stripe_configured():
    if not STRIPE_SECRET_KEY:
        raise RuntimeError("STRIPE_SECRET_KEY not configured")

def get_or_create_customer(email: str, name: str = None, stripe_customer_id: str = None) -> str:
    ensure_stripe_configured()
    if stripe_customer_id:
        try:
            cust = stripe.Customer.retrieve(stripe_customer_id)
            if cust and not cust.get("deleted"):
                return stripe_customer_id
        except Exception:
            pass
    customers = stripe.Customer.list(email=email, limit=1)
    if customers.data:
        return customers.data[0].id
    new_customer = stripe.Customer.create(email=email, name=name or email.split("@")[0])
    return new_customer.id

def create_checkout_session(customer_id: str, plan_id: str, success_url: str, cancel_url: str):
    ensure_stripe_configured()
    price_id = PLAN_PRICES.get(plan_id)
    if not price_id:
        raise ValueError(f"Unknown plan_id: {plan_id}. Set STRIPE_{plan_id.upper()}_PRICE_ID env var.")
    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"plan_id": plan_id},
    )
    return session

def create_portal_session(customer_id: str, return_url: str):
    ensure_stripe_configured()
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session

def get_subscription_info(stripe_customer_id: str):
    ensure_stripe_configured()
    subs = stripe.Subscription.list(customer=stripe_customer_id, status="all", limit=1)
    if not subs.data:
        return None
    s = subs.data[0]
    items = s.get("items", {}).get("data", [])
    price_id = items[0].get("price", {}).get("id") if items else None
    plan_id = None
    for pid, val in PLAN_PRICES.items():
        if val == price_id:
            plan_id = pid
            break
    return {
        "subscription_id": s.get("id"),
        "status": s.get("status"),
        "plan_id": plan_id or "unknown",
        "current_period_end": s.get("current_period_end"),
        "cancel_at_period_end": s.get("cancel_at_period_end"),
    }

def construct_event(payload: bytes, sig_header: str):
    if not STRIPE_WEBHOOK_SECRET:
        raise RuntimeError("STRIPE_WEBHOOK_SECRET not configured")
    return stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
