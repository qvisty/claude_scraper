"""Example: Scrape product data from a webpage using Claude as extraction engine.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python examples/scrape_products.py
"""

import asyncio
import json

from claude_scraper import scrape


async def main():
    # Define what data we want to extract (natural language!)
    extraction_prompt = """
    Extract all products from this page. For each product, get:
    - name: the product name
    - price: the price as a number (without currency symbol)
    - currency: the currency code (e.g. USD, EUR, DKK)
    - rating: the rating as a number (if available)
    - description: a short description (if available)
    """

    # Optional: provide a JSON schema for stricter output
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "price": {"type": "number"},
                "currency": {"type": "string"},
                "rating": {"type": ["number", "null"]},
                "description": {"type": ["string", "null"]},
            },
            "required": ["name", "price", "currency"],
        },
    }

    # Scrape a demo page (replace with your target URL)
    url = "https://books.toscrape.com/"

    result = await scrape(
        url,
        extraction_prompt,
        schema=schema,
        # proxy_url="http://user:pass@gate.decodo.com:7000",  # Uncomment for proxy
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
