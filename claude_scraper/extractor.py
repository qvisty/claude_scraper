"""Claude API integration for intelligent data extraction from HTML."""

import json

import anthropic

DEFAULT_MODEL = "claude-sonnet-4-20250514"


def _build_system_prompt() -> str:
    return (
        "You are a precise data extraction engine. "
        "You receive HTML content and a description of the data to extract. "
        "You MUST respond with valid JSON only — no markdown, no explanation, no extra text. "
        "If data is missing or not found, use null for that field. "
        "If multiple items are expected, return a JSON array. "
        "If a single item is expected, return a JSON object."
    )


def _build_user_prompt(html: str, extraction_prompt: str, schema: dict | None) -> str:
    parts = [
        f"Extract the following data from the HTML below:\n\n{extraction_prompt}",
    ]
    if schema:
        parts.append(f"\nReturn the data matching this JSON schema:\n{json.dumps(schema, indent=2)}")
    parts.append(f"\n\n--- HTML CONTENT ---\n{html}\n--- END HTML ---")
    return "\n".join(parts)


async def extract_data(
    html: str,
    extraction_prompt: str,
    *,
    schema: dict | None = None,
    api_key: str | None = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 4096,
) -> dict | list:
    """Send HTML to Claude and extract structured data.

    Args:
        html: Cleaned HTML or text content to extract data from.
        extraction_prompt: Natural language description of what to extract.
            Example: "Extract all product names, prices, and ratings."
        schema: Optional JSON schema describing the expected output structure.
        api_key: Anthropic API key. If None, uses ANTHROPIC_API_KEY env var.
        model: Claude model to use.
        max_tokens: Maximum tokens in Claude's response.

    Returns:
        Parsed JSON as a dict or list.

    Raises:
        json.JSONDecodeError: If Claude's response is not valid JSON.
        anthropic.APIError: If the API call fails.
    """
    client = anthropic.AsyncAnthropic(api_key=api_key)

    message = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=_build_system_prompt(),
        messages=[
            {
                "role": "user",
                "content": _build_user_prompt(html, extraction_prompt, schema),
            }
        ],
    )

    response_text = message.content[0].text.strip()

    # Handle potential markdown code blocks in response
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        # Remove first and last lines (```json and ```)
        response_text = "\n".join(lines[1:-1]).strip()

    return json.loads(response_text)
