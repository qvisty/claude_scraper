// Content script — injects floating button and extraction panel into every page

(function () {
  if (document.getElementById("claude-scraper-root")) return;

  // --- Create root container ---
  const root = document.createElement("div");
  root.id = "claude-scraper-root";

  // --- Floating button ---
  const btn = document.createElement("button");
  btn.id = "claude-scraper-btn";
  btn.textContent = "CS";
  btn.title = "Claude Scraper";

  // --- Panel ---
  const panel = document.createElement("div");
  panel.id = "claude-scraper-panel";
  panel.classList.add("claude-scraper-hidden");
  panel.innerHTML = `
    <div class="cs-header">
      <span class="cs-title">Claude Scraper</span>
      <button class="cs-close">&times;</button>
    </div>
    <div class="cs-body">
      <label class="cs-label" for="cs-prompt">Hvad vil du udtrække?</label>
      <textarea id="cs-prompt" class="cs-textarea" rows="4"
        placeholder="F.eks.: Find alle produkter med navn, pris og rating"></textarea>
      <div class="cs-options">
        <label class="cs-label-small">
          <input type="checkbox" id="cs-text-only"> Kun tekst (billigere)
        </label>
        <select id="cs-model" class="cs-select">
          <option value="claude-sonnet-4-20250514">Sonnet 4 (standard)</option>
          <option value="claude-haiku-4-5-20251001">Haiku 4.5 (billig)</option>
        </select>
      </div>
      <button id="cs-extract" class="cs-btn-extract">Udtræk data</button>
      <div id="cs-status" class="cs-status"></div>
      <pre id="cs-result" class="cs-result claude-scraper-hidden"></pre>
      <button id="cs-copy" class="cs-btn-copy claude-scraper-hidden">Kopier JSON</button>
    </div>
  `;

  root.appendChild(btn);
  root.appendChild(panel);
  document.body.appendChild(root);

  // --- Clean HTML (same logic as Python cleaner) ---
  function cleanHtml(doc, textOnly) {
    const clone = doc.cloneNode(true);
    const removeTags = [
      "script", "style", "noscript", "iframe", "svg",
      "meta", "link", "head", "footer", "nav", "header",
    ];
    for (const tag of removeTags) {
      clone.querySelectorAll(tag).forEach((el) => el.remove());
    }
    // Remove comments
    const walker = document.createTreeWalker(clone, NodeFilter.SHOW_COMMENT);
    const comments = [];
    while (walker.nextNode()) comments.push(walker.currentNode);
    comments.forEach((c) => c.remove());

    if (textOnly) {
      return clone.body ? clone.body.innerText : clone.innerText;
    }

    // Strip non-essential attributes
    const keepAttrs = new Set(["href", "src", "alt", "title", "class", "id"]);
    clone.querySelectorAll("*").forEach((el) => {
      const attrs = [...el.attributes];
      for (const attr of attrs) {
        if (!keepAttrs.has(attr.name)) {
          el.removeAttribute(attr.name);
        }
      }
    });

    return clone.body ? clone.body.innerHTML : clone.innerHTML;
  }

  // --- Toggle panel ---
  btn.addEventListener("click", () => {
    panel.classList.toggle("claude-scraper-hidden");
  });

  panel.querySelector(".cs-close").addEventListener("click", () => {
    panel.classList.add("claude-scraper-hidden");
  });

  // --- Extract ---
  panel.querySelector("#cs-extract").addEventListener("click", async () => {
    const prompt = panel.querySelector("#cs-prompt").value.trim();
    if (!prompt) {
      setStatus("Skriv en prompt først.", "error");
      return;
    }

    const textOnly = panel.querySelector("#cs-text-only").checked;
    const model = panel.querySelector("#cs-model").value;
    const resultEl = panel.querySelector("#cs-result");
    const copyBtn = panel.querySelector("#cs-copy");
    const extractBtn = panel.querySelector("#cs-extract");

    setStatus("Renser HTML...", "info");
    const html = cleanHtml(document, textOnly);

    // Truncate if very large (Claude context limit)
    const maxChars = 150_000;
    const truncated = html.length > maxChars ? html.slice(0, maxChars) : html;

    setStatus("Sender til Claude...", "info");
    extractBtn.disabled = true;

    const response = await chrome.runtime.sendMessage({
      type: "extract",
      html: truncated,
      prompt,
      model,
    });

    extractBtn.disabled = false;

    if (response.error) {
      setStatus(response.error, "error");
      resultEl.classList.add("claude-scraper-hidden");
      copyBtn.classList.add("claude-scraper-hidden");
      return;
    }

    const json = JSON.stringify(response.data, null, 2);
    resultEl.textContent = json;
    resultEl.classList.remove("claude-scraper-hidden");
    copyBtn.classList.remove("claude-scraper-hidden");
    setStatus("Færdig!", "success");
  });

  // --- Copy ---
  panel.querySelector("#cs-copy").addEventListener("click", () => {
    const text = panel.querySelector("#cs-result").textContent;
    navigator.clipboard.writeText(text).then(() => {
      setStatus("Kopieret!", "success");
    });
  });

  function setStatus(msg, type) {
    const el = panel.querySelector("#cs-status");
    el.textContent = msg;
    el.className = "cs-status cs-status-" + type;
  }
})();
