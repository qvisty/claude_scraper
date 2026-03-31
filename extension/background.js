// Background service worker — handles Claude API calls
// Keeps the API key out of the content script context

const DEFAULT_MODEL = "claude-sonnet-4-20250514";

const SYSTEM_PROMPT = `You are a precise data extraction engine.
You receive HTML content and a description of the data to extract.
You MUST respond with valid JSON only — no markdown, no explanation, no extra text.
If data is missing or not found, use null for that field.
If multiple items are expected, return a JSON array.
If a single item is expected, return a JSON object.`;

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === "extract") {
    handleExtraction(message).then(sendResponse);
    return true; // keep channel open for async response
  }
});

async function handleExtraction({ html, prompt, model }) {
  try {
    const { apiKey } = await chrome.storage.sync.get("apiKey");
    if (!apiKey) {
      return { error: "API-nøgle mangler. Klik på extension-ikonet for at sætte den." };
    }

    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
        "anthropic-dangerous-direct-browser-access": "true",
      },
      body: JSON.stringify({
        model: model || DEFAULT_MODEL,
        max_tokens: 4096,
        system: SYSTEM_PROMPT,
        messages: [
          {
            role: "user",
            content: `Extract the following data from the HTML below:\n\n${prompt}\n\n--- HTML CONTENT ---\n${html}\n--- END HTML ---`,
          },
        ],
      }),
    });

    if (!response.ok) {
      const err = await response.text();
      return { error: `API error ${response.status}: ${err}` };
    }

    const data = await response.json();
    let text = data.content[0].text.trim();

    // Strip markdown code fences if present
    if (text.startsWith("```")) {
      const lines = text.split("\n");
      text = lines.slice(1, -1).join("\n").trim();
    }

    return { data: JSON.parse(text) };
  } catch (e) {
    return { error: e.message };
  }
}
