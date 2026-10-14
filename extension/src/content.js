(() => {
  const EXISTING_ID = "chessvision-snip-overlay";
  document.getElementById(EXISTING_ID)?.remove();

  const overlay = document.createElement("div");
  overlay.id = EXISTING_ID;
  Object.assign(overlay.style, {
    position: "fixed",
    inset: "0",
    zIndex: "2147483647",
    cursor: "crosshair",
    backgroundColor: "rgba(0, 0, 0, 0.45)",
    userSelect: "none",
  });

  const hint = document.createElement("div");
  hint.textContent = "Drag to select chessboard • Esc to cancel";
  Object.assign(hint.style, {
    position: "fixed",
    top: "16px",
    left: "50%",
    transform: "translateX(-50%)",
    padding: "8px 16px",
    borderRadius: "999px",
    backgroundColor: "rgba(20, 20, 24, 0.9)",
    color: "#ffffff",
    fontFamily: "system-ui, -apple-system, sans-serif",
    fontSize: "13px",
    fontWeight: "500",
    pointerEvents: "none",
    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.35)",
  });

  const selectionBox = document.createElement("div");
  Object.assign(selectionBox.style, {
    position: "fixed",
    display: "none",
    border: "2px solid #35c555",
    borderRadius: "2px",
    boxShadow: "0 0 0 9999px rgba(0, 0, 0, 0.45)",
    backgroundImage: [
      "linear-gradient(to right, rgba(53, 197, 85, 0.45) 1px, transparent 1px)",
      "linear-gradient(to bottom, rgba(53, 197, 85, 0.45) 1px, transparent 1px)",
    ].join(", "),
    backgroundSize: "12.5% 12.5%",
    boxSizing: "border-box",
    pointerEvents: "none",
  });

  overlay.append(hint, selectionBox);
  document.documentElement.appendChild(overlay);

  let startX = 0;
  let startY = 0;
  let isDragging = false;

  const getRect = (e) => ({
    x: Math.min(startX, e.clientX),
    y: Math.min(startY, e.clientY),
    width: Math.abs(e.clientX - startX),
    height: Math.abs(e.clientY - startY),
  });

  const cleanup = () => {
    window.removeEventListener("keydown", onKeyDown, true);
    overlay.remove();
  };

  const onKeyDown = (e) => {
    if (e.key === "Escape") {
      e.preventDefault();
      e.stopPropagation();
      cleanup();
    }
  };

  overlay.addEventListener("mousedown", (e) => {
    if (e.button !== 0) return;
    isDragging = true;
    startX = e.clientX;
    startY = e.clientY;
    overlay.style.backgroundColor = "transparent";
    Object.assign(selectionBox.style, {
      display: "block",
      left: `${startX}px`,
      top: `${startY}px`,
      width: "0px",
      height: "0px",
    });
  });

  overlay.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    const { x, y, width, height } = getRect(e);
    Object.assign(selectionBox.style, {
      left: `${x}px`,
      top: `${y}px`,
      width: `${width}px`,
      height: `${height}px`,
    });
  });

  overlay.addEventListener("mouseup", (e) => {
    if (!isDragging) return;
    isDragging = false;

    const { x, y, width, height } = getRect(e);
    cleanup();

    if (width < 32 || height < 32) return;

    const dpr = window.devicePixelRatio || 1;
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        chrome.runtime.sendMessage({
          type: "CHESSVISION_SNIP_COMPLETE",
          crop: {
            x: Math.max(0, Math.round(x * dpr)),
            y: Math.max(0, Math.round(y * dpr)),
            width: Math.round(width * dpr),
            height: Math.round(height * dpr),
          },
        });
      });
    });
  });

  window.addEventListener("keydown", onKeyDown, true);
})();
