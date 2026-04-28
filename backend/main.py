from fastapi import FastAPI, Depends, HTTPException, status, Header
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
def create_brand(brand: BrandCreate, db: Session = Depends(get_db)):
    db_brand = Brand(**brand.dict())
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand

@app.get("/brands")
def list_brands(db: Session = Depends(get_db)):
    return db.query(Brand).all()

@app.post("/content/generate", response_model=ContentResponse)
async def generate_content_endpoint(
    req: ContentGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
