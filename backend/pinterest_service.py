import os
import httpx
from urllib.parse import urlencode

PINTEREST_APP_ID = os.getenv("PINTEREST_APP_ID", "")
PINTEREST_APP_SECRET = os.getenv("PINTEREST_APP_SECRET", "")
PINTEREST_REDIRECT_URI = os.getenv("PINTEREST_REDIRECT_URI", "http://localhost:3000/dashboard/settings")

API_BASE = "https://api.pinterest.com/v5"
OAUTH_BASE = "https://www.pinterest.com/oauth"

def get_oauth_url(state: str) -> str:
    """Build the Pinterest OAuth URL."""
    params = {
        "client_id": PINTEREST_APP_ID,
        "redirect_uri": PINTEREST_REDIRECT_URI,
        "response_type": "code",
        "scope": "pins:read,pins:write,boards:read,boards:write",
        "state": state,
    }
    return f"{OAUTH_BASE}?{urlencode(params)}"

async def exchange_code(code: str) -> dict:
    """Exchange authorization code for access token."""
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": PINTEREST_REDIRECT_URI,
    }
    auth = (PINTEREST_APP_ID, PINTEREST_APP_SECRET)
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{API_BASE}/oauth/token",
            data=data,
            auth=auth,
        )
        r.raise_for_status()
        return r.json()

async def refresh_access_token(refresh_token: str) -> dict:
    """Refresh Pinterest access token."""
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    auth = (PINTEREST_APP_ID, PINTEREST_APP_SECRET)
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{API_BASE}/oauth/token",
            data=data,
            auth=auth,
        )
        r.raise_for_status()
        return r.json()

async def list_boards(access_token: str) -> list:
    """List user's Pinterest boards."""
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{API_BASE}/boards",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        r.raise_for_status()
        return r.json().get("items", [])

async def create_pin(
    access_token: str,
    board_id: str,
    title: str,
    description: str,
    link: str,
    image_url: str,
) -> dict:
    """Create a standard Pin on Pinterest using an external image URL."""
    payload = {
        "title": title,
        "description": description,
        "link": link,
        "board_id": board_id,
        "media_source": {
            "source_type": "image_url",
            "url": image_url,
        },
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{API_BASE}/pins",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        r.raise_for_status()
        return r.json()

async def get_user(access_token: str) -> dict:
    """Get the authenticated Pinterest user profile."""
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{API_BASE}/user_account",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        r.raise_for_status()
        return r.json()

async def delete_pin(access_token: str, pin_id: str) -> bool:
    """Delete a pin by ID."""
    async with httpx.AsyncClient() as client:
        r = await client.delete(
            f"{API_BASE}/pins/{pin_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return r.status_code in (200, 204)
