# Claude Scraper

Web scraper that uses Claude as the data extraction engine. Instead of writing CSS selectors or XPath queries, you describe what data you want in natural language and Claude extracts it from the HTML.

Based on the [Direct Integration Method](https://decodo.com/blog/claude-web-scraping#h2-direct_integration_method:_claude_as_the_data_extraction_engine) from Decodo.

## Architecture

```
URL → httpx (fetch HTML) → BeautifulSoup (clean) → Claude API (extract) → JSON
         ↑
    Decodo/Smartproxy
    proxy (optional)
```

**Pipeline:**
1. **Fetch** — `httpx` fetches the page with optional proxy rotation (Decodo/Smartproxy)
2. **Clean** — `BeautifulSoup` strips scripts, styles, navs, and unnecessary attributes to reduce token cost
3. **Extract** — Cleaned HTML is sent to Claude with a natural language prompt describing the desired data
4. **Return** — Claude returns structured JSON matching your schema

## Setup

```bash
# Install dependencies
pip install -e .

# Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

# Optional: configure proxy
export PROXY_URL=http://user:pass@gate.decodo.com:7000
```

Or copy `.env.example` to `.env` and fill in your keys.

## Quick start

```python
import asyncio
from claude_scraper import scrape

result = asyncio.run(scrape(
    "https://books.toscrape.com/",
    "Extract all book titles and prices",
))
print(result)
```

## API

### `scrape(url, extraction_prompt, **kwargs)`

Main entry point. Fetches, cleans, and extracts in one call.

| Parameter | Type | Description |
|---|---|---|
| `url` | `str` | URL to scrape |
| `extraction_prompt` | `str` | Natural language description of data to extract |
| `schema` | `dict \| None` | Optional JSON schema for output structure |
| `proxy_url` | `str \| None` | Proxy URL (e.g. Decodo) |
| `model` | `str` | Claude model to use (default: `claude-sonnet-4-20250514`) |
| `extract_text_only` | `bool` | Send only visible text, not HTML (cheaper) |
| `clean` | `bool` | Clean HTML before extraction (default: `True`) |

### `scrape_multiple(urls, extraction_prompt, **kwargs)`

Scrape multiple URLs concurrently. Returns a list of `{url, data, error}` dicts.

### Lower-level functions

- `fetch_page(url, proxy_url=..., headers=...)` — Fetch raw HTML
- `clean_html(html, extract_text_only=...)` — Clean HTML with BeautifulSoup
- `extract_data(html, prompt, schema=...)` — Send to Claude API

## Examples

```bash
python examples/scrape_products.py    # Scrape product listings
python examples/scrape_articles.py    # Scrape news articles
python examples/scrape_with_proxy.py  # Scrape via Decodo proxy
```

## Proxy support (Decodo/Smartproxy)

For production scraping, use a proxy to avoid blocks. [Decodo](https://decodo.com/) (formerly Smartproxy) provides rotating residential proxies:

```python
result = await scrape(
    "https://target-site.com",
    "Extract product data",
    proxy_url="http://user:pass@gate.decodo.com:7000",
)
```

## Cost optimization

- Use `clean=True` (default) to strip unnecessary HTML before sending to Claude
- Use `extract_text_only=True` for pages where HTML structure isn't needed
- Use `claude-haiku-4-5-20251001` for simpler extraction tasks (cheaper)
- Provide a `schema` to get more consistent, parseable output
