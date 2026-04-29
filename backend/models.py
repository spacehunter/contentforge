from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String)
    is_active = Column(Boolean, default=True)
    stripe_customer_id = Column(String, nullable=True)
    pinterest_access_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Brand(Base):
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    voice = Column(Text)
    industry = Column(String)
    target_audience = Column(String)
    user_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class ContentPiece(Base):
    __tablename__ = "content_pieces"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content_type = Column(String)
    prompt = Column(Text)
    generated_text = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    status = Column(String, default="pending")
    user_id = Column(Integer)
    brand_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    plan_id = Column(String)
    stripe_subscription_id = Column(String)
    status = Column(String, default="active")
    amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

class WaitlistEntry(Base):
    __tablename__ = "waitlist"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    source = Column(String, nullable=True, default="landing")
    converted_to_user = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
