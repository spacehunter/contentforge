import os
import httpx
from fastapi import HTTPException
from typing import Optional, List
from models import Brand

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen3.5-35b-a3b")

DEFAULT_SYSTEM_PROMPT = """You are an expert marketing copywriter. Write high-quality, engaging content based on the user's request. Match the requested tone and target audience. Keep responses concise and actionable."""

CONTENT_TEMPLATES = {
    "blog": "Write a SEO-optimized blog post titled '{title}'. Tone: {tone}. Target: {audience}. Topic: {prompt}",
    "social": "Write 3 social media posts for a brand. Tone: {tone}. Target: {audience}. Topic: {prompt}",
    "email": "Write a marketing email. Subject line: '{title}'. Tone: {tone}. Target: {audience}. Topic: {prompt}",
    "pinterest": "Write a Pinterest pin description and title. Product/topic: {prompt}. Tone: {tone}. Target: {audience}. Brand: {title}.",
}

async def generate_content(
    title: str,
    content_type: str,
    prompt: str,
    tone: str = "professional",
    brand: Optional[Brand] = None,
    user_context: str = "",
) -> str:
    template = CONTENT_TEMPLATES.get(content_type, CONTENT_TEMPLATES["blog"])
    audience = brand.target_audience if brand else "general audience"
    brand_voice = brand.voice if brand else ""

    user_prompt = template.format(
        title=title,
        tone=tone,
        audience=audience,
        prompt=prompt,
    )

    system = DEFAULT_SYSTEM_PROMPT
    if brand_voice:
        system += f"\n\nBrand Voice Instructions:\n{brand_voice}"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_prompt},
    ]

    if user_context:
        messages.append({"role": "user", "content": f"Additional context: {user_context}"})

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            res = await client.post(
                f"{LLM_BASE_URL}/chat/completions",
                json={
                    "model": LLM_MODEL,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "stream": False,
                },
            )
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"]

    except (httpx.ConnectError, httpx.HTTPStatusError):
        # Fallback if local LLM unavailable or returns error
        return fallback_generate(title, content_type, prompt, tone, brand)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

def fallback_generate(
    title: str, content_type: str, prompt: str, tone: str, brand: Optional[Brand]
) -> str:
    brand_name = brand.name if brand else "Your Brand"
    return f"""# {title}

*(This is a placeholder — local LLM at {LLM_BASE_URL} is offline. Start LM Studio to get real AI generation.)*

## Overview
This {content_type} covers: {prompt}.

## Key Points
- First key point about {prompt}
- Second important consideration for {brand_name}'s audience
- Actionable takeaway for readers

## Summary
Tone: {tone}. Target: {brand.target_audience if brand else 'general audience'}.
"""
