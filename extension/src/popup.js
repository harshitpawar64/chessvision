import { predictBoard } from "./board.js";

const selectBtn = document.getElementById("select-btn");
const statusText = document.getElementById("status-text");
const lichessFrame = document.getElementById("lichess-frame");

function showBoard(lichessUrl) {
  document.body.classList.add("has-board");
  lichessFrame.src = lichessUrl;
}

function showError(message) {
  document.body.classList.remove("has-board");
  statusText.textContent = message;
  statusText.classList.add("error");
}

selectBtn.addEventListener("click", async () => {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ["src/content.js"],
    });
    window.close();
  } catch {
    showError("Cannot select board on this page.");
  }
});

const { pendingCapture, lastLichessUrl } = await chrome.storage.session.get([
  "pendingCapture",
  "lastLichessUrl",
]);

if (pendingCapture) {
  await chrome.storage.session.remove("pendingCapture");
  statusText.textContent = "Recognizing board position...";

  try {
    const lichessUrl = await predictBoard(pendingCapture.dataUrl, pendingCapture.crop);
    await chrome.storage.session.set({ lastLichessUrl: lichessUrl });
    showBoard(lichessUrl);
  } catch (err) {
    showError(`Prediction failed: ${err.message}`);
  }
} else if (lastLichessUrl) {
  showBoard(lastLichessUrl);
}
