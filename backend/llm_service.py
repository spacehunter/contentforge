import os
import asyncio
import httpx
from fastapi import HTTPException
from typing import Optional, List
from models import Brand

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen3.5-35b-a3b")
COMFYUI_BASE_URL = os.getenv("COMFYUI_BASE_URL", "http://localhost:8188")

IMAGE_PROMPT_TEMPLATES = {
    "pinterest": "A visually stunning Pinterest pin for a brand. Vertical 2:3 composition. Clean typography overlay. Inspired by modern Canva designs. Topic: {prompt}. Brand vibe: {brand_voice}. High detail, marketing-ready, bold colors.",
    "hero": "A wide landscape hero banner image (16:9) for a website. Modern, clean design. Slight bokeh background. Professional marketing photography style. Topic: {prompt}. Brand vibe: {brand_voice}.",
    "before_after": "A before-and-after split frame image for a home services brand. Clean division down the middle. Professional lighting. Trustworthy, clean, inviting. Topic: {prompt}. Brand vibe: {brand_voice}.",
}

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

async def generate_image(
    prompt: str,
    template_type: str = "pinterest",
    brand: Optional[Brand] = None,
) -> str:
    """Generate an image via ComfyUI. Returns the URL/path to the saved image."""
    template = IMAGE_PROMPT_TEMPLATES.get(template_type, IMAGE_PROMPT_TEMPLATES["pinterest"])
    brand_voice = brand.voice if brand else "modern, professional brand"

    image_prompt = template.format(prompt=prompt, brand_voice=brand_voice)

    comfy_prompt = {
        "prompt": {
            "1": {"inputs": {"text": image_prompt, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
            "2": {"inputs": {"seed": 12345, "steps": 20, "cfg": 7.0, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0, "model": ["4", 0], "positive": ["1", 0], "negative": ["1", 0], "latent_image": ["3", 0]}, "class_type": "KSampler"},
            "3": {"inputs": {"width": 768, "height": 1344, "batch_size": 1}, "class_type": "EmptyLatentImage"},
            "4": {"inputs": {"ckpt_name": "flux1-dev.safetensors", "vae_name": "flux1-dev.safetensors"}, "class_type": "CheckpointLoaderSimple"},
            "5": {"inputs": {"samples": ["2", 0], "vae": ["4", 2]}, "class_type": "VAEDecode"},
            "6": {"inputs": {"filename_prefix": "contentforge", "images": ["5", 0]}, "class_type": "SaveImage"}
        }
    }

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            # Queue the prompt
            res = await client.post(f"{COMFYUI_BASE_URL}/prompt", json=comfy_prompt)
            res.raise_for_status()
            data = res.json()
            prompt_id = data.get("prompt_id")

            if not prompt_id:
                raise HTTPException(status_code=500, detail="ComfyUI did not return a prompt_id")

            # Poll for completion
            for _ in range(120):  # ~2 minutes max
                history_res = await client.get(f"{COMFYUI_BASE_URL}/history/{prompt_id}")
                history_res.raise_for_status()
                history = history_res.json()

                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    for node_id, node_output in outputs.items():
                        images = node_output.get("images", [])
                        if images:
                            filename = images[0].get("filename")
                            if filename:
                                # Copy from ComfyUI output to our static dir
                                output_dir = "static/images"
                                os.makedirs(output_dir, exist_ok=True)
                                src = f"/home/nova/comfyui/output/{filename}"
                                dst = os.path.join(os.path.dirname(__file__), output_dir, filename)
                                if os.path.exists(src):
                                    import shutil
                                    shutil.copy2(src, dst)
                                return f"/images/{filename}"
                    break  # Completed but no images
                await asyncio.sleep(2)

            return fallback_image(prompt, template_type, brand)

    except (httpx.ConnectError, httpx.HTTPStatusError):
        return fallback_image(prompt, template_type, brand)
    except Exception as e:
        return fallback_image(prompt, template_type, brand)


def fallback_image(prompt: str, template_type: str, brand: Optional[Brand]) -> str:
    """Return a placeholder image path if ComfyUI is unavailable."""
    import uuid
    output_dir = "static/images"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"placeholder-{uuid.uuid4().hex[:8]}.png"
    dst = os.path.join(os.path.dirname(__file__), output_dir, filename)
    # Create a tiny 1x1 transparent PNG as placeholder
    with open(dst, "wb") as f:
        f.write(bytes.fromhex("89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000a49444154789c63000100000500010d0a2db40000000049454e44ae426082"))
    return f"/images/{filename}"
