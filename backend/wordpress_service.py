import httpx

async def publish_post(
    wp_base_url: str,
    wp_username: str,
    wp_app_password: str,
    title: str,
    content: str,
    status: str = "publish",
    excerpt: str = "",
    tags: list = None,
    categories: list = None,
) -> dict:
    """Publish a blog post to WordPress via REST API v2 using Application Passwords."""
    url = f"{wp_base_url.rstrip('/')}/wp-json/wp/v2/posts"
    payload = {
        "title": title,
        "content": content,
        "status": status,  # 'publish', 'draft', 'private'
        "excerpt": excerpt,
        "format": "standard",
    }
    if tags:
        payload["tags"] = tags
    if categories:
        payload["categories"] = categories

    async with httpx.AsyncClient() as client:
        r = await client.post(
            url,
            json=payload,
            auth=(wp_username, wp_app_password),
        )
        r.raise_for_status()
        return r.json()

async def list_posts(
    wp_base_url: str,
    wp_username: str,
    wp_app_password: str,
    per_page: int = 10,
) -> list:
    """List recent WordPress posts."""
    url = f"{wp_base_url.rstrip('/')}/wp-json/wp/v2/posts?per_page={per_page}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, auth=(wp_username, wp_app_password))
        r.raise_for_status()
        return r.json()

async def test_connection(wp_base_url: str, wp_username: str, wp_app_password: str) -> dict:
    """Test WordPress credentials by fetching the current user."""
    url = f"{wp_base_url.rstrip('/')}/wp-json/wp/v2/users/me"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, auth=(wp_username, wp_app_password))
        r.raise_for_status()
        return r.json()
