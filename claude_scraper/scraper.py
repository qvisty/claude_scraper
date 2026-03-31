"""Main scraper orchestrator — ties fetcher, cleaner, and extractor together."""

from claude_scraper.cleaner import clean_html
from claude_scraper.extractor import extract_data
from claude_scraper.fetcher import fetch_page


async def scrape(
    url: str,
    extraction_prompt: str,
    *,
    schema: dict | None = None,
    proxy_url: str | None = None,
    headers: dict[str, str] | None = None,
    api_key: str | None = None,
    model: str = "claude-sonnet-4-20250514",
    extract_text_only: bool = False,
    clean: bool = True,
) -> dict | list:
    """Scrape a URL and extract structured data using Claude.

    This is the main entry point that orchestrates the full pipeline:
    1. Fetch the page HTML (with optional proxy)
    2. Clean the HTML to reduce tokens
    3. Send to Claude for intelligent data extraction

    Args:
        url: The URL to scrape.
        extraction_prompt: Natural language description of what data to extract.
        schema: Optional JSON schema for the expected output.
        proxy_url: Optional proxy URL for fetching.
        headers: Optional custom HTTP headers.
        api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var).
        model: Claude model to use.
        extract_text_only: If True, send only visible text (no HTML) to Claude.
        clean: If True, clean the HTML before sending to Claude.

    Returns:
        Extracted data as a dict or list.
    """
    html = await fetch_page(url, proxy_url=proxy_url, headers=headers)

    if clean:
        content = clean_html(html, extract_text_only=extract_text_only)
    else:
        content = html

    return await extract_data(
        content,
        extraction_prompt,
        schema=schema,
        api_key=api_key,
        model=model,
    )


async def scrape_multiple(
    urls: list[str],
    extraction_prompt: str,
    *,
    schema: dict | None = None,
    proxy_url: str | None = None,
    api_key: str | None = None,
    model: str = "claude-sonnet-4-20250514",
    extract_text_only: bool = False,
) -> list[dict]:
    """Scrape multiple URLs and return a list of results.

    Each result dict contains 'url', 'data' (extracted data), and 'error' (if any).
    """
    import asyncio

    async def _scrape_one(url: str) -> dict:
        try:
            data = await scrape(
                url,
                extraction_prompt,
                schema=schema,
                proxy_url=proxy_url,
                api_key=api_key,
                model=model,
                extract_text_only=extract_text_only,
            )
            return {"url": url, "data": data, "error": None}
        except Exception as e:
            return {"url": url, "data": None, "error": str(e)}

    tasks = [_scrape_one(url) for url in urls]
    return await asyncio.gather(*tasks)
