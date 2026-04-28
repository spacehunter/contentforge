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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
