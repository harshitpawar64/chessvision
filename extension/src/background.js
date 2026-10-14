chrome.runtime.onMessage.addListener((message, sender) => {
  if (message?.type !== "CHESSVISION_SNIP_COMPLETE" || !sender.tab?.windowId) {
    return;
  }

  (async () => {
    try {
      const dataUrl = await chrome.tabs.captureVisibleTab(sender.tab.windowId, {
        format: "png",
      });

      await chrome.storage.session.set({
        pendingCapture: {
          dataUrl,
          crop: message.crop,
        },
      });

      await chrome.action.openPopup();
    } catch (err) {
      console.error("Failed to capture selected board:", err);
    }
  })();
});
