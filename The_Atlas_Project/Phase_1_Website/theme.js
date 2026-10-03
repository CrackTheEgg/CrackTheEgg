"use strict";

// A temporary URL preference makes either appearance easy to review.
// Without this parameter, the stylesheet follows the device automatically.
const appearance = new URLSearchParams(window.location.search).get("theme");
if (appearance === "dark" || appearance === "light") {
  document.querySelector("#dark-theme").media = appearance === "dark" ? "all" : "not all";
  document.querySelectorAll('meta[name="theme-color"]').forEach((meta) => meta.remove());
  const themeColor = document.createElement("meta");
  themeColor.name = "theme-color";
  themeColor.content = appearance === "dark" ? "#101923" : "#f4f4f1";
  document.head.append(themeColor);
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('a[href$=".html"]').forEach((link) => {
      link.href += "?theme=" + appearance;
    });
  });
}
