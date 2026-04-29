from fastapi import FastAPI, Depends, HTTPException, status, Header, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
import os

from database import SessionLocal, engine, Base
from models import User, Brand, ContentPiece, Subscription
from llm_service import generate_content as llm_generate
from comfyui_service import generate_image
from pinterest_service import (
    get_oauth_url,
    exchange_code,
    list_boards,
    create_pin,
    get_user,
    delete_pin,
)
from wordpress_service import publish_post, list_posts, test_connection

try:
    from stripe_service import (
        create_checkout_session,
        get_or_create_customer,
        construct_event,
        get_subscription_info,
        create_portal_session,
        PLAN_HIERARCHY,
    )
    STRIPE_ENABLED = True
except Exception:
    STRIPE_ENABLED = False

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ContentForge API", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static images directory
os.makedirs("static/images", exist_ok=True)
app.mount("/images", StaticFiles(directory="static/images"), name="images")

# Config
SECRET_KEY = os.getenv("SECRET_KEY", "contentforge-dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic Models
class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    class Config:
        from_attributes = True

class BrandCreate(BaseModel):
    name: str
    voice: str
    industry: str
    target_audience: str

class ContentGenerateRequest(BaseModel):
    title: str
    content_type: str
    prompt: str
    tone: str = "professional"
    brand_id: Optional[int] = None

class ImageGenerateRequest(BaseModel):
    prompt: str
    template_type: str = "pinterest"  # pinterest, hero, before_after
    brand_id: Optional[int] = None

class ContentResponse(BaseModel):
    id: int
    title: str
    content_type: str
    prompt: str
    generated_text: Optional[str]
    status: str
    brand_id: Optional[int]
    user_id: int
    created_at: datetime
    class Config:
        from_attributes = True

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Token / Auth helpers
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/auth/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        name=user.name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.post("/brands")
def create_brand(brand: BrandCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = get_user_plan(db, current_user)
    enforce_plan_limit(db, current_user, plan, generation_type="brand")
    db_brand = Brand(**brand.dict(), user_id=current_user.id)
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand

@app.get("/brands")
def list_brands(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Brand).filter(Brand.user_id == current_user.id).all()

@app.post("/content/generate", response_model=ContentResponse)
async def generate_content_endpoint(
    req: ContentGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = get_user_plan(db, current_user)
    enforce_plan_limit(db, current_user, plan, generation_type="content")
    # Fetch brand if brand_id provided
    brand = None
    if req.brand_id:
        brand = db.query(Brand).filter(Brand.id == req.brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
    
    # Call LLM
    try:
        generated_text = await llm_generate(
            title=req.title,
            content_type=req.content_type,
            prompt=req.prompt,
            tone=req.tone,
            brand=brand,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
    
    # Save to DB
    db_content = ContentPiece(
        title=req.title,
        content_type=req.content_type,
        prompt=req.prompt,
        generated_text=generated_text,
        status="generated",
        user_id=current_user.id,
        brand_id=req.brand_id,
    )
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

@app.get("/content")
def list_content(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(ContentPiece).filter(ContentPiece.user_id == current_user.id).order_by(ContentPiece.created_at.desc()).all()

@app.get("/subscriptions/plans")
def get_plans():
    return {
        "plans": [
            {
                "id": "starter",
                "name": "Starter",
                "price": 49,
                "features": ["5 brands", "100 content pieces/mo", "Basic analytics"]
            },
            {
                "id": "pro",
                "name": "Pro",
                "price": 149,
                "features": ["Unlimited brands", "Unlimited content", "AI image generation", "Priority support", "Team collaboration"]
            }
        ]
    }

@app.post("/content/generate-image")
async def generate_image_endpoint(
    req: ImageGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = get_user_plan(db, current_user)
    enforce_plan_limit(db, current_user, plan, generation_type="image")
    brand = None
    if req.brand_id:
        brand = db.query(Brand).filter(Brand.id == req.brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")

    try:
        image_url = await generate_image(
            prompt=req.prompt,
            template_type=req.template_type,
            brand_voice=brand.voice if brand else None,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

    db_content = ContentPiece(
        title=f"Generated image - {req.template_type}",
        content_type="image",
        prompt=req.prompt,
        generated_text=image_url,
        status="generated",
        user_id=current_user.id,
        brand_id=req.brand_id,
    )
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return {"id": db_content.id, "image_url": image_url, "template_type": req.template_type, "status": "generated"}

## Pinterest OAuth & Publishing Routes
class PinterestConnect(BaseModel):
    code: str

class PinterestPinCreate(BaseModel):
    content_id: int
    board_id: str
    title: str
    description: str
    link: str = ""

@app.get("/pinterest/auth-url")
def pinterest_auth_url(current_user: User = Depends(get_current_user)):
    """Return the OAuth URL to start Pinterest authorization."""
    if not get_oauth_url(""):
        raise HTTPException(status_code=500, detail="Pinterest OAuth not configured")
    state = str(current_user.id)
    return {"auth_url": get_oauth_url(state)}

@app.post("/pinterest/connect")
async def pinterest_connect(
    payload: PinterestConnect,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Exchange authorization code and store access token."""
    try:
        token_data = await exchange_code(payload.code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Pinterest token exchange failed: {str(e)}")
    
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Pinterest did not return access_token")

    current_user.pinterest_access_token = access_token
    db.commit()
    db.refresh(current_user)
    return {"connected": True, "account": token_data.get("scope", "")}

@app.get("/pinterest/boards")
async def pinterest_boards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List boards of the connected Pinterest account."""
    if not current_user.pinterest_access_token:
        raise HTTPException(status_code=400, detail="Pinterest not connected. Connect first.")
    try:
        boards = await list_boards(current_user.pinterest_access_token)
        return {"boards": boards}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pinterest boards fetch failed: {str(e)}")

@app.get("/pinterest/me")
async def pinterest_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the connected Pinterest user's profile."""
    if not current_user.pinterest_access_token:
        raise HTTPException(status_code=400, detail="Pinterest not connected. Connect first.")
    try:
        user = await get_user(current_user.pinterest_access_token)
        return {"user": user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pinterest user fetch failed: {str(e)}")

@app.post("/pinterest/pin")
async def pinterest_pin_publish(
    req: PinterestPinCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Publish a piece of content as a Pinterest Pin."""
    # Verify Pinterest is connected
    if not current_user.pinterest_access_token:
        raise HTTPException(status_code=400, detail="Pinterest not connected")
    
    # Fetch the content piece
    content = db.query(ContentPiece).filter(ContentPiece.id == req.content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content piece not found")
    if content.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your content")
    
    # Need an image_url for a pin
    image_url = content.image_url or (content.generated_text if content.content_type == "image" else None)
    if not image_url:
        raise HTTPException(status_code=400, detail="Content has no image URL to pin")
    
    # Ensure absolute URL
    if image_url.startswith("/"):
        image_url = f"http://localhost:8000{image_url}"

    try:
        pin_result = await create_pin(
            access_token=current_user.pinterest_access_token,
            board_id=req.board_id,
            title=req.title or content.title,
            description=req.description,
            link=req.link,
            image_url=image_url,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pinterest pin creation failed: {str(e)}")
    
    # Update content status
    content.status = "published"
    content.published_at = datetime.utcnow()
    db.commit()
    db.refresh(content)
    
    return {
        "id": content.id,
        "pinterest_pin_id": pin_result.get("id"),
        "pinterest_url": f"https://pinterest.com/pin/{pin_result.get('id')}",
        "status": "published",
    }

## WordPress Publishing Routes
class WordPressConnect(BaseModel):
    site_url: str
    username: str
    app_password: str

class WordPressPublishRequest(BaseModel):
    content_id: int
    wp_site_url: Optional[str] = None
    wp_username: Optional[str] = None
    wp_app_password: Optional[str] = None
    status: str = "draft"  # 'publish' or 'draft'

@app.post("/wordpress/test")
async def wordpress_test_connection(
    req: WordPressConnect,
    current_user: User = Depends(get_current_user),
):
    """Test WordPress connection with Application Passwords."""
    try:
        me = await test_connection(req.site_url, req.username, req.app_password)
        return {"connected": True, "user": me.get("name"), "slug": me.get("slug")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"WordPress connection failed: {str(e)}")

@app.post("/wordpress/publish")
async def wordpress_publish(
    req: WordPressPublishRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Publish a content piece to WordPress."""
    content = db.query(ContentPiece).filter(ContentPiece.id == req.content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content piece not found")
    if content.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your content")

    # Only text content can be blog posts
    if content.content_type not in ("blog", "social", "email"):
        raise HTTPException(status_code=400, detail="Content type must be blog/social/email to publish to WordPress")

    wp_url = req.wp_site_url or os.getenv("WP_DEFAULT_SITE_URL")
    wp_user = req.wp_username or os.getenv("WP_DEFAULT_USERNAME")
    wp_pass = req.wp_app_password or os.getenv("WP_DEFAULT_APP_PASSWORD")

    if not all([wp_url, wp_user, wp_pass]):
        raise HTTPException(status_code=400, detail="WordPress credentials not provided. Supply wp_site_url, wp_username, wp_app_password or set env vars.")

    try:
        post = await publish_post(
            wp_base_url=wp_url,
            wp_username=wp_user,
            wp_app_password=wp_pass,
            title=content.title,
            content=content.generated_text or content.prompt,
            status=req.status,
            excerpt=content.prompt[:200] if content.prompt else "",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"WordPress publish failed: {str(e)}")

    content.status = "published" if req.status == "publish" else "draft"
    content.published_at = datetime.utcnow()
    db.commit()
    db.refresh(content)

    return {
        "id": content.id,
        "wordpress_post_id": post.get("id"),
        "wordpress_url": post.get("link"),
        "status": content.status,
    }

# ─── Stripe Billing ───
class CheckoutRequest(BaseModel):
    plan_id: str  # "starter" or "pro"

class BillingInfo(BaseModel):
    stripe_customer_id: Optional[str] = None

@app.post("/billing/checkout")
def create_checkout(
    req: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a Stripe Checkout Session for subscription."""
    try:
        customer_id = get_or_create_customer(
            email=current_user.email,
            name=current_user.name,
            stripe_customer_id=current_user.stripe_customer_id,
        )
        current_user.stripe_customer_id = customer_id
        db.commit()
        session = create_checkout_session(
            customer_id=customer_id,
            plan_id=req.plan_id,
            success_url=os.getenv("NEXT_PUBLIC_APP_URL", "http://localhost:3000") + "/dashboard/settings?checkout=success",
            cancel_url=os.getenv("NEXT_PUBLIC_APP_URL", "http://localhost:3000") + "/dashboard/settings?checkout=cancel",
        )
        return {"checkout_url": session.url, "session_id": session.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stripe checkout failed: {str(e)}")

@app.get("/billing/subscription")
def get_billing_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return current subscription info from Stripe."""
    if not current_user.stripe_customer_id:
        return {"plan_id": "free", "status": "none"}
    try:
        info = get_subscription_info(current_user.stripe_customer_id)
        if not info:
            return {"plan_id": "free", "status": "none"}
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stripe subscription fetch failed: {str(e)}")

@app.post("/billing/portal")
def create_billing_portal(
    current_user: User = Depends(get_current_user),
):
    """Create a Stripe Customer Portal session."""
    if not current_user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No Stripe customer record")
    try:
        portal = create_portal_session(
            customer_id=current_user.stripe_customer_id,
            return_url=os.getenv("NEXT_PUBLIC_APP_URL", "http://localhost:3000") + "/dashboard/settings",
        )
        return {"portal_url": portal.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Portal session failed: {str(e)}")

@app.post("/billing/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhooks (subscriptions created, invoices paid, cancellations)."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    try:
        event = construct_event(payload, sig_header)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")

    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")
        plan_id = session.get("metadata", {}).get("plan_id", "starter")
        lookup_email = session.get("customer_email")
        # Update user
        user = db.query(User).filter(User.email == lookup_email).first()
        if user:
            user.stripe_customer_id = customer_id
            existing = db.query(Subscription).filter(Subscription.user_id == user.id).first()
            if existing:
                existing.stripe_subscription_id = subscription_id
                existing.plan_id = plan_id
                existing.status = "active"
                existing.amount = 149.00 if plan_id == "pro" else 49.00
            else:
                new_sub = Subscription(
                    user_id=user.id,
                    plan_id=plan_id,
                    stripe_subscription_id=subscription_id,
                    status="active",
                    amount=149.00 if plan_id == "pro" else 49.00,
                )
                db.add(new_sub)
            db.commit()

    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        customer_id = invoice.get("customer")
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
            if sub:
                sub.status = "past_due"
                db.commit()

    return {"status": "ok"}

# ─── Subscription gating helper ───

def get_user_plan(db: Session, user: User) -> str:
    """Return 'free', 'starter', 'pro', or 'enterprise' based on active Stripe sub."""
    if not user.stripe_customer_id:
        return "free"
    sub = db.query(Subscription).filter(
        Subscription.user_id == user.id,
        Subscription.status == "active"
    ).first()
    if not sub:
        return "free"
    return sub.plan_id

def enforce_plan_limit(db: Session, user: User, plan_id: str, generation_type: str = "content"):
    """Raise HTTPException if user has exceeded their plan limits."""
    limits = {
        "free": {"brands": 1, "pieces": 3, "images": 0},  # free has 1 brand and 3 pieces total
        "starter": {"brands": 5, "pieces": 100, "images": 0},
        "pro": {"brands": -1, "pieces": -1, "images": -1},
    }.get(plan_id, {"brands": 1, "pieces": 3, "images": 0})

    # Count brands owned
    if limits["brands"] >= 0:
        brand_count = db.query(Brand).filter(Brand.user_id == user.id).count()
        if brand_count > limits["brands"]:
            raise HTTPException(status_code=403, detail=f"Plan limit: {limits['brands']} brands max. Upgrade for more.")

    # Count content pieces this month
    if limits["pieces"] >= 0:
        from datetime import datetime, timedelta
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        piece_count = db.query(ContentPiece).filter(
            ContentPiece.user_id == user.id,
            ContentPiece.created_at >= start_of_month
        ).count()
        if piece_count > limits["pieces"]:
            raise HTTPException(status_code=403, detail=f"Plan limit: {limits['pieces']} pieces/mo. Upgrade for more.")

    # Image blocks
    if generation_type == "image" and limits["images"] == 0:
        raise HTTPException(status_code=403, detail="Image generation requires Starter or Pro plan.")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# ─── Analytics ───

@app.get("/analytics")
def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return content generation analytics for the current user."""
    from datetime import datetime, timedelta

    now = datetime.utcnow()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Count by type
    by_type = {}
    for row in db.query(ContentPiece.content_type, db.func.count(ContentPiece.id)).filter(
        ContentPiece.user_id == current_user.id
    ).group_by(ContentPiece.content_type).all():
        by_type[row[0]] = row[1]

    # Count by status
    by_status = {}
    for row in db.query(ContentPiece.status, db.func.count(ContentPiece.id)).filter(
        ContentPiece.user_id == current_user.id
    ).group_by(ContentPiece.status).all():
        by_status[row[0]] = row[1]

    # Last 7 days
    daily = []
    for i in range(7):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = db.query(db.func.count(ContentPiece.id)).filter(
            ContentPiece.user_id == current_user.id,
            ContentPiece.created_at >= day_start,
            ContentPiece.created_at < day_end
        ).scalar() or 0
        daily.insert(0, {"date": day_start.strftime("%Y-%m-%d"), "count": count})

    # Last 6 months
    monthly = []
    for i in range(6):
        month = now - timedelta(days=i * 30)
        month_start = month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        count = db.query(db.func.count(ContentPiece.id)).filter(
            ContentPiece.user_id == current_user.id,
            ContentPiece.created_at >= month_start,
            ContentPiece.created_at < month_end
        ).scalar() or 0
        monthly.insert(0, {
            "month": month_start.strftime("%b %Y"),
            "count": count
        })

    # Recent activity (last 10)
    recent = db.query(ContentPiece).filter(
        ContentPiece.user_id == current_user.id
    ).order_by(ContentPiece.created_at.desc()).limit(10).all()

    return {
        "summary": {
            "total": sum(by_type.values(), 0),
            "this_month": sum(1 for p in db.query(ContentPiece).filter(
                ContentPiece.user_id == current_user.id,
                ContentPiece.created_at >= start_of_month
            ).all()),
            "by_type": by_type,
            "by_status": by_status,
        },
        "daily": daily,
        "monthly": monthly,
        "recent": [
            {
                "id": r.id,
                "title": r.title,
                "type": r.content_type,
                "status": r.status,
                "created_at": r.created_at.isoformat(),
            }
            for r in recent
        ],
    }

