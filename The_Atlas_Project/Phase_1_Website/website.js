"use strict";

(() => {
  const dialog = document.querySelector("#website-preview");
  const frame = document.querySelector("#preview-frame");
  const theme = document.querySelector("#preview-theme");
  const status = document.querySelector("#preview-status");
  const openers = document.querySelectorAll("[data-open-preview]");
  if (!dialog || !frame || !theme) return;
  let opener;
  const loadPreview = (reset = false) => {
    let url = new URL("index.html", location.href);
    if (!reset) {
      try {
        const current = new URL(frame.contentWindow.location.href);
        if (current.origin === location.origin && current.pathname.endsWith(".html")) url = current;
      } catch { /* Reset to the card if the previous preview cannot be read. */ }
    }
    url.searchParams.set("theme", theme.value);
    status.textContent = "Loading preview…";
    frame.setAttribute("aria-busy", "true");
    frame.src = url.href;
  };
  const closePreview = () => { if (dialog.open) dialog.close(); };
  openers.forEach(button => {
    button.hidden = false;
    button.addEventListener("click", () => {
      if (typeof dialog.showModal !== "function") {
        location.assign(new URL("index.html", location.href));
        return;
      }
      opener = button;
      const chosen = button.dataset.openPreview || new URL(location.href).searchParams.get("theme");
      theme.value = chosen === "dark" || chosen === "light" ? chosen : (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      dialog.showModal();
      document.body.classList.add("website-preview-open");
      loadPreview(true);
    });
  });
  document.querySelector("#close-preview").addEventListener("click", closePreview);
  document.querySelector("#reset-preview").addEventListener("click", () => loadPreview(true));
  theme.addEventListener("change", () => loadPreview());
  frame.addEventListener("load", () => {
    if (!dialog.open) return;
    frame.removeAttribute("aria-busy");
    status.textContent = "Preview ready";
    // Keyboard events inside a frame do not reach the surrounding dialog.
    try {
      frame.contentDocument.addEventListener("keydown", event => {
        if (event.key === "Escape") {
          event.preventDefault();
          event.stopImmediatePropagation();
          closePreview();
        }
      }, {capture: true});
    } catch { /* The outer Close button remains available. */ }
  });
  dialog.addEventListener("close", () => {
    document.body.classList.remove("website-preview-open");
    frame.src = "about:blank";
    frame.removeAttribute("aria-busy");
    status.textContent = "";
    opener?.focus({preventScroll: true});
  });
  window.addEventListener("pageshow", event => {
    if (event.persisted) closePreview();
  });
})();
