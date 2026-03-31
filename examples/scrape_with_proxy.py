"""Example: Scrape with Decodo/Smartproxy proxy rotation.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    export PROXY_URL=http://username:password@gate.decodo.com:7000
    python examples/scrape_with_proxy.py
"""

import asyncio
import json
import os

from dotenv import load_dotenv

from claude_scraper import scrape

load_dotenv()


async def main():
    proxy_url = os.getenv("PROXY_URL")
    if not proxy_url:
        print("Set PROXY_URL in .env or environment to use proxy rotation.")
        print("Example: http://username:password@gate.decodo.com:7000")
        return

    extraction_prompt = """
    Extract the main content from this page:
    - title: the page title
    - main_text: the primary article/content text
    - author: author name if available
    - date: publication date if available
    """

    url = "https://example.com"

    result = await scrape(
        url,
        extraction_prompt,
        proxy_url=proxy_url,
        extract_text_only=True,  # Text only = fewer tokens = lower cost
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
