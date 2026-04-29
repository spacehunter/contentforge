#!/usr/bin/env python3
"""Seed script: create demo user, brand, and sample content pieces."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from database import SessionLocal, Base, engine
from models import User, Brand, ContentPiece, Subscription
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Demo user
    demo_email = "demo@contentforge.local"
    existing = db.query(User).filter(User.email == demo_email).first()
    if existing:
        print(f"Demo user {demo_email} already exists, skipping.")
        db.close()
        return

    demo_user = User(
        email=demo_email,
        hashed_password=pwd_context.hash("demo123"),
        name="Demo User",
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)
    print(f"Created user: {demo_email} / demo123")

    # Demo brand
    brand = Brand(
        name="Acme Corp",
        voice="Professional, witty, and concise",
        industry="Technology",
        target_audience="B2B marketers, SaaS founders",
        user_id=demo_user.id,
        created_at=datetime.utcnow(),
    )
    db.add(brand)
    db.commit()
    db.refresh(brand)
    print(f"Created brand: {brand.name}")

    # Sample content pieces
    samples = [
        {
            "title": "How AI Is Changing Content Marketing in 2026",
            "content_type": "blog",
            "prompt": "Write a blog post about AI in content marketing.",
            "generated_text": "Artificial intelligence has revolutionized content marketing by automating research, generating drafts, and personalizing messaging at scale. In 2026, brands that leverage AI for keyword research, headline optimization, and video scripting are seeing 40% faster production cycles...",
            "status": "published",
            "brand_id": brand.id,
        },
        {
            "title": "Spring Sale Social Post",
            "content_type": "social",
            "prompt": "Create an engaging social media post for a spring sale.",
            "generated_text": "Spring into savings! Our biggest sale of the season is here. Refresh your strategy with 30% off all ContentForge plans. Limited time only.",
            "status": "generated",
            "brand_id": brand.id,
        },
        {
            "title": "Weekly Newsletter Volume 42",
            "content_type": "email",
            "prompt": "Write a weekly newsletter for a SaaS audience.",
            "generated_text": "Welcome to this week's edition of ContentForge Weekly. This week we cover the latest in AI regulation, share a case study from our Pro user Acme Corp, and announce our new Pinterest publishing integration.",
            "status": "draft",
            "brand_id": None,
        },
        {
            "title": "Generated image - pinterest",
            "content_type": "image",
            "prompt": "A minimalist pinterest pin showing spring flowers and a 30% off badge.",
            "generated_text": "/images/demo_spring_pin.png",
            "status": "published",
            "brand_id": None,
            "image_url": "/images/demo_spring_pin.png",
        },
    ]

    for s in samples:
        piece = ContentPiece(
            title=s["title"],
            content_type=s["content_type"],
            prompt=s["prompt"],
            generated_text=s["generated_text"],
            status=s["status"],
            user_id=demo_user.id,
            brand_id=s.get("brand_id"),
            image_url=s.get("image_url"),
            created_at=datetime.utcnow() - timedelta(days=samples.index(s)),
        )
        db.add(piece)
    db.commit()
    print(f"Created {len(samples)} content pieces.")

    db.close()
    print("Seeding complete.")

if __name__ == "__main__":
    seed()
