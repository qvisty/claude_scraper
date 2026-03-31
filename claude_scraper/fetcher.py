"""HTML fetcher with proxy support using httpx."""

import httpx

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


async def fetch_page(
    url: str,
    *,
    proxy_url: str | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
    follow_redirects: bool = True,
) -> str:
    """Fetch a webpage and return its HTML content.

    Args:
        url: The URL to fetch.
        proxy_url: Optional proxy URL (e.g. http://user:pass@gate.decodo.com:7000).
        headers: Optional custom headers. Defaults to a Chrome-like UA.
        timeout: Request timeout in seconds.
        follow_redirects: Whether to follow HTTP redirects.

    Returns:
        The HTML content of the page as a string.

    Raises:
        httpx.HTTPStatusError: If the response status code indicates an error.
    """
    merged_headers = {**DEFAULT_HEADERS, **(headers or {})}

    async with httpx.AsyncClient(
        proxy=proxy_url,
        headers=merged_headers,
        timeout=timeout,
        follow_redirects=follow_redirects,
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text
