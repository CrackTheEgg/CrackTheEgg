"use strict";

// Animate two real card faces, then follow the link normally so URLs and history work.
(() => {
  const source = document.querySelector(".business-card");
  const links = document.querySelectorAll("a[data-card-flip]");
  if (!source || !links.length) return;
  const backLink = document.querySelector(".contact-card-back");
  if (backLink) document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !event.defaultPrevented) backLink.click();
  });
  let busy = false;
  let scene;
  const originalVisibility = source.style.visibility;
  const originalInert = source.inert;
  const restore = () => {
    scene?.remove();
    scene = null;
    source.style.visibility = originalVisibility;
    source.inert = originalInert;
    busy = false;
  };
  window.addEventListener("pageshow", restore);

  // Measure the destination with its own responsive styles before moving the card.
  const measurePage = async (page, destination) => {
    page.querySelectorAll("script").forEach(script => script.remove());
    const base = page.createElement("base");
    base.href = destination;
    page.head.prepend(base);
    const theme = page.querySelector("#dark-theme");
    if (theme) theme.media = document.querySelector("#dark-theme").media;
    const frame = document.createElement("iframe");
    frame.setAttribute("sandbox", "allow-same-origin");
    frame.setAttribute("aria-hidden", "true");
    frame.inert = true;
    Object.assign(frame.style, {
      position: "fixed", left: "-100000px", top: "0", border: "0",
      width: innerWidth + "px", height: innerHeight + "px", visibility: "hidden"
    });
    let timeout;
    try {
      await new Promise((resolve, reject) => {
        frame.onload = resolve;
        timeout = setTimeout(() => reject(new Error("Page measurement timed out")), 2500);
        frame.srcdoc = page.documentElement.outerHTML;
        document.body.append(frame);
      });
      const rect = frame.contentDocument.querySelector(".page").getBoundingClientRect();
      return {left: rect.left, top: rect.top, width: rect.width, height: rect.height};
    } finally {
      clearTimeout(timeout);
      frame.remove();
    }
  };

  links.forEach((link) => link.addEventListener("click", async (event) => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || !source.animate) return;
    event.preventDefault();
    if (busy) return;
    busy = true;
    const destination = link.href;
    try {
      const response = await fetch(destination);
      if (!response.ok) throw new Error("Card unavailable");
      const nextPage = new DOMParser().parseFromString(await response.text(), "text/html");
      let nextCard = nextPage.querySelector(".business-card");
      const expandsToPage = Boolean(link.dataset.pageFlip && nextPage.querySelector(".page"));
      const targetBounds = expandsToPage ? await measurePage(nextPage, destination) : null;
      if (expandsToPage) {
        nextCard = nextPage.querySelector(".page");
        nextCard.classList.add("business-card");
      }
      if (!nextCard) throw new Error("Card unavailable");
      // Honour a motion preference changed while the page was loading.
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        window.location.assign(destination);
        return;
      }
      const bounds = source.getBoundingClientRect();
      const width = source.offsetWidth;
      const height = source.offsetHeight;
      scene = document.createElement("div");
      scene.className = "card-flip-scene";
      scene.setAttribute("aria-hidden", "true");
      scene.inert = true;
      Object.assign(scene.style, {
        width: width + "px", height: height + "px",
        left: bounds.left + (bounds.width - width) / 2 + "px",
        top: bounds.top + (bounds.height - height) / 2 + "px",
        transform: getComputedStyle(source).transform
      });
      const rotor = document.createElement("div");
      rotor.className = "card-flip-rotor";
      // Keep the container-sized card inside a separate 3D face.
      const faces = [source, nextCard].map((card) => {
        const face = document.createElement("div");
        face.className = "card-flip-face";
        const copy = card.cloneNode(true);
        for (const element of [copy, ...copy.querySelectorAll("[id], [aria-labelledby], [aria-controls]")]) {
          element.removeAttribute("id");
          element.removeAttribute("aria-labelledby");
          element.removeAttribute("aria-controls");
        }
        face.append(copy);
        return face;
      });
      const [front, back] = faces;
      back.classList.add("card-flip-reverse");
      if (expandsToPage) {
        back.classList.add(...nextPage.body.classList, "page-flip-face");
      }
      rotor.append(front, back);
      scene.append(rotor);
      document.body.append(scene);
      // Root scrollbar gutters offset fixed positioning in Safari. Convert viewport
      // measurements into the scene's positioning coordinates on both faces.
      const positioned = scene.getBoundingClientRect();
      const originX = positioned.left - parseFloat(scene.style.left);
      const originY = positioned.top - parseFloat(scene.style.top);
      scene.style.left = parseFloat(scene.style.left) - originX + "px";
      scene.style.top = parseFloat(scene.style.top) - originY + "px";
      source.style.visibility = "hidden";
      source.inert = true;
      const timing = { duration: expandsToPage ? 900 : 760, easing: "cubic-bezier(.45, 0, .2, 1)", fill: "forwards" };
      const animations = [
        rotor.animate([
          { transform: "rotateY(0deg)" },
          { transform: `rotateY(${Number(link.dataset.cardFlip) === 180 ? 180 : -180}deg)` }
        ], timing),
        // Explicitly swap visibility edge-on to prevent text bleeding through in Safari.
        front.animate([
          { opacity: 1, offset: 0, easing: "steps(1, end)" },
          { opacity: 0, offset: .5 },
          { opacity: 0, offset: 1 }
        ], timing),
        back.animate([
          { opacity: 0, offset: 0, easing: "steps(1, end)" },
          { opacity: 1, offset: .5 },
          { opacity: 1, offset: 1 }
        ], timing)
      ];
      if (targetBounds) {
        // Keep long pages at viewport scale while turning. The lower edge stays
        // below the viewport; normal document scrolling takes over on arrival.
        const visibleHeight = Math.min(targetBounds.height, innerHeight - targetBounds.top + 40);
        // Lay out the reverse once at its final width. Animate only transforms,
        // so line wrapping and container-query typography cannot jump mid-turn.
        const startLeft = parseFloat(scene.style.left);
        const startTop = parseFloat(scene.style.top);
        const endLeft = targetBounds.left - originX;
        const endTop = targetBounds.top - originY;
        Object.assign(scene.style, {
          left: endLeft + "px", top: endTop + "px",
          width: targetBounds.width + "px", height: visibleHeight + "px",
          perspective: "2200px", transformOrigin: "0 0", willChange: "transform"
        });
        // Preserve the starting face's original proportions inside the scaled scene.
        Object.assign(front.firstElementChild.style, {
          width: width + "px", height: height + "px", transformOrigin: "0 0",
          transform: `scale(${targetBounds.width / width}, ${visibleHeight / height})`
        });
        animations.push(scene.animate([
          {transform: `translate(${startLeft - endLeft}px, ${startTop - endTop}px) scale(${width / targetBounds.width}, ${height / visibleHeight})`},
          {transform: "translate(0px, 0px) scale(1, 1)"}
        ], timing));

      }
      const finishOnResize = () => animations.forEach((animation) => animation.finish());
      window.addEventListener("resize", finishOnResize, { once: true });
      try { await Promise.all(animations.map((animation) => animation.finished)); }
      finally { window.removeEventListener("resize", finishOnResize); }
      window.location.assign(destination);
    } catch {
      restore();
      window.location.assign(destination);
    }
  }));
})();
