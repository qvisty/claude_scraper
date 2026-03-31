"""Example: Scrape news articles and extract structured data.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python examples/scrape_articles.py
"""

import asyncio
import json

from claude_scraper import scrape


async def main():
    extraction_prompt = """
    Extract all article listings from this page. For each article, get:
    - title: the article headline
    - author: the author name (if available)
    - date: the publication date (if available, in ISO format)
    - summary: a brief summary or excerpt
    - url: the link to the full article
    """

    url = "https://news.ycombinator.com/"

    result = await scrape(
        url,
        extraction_prompt,
        extract_text_only=False,  # Keep HTML so Claude can see links
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
