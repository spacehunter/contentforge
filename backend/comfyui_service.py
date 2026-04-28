import os
import httpx
import json
import time
import uuid
import shutil
from typing import Optional

COMFYUI_URL = os.getenv("COMFYUI_URL", "http://localhost:8188")
STATIC_IMAGES_DIR = os.environ.get("STATIC_IMAGES_DIR", os.path.join(os.path.dirname(__file__), "static", "images"))

os.makedirs(STATIC_IMAGES_DIR, exist_ok=True)

IMAGE_TEMPLATES = {
    "pinterest": {
        "dimensions": (768, 1344),
        "prompt_suffix": "vertical composition, Pinterest pin style, text overlay friendly, clean aesthetic, high contrast, product photography",
    },
    "hero": {
        "dimensions": (1344, 768),
        "prompt_suffix": "wide banner composition, website hero section, dramatic lighting, cinematic, high quality, landscape orientation, professional",
    },
    "before_after": {
        "dimensions": (1024, 1024),
        "prompt_suffix": "split frame showing before and after transformation, clean divider, matching lighting and angle on both sides, real photography style",
    },
}


def build_comfyui_workflow(width: int, height: int, positive: str, negative: str = "", seed: int = 42):
    """Build a standard Flux fp8 KSampler workflow for ComfyUI API."""
    return {
        "1": {
            "inputs": {"ckpt_name": "flux1-dev-fp8.safetensors"},
            "class_type": "CheckpointLoaderSimple",
        },
        "2": {
            "inputs": {"width": width, "height": height, "batch_size": 1},
            "class_type": "EmptyLatentImage",
        },
        "3": {
            "inputs": {"clip": ["1", 1], "text": positive},
            "class_type": "CLIPTextEncode",
        },
        "4": {
            "inputs": {"clip": ["1", 1], "text": negative},
            "class_type": "CLIPTextEncode",
        },
        "5": {
            "inputs": {
                "seed": seed,
                "steps": 20,
                "cfg": 3.5,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["3", 0],
                "negative": ["4", 0],
                "latent_image": ["2", 0],
            },
            "class_type": "KSampler",
        },
        "6": {
            "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
            "class_type": "VAEDecode",
        },
        "7": {
            "inputs": {
                "filename_prefix": "cf_gen",
                "images": ["6", 0],
            },
            "class_type": "SaveImage",
        },
    }


async def generate_image(
    prompt: str,
    template_type: str = "pinterest",
    brand_voice: Optional[str] = None,
) -> str:
    """
    Queue a ComfyUI image generation job, wait for completion,
    copy the output image to backend/static/images/, and return the public URL path.
    """
    template = IMAGE_TEMPLATES.get(template_type, IMAGE_TEMPLATES["pinterest"])
    width, height = template["dimensions"]
    full_prompt = f"{prompt}. {template['prompt_suffix']}"

    if brand_voice:
        full_prompt = f"{brand_voice} style. {full_prompt}"

    workflow = build_comfyui_workflow(width=width, height=height, positive=full_prompt)

    prompt_id = str(uuid.uuid4())

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(f"{COMFYUI_URL}/prompt", json={"prompt": workflow})
            res.raise_for_status()
            data = res.json()
            prompt_id = data.get("prompt_id", prompt_id)
    except Exception as e:
        raise RuntimeError(f"Failed to queue ComfyUI prompt: {e}")

    # Poll history endpoint until image is ready
    max_wait = 120  # seconds
    interval = 2
    image_filename = None
    image_subfolder = ""

    for _ in range(max_wait // interval):
        await httpx_sleep(interval)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                hist_res = await client.get(f"{COMFYUI_URL}/history/{prompt_id}")
                hist_res.raise_for_status()
                hist = hist_res.json()
                entry = hist.get(prompt_id, {})
                if entry:
                    outputs = entry.get("outputs", {})
                    if outputs:
                        for node_id, node_output in outputs.items():
                            imgs = node_output.get("images", [])
                            if imgs:
                                image_filename = imgs[0].get("filename")
                                image_subfolder = imgs[0].get("subfolder", "")
                                break
                    break
        except Exception:
            pass

    if not image_filename:
        raise RuntimeError("ComfyUI did not return an image in time")

    # Download image from ComfyUI output folder
    comfyui_output_dir = os.environ.get("COMFYUI_OUTPUT_DIR", "/home/nova/ComfyUI/output")
    src_path = os.path.join(comfyui_output_dir, image_subfolder, image_filename)
    if not os.path.exists(src_path):
        # fallback: try to fetch via ComfyUI view endpoint
        view_url = f"{COMFYUI_URL}/view?filename={image_filename}&subfolder={image_subfolder}&type=output"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                img_res = await client.get(view_url)
                img_res.raise_for_status()
                unique_name = f"cf_{prompt_id.replace('-','')[:8]}_{image_filename}"
                dest_path = os.path.join(STATIC_IMAGES_DIR, unique_name)
                with open(dest_path, "wb") as f:
                    f.write(img_res.content)
                return f"/images/{unique_name}"
        except Exception as e:
            raise RuntimeError(f"Could not retrieve generated image: {e}")

    unique_name = f"cf_{prompt_id.replace('-','')[:8]}_{image_filename}"
    dest_path = os.path.join(STATIC_IMAGES_DIR, unique_name)
    shutil.copy(src_path, dest_path)
    return f"/images/{unique_name}"


async def comfyui_generate_blocking(
    prompt: str,
    template_type: str = "pinterest",
    brand_voice: Optional[str] = None,
    timeout: int = 120,
) -> str:
    return await generate_image(prompt, template_type, brand_voice)


# Reusable sleep helper using anyio/httpx (httpx does not provide sleep natively)
async def httpx_sleep(seconds: float):
    import asyncio
    await asyncio.sleep(seconds)
