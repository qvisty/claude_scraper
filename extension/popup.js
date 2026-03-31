// Popup script — save/load API key from chrome.storage

const keyInput = document.getElementById("api-key");
const saveBtn = document.getElementById("save");
const statusEl = document.getElementById("status");

// Load existing key
chrome.storage.sync.get("apiKey", ({ apiKey }) => {
  if (apiKey) {
    keyInput.value = apiKey;
    statusEl.textContent = "Nøgle er gemt.";
    statusEl.className = "status ok";
  }
});

saveBtn.addEventListener("click", () => {
  const key = keyInput.value.trim();
  if (!key) {
    statusEl.textContent = "Indtast en API-nøgle.";
    statusEl.className = "status err";
    return;
  }

  chrome.storage.sync.set({ apiKey: key }, () => {
    statusEl.textContent = "Gemt!";
    statusEl.className = "status ok";
  });
});
