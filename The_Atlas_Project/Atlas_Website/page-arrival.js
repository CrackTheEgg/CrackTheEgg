"use strict";

// Read before first paint so the normal page never flashes behind the opening card.
(() => {
  let arrival;
  try {
    arrival = JSON.parse(sessionStorage.getItem("portfolio-page-arrival"));
    sessionStorage.removeItem("portfolio-page-arrival");
  } catch { return; }
  if (!arrival || arrival.path !== location.pathname || Date.now() - arrival.time > 5000 ||
      matchMedia("(prefers-reduced-motion: reduce)").matches ||
      ![arrival.left, arrival.top, arrival.width, arrival.height].every(Number.isFinite) ||
      arrival.viewportWidth !== innerWidth || arrival.viewportHeight !== innerHeight) return;

  const root = document.documentElement;
  root.classList.add("page-arriving");
  let cover;
  let animations = [];
  const reveal = () => {
    root.classList.remove("page-arriving");
    cover?.remove();
    animations.forEach(animation => animation.cancel());
    animations = [];
  };
  // Always restore the real page, including browser Back/Forward cache restores.
  window.addEventListener("pageshow", event => { if (event.persisted) reveal(); });
  const safeguard = setTimeout(reveal, 1800);
  document.addEventListener("DOMContentLoaded", async () => {
    const page = document.querySelector(".page");
    const motion = matchMedia("(prefers-reduced-motion: reduce)");
    const initialWidth = innerWidth;
    const initialHeight = innerHeight;
    const finishOnResize = () => {
      if (innerWidth !== initialWidth || innerHeight !== initialHeight) reveal();
    };
    const finishOnMotion = () => { if (motion.matches) reveal(); };
    window.addEventListener("resize", finishOnResize);
    motion.addEventListener("change", finishOnMotion);
    try {
      if (!page?.animate || motion.matches) return;
      if (!arrival.sizeReached) {
        const target = page.getBoundingClientRect();
        cover = document.createElement("div");
        cover.className = "business-card page-arrival-card";
        cover.setAttribute("aria-hidden", "true");
        cover.inert = true;
        const title = document.createElement("span");
        title.className = "page-flip-title";
        title.textContent = arrival.title;
        cover.append(title);
        document.body.append(cover);
        const start = {left: arrival.left + "px", top: arrival.top + "px", width: arrival.width + "px", height: arrival.height + "px"};
        const end = {left: target.left + "px", top: target.top + "px", width: target.width + "px", height: target.height + "px"};
        Object.assign(cover.style, start);
        animations = [
          cover.animate([start, end], {duration: 420, easing: "cubic-bezier(.22, .7, .2, 1)", fill: "forwards"}),
          title.animate([{opacity: 1}, {opacity: 0}], {duration: 180, fill: "forwards"})
        ];
        await animations[0].finished;
        // Switch identical paper surfaces, then bring in the full-size text.
        root.classList.remove("page-arriving");
        cover.remove();
      } else {
        // The card already reached the page bounds during its turn.
        root.classList.remove("page-arriving");
      }
      animations = Array.from(page.children).map(child => child.animate(
        [{opacity: 0, transform: "translateY(5px)"}, {opacity: 1, transform: "translateY(0)"}],
        {duration: 200, easing: "ease-out"}
      ));
      await Promise.all(animations.map(animation => animation.finished));
    } catch { /* Interrupted motion immediately reveals the usable page. */ }
    finally {
      clearTimeout(safeguard);
      window.removeEventListener("resize", finishOnResize);
      motion.removeEventListener("change", finishOnMotion);
      reveal();
    }
  }, {once: true});
})();
