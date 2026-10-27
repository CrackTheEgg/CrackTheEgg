"use strict";

const card = document.querySelector("#business-card");
const menu = document.querySelector("#site-menu");

if (card && menu) {
  card.addEventListener("click", () => {
    menu.showModal();
    document.body.classList.add("menu-open");
  });

  // Close only when the press begins AND ends outside the panel.
  let pressedOutside = false;
  const outsidePanel = (event) => {
    const bounds = menu.getBoundingClientRect();
    return event.clientX < bounds.left || event.clientX > bounds.right ||
      event.clientY < bounds.top || event.clientY > bounds.bottom;
  };
  menu.addEventListener("pointerdown", (event) => {
    pressedOutside = event.target === menu && outsidePanel(event);
  });
  menu.addEventListener("click", (event) => {
    if (pressedOutside && event.target === menu && outsidePanel(event)) menu.close();
    pressedOutside = false;
  });
  menu.addEventListener("close", () => {
    document.body.classList.remove("menu-open");
    card.focus({ preventScroll: true });
  });
  // Escape and the Back button use the dialog's native closing behaviour.
  window.addEventListener("pageshow", () => {
    if (menu.open) menu.close();
    document.body.classList.remove("menu-open");
  });
}
