"use strict";

// Atlas website analytics is optional. No RUM code or session cookie is loaded
// until a visitor explicitly accepts the notice below.
(() => {
  if (location.protocol !== "https:" || location.hostname !== "christianhegarty.com") return;

  const preferenceKey = "atlas-analytics-consent-v1";
  const monitorId = "14dce7db-886f-4efc-8a12-a35e0e90f11a";
  let running = false;
  let pageChoice = null;

  const readChoice = () => {
    try { return localStorage.getItem(preferenceKey) || pageChoice; } catch { return pageChoice; }
  };
  const saveChoice = (choice) => {
    pageChoice = choice;
    try { localStorage.setItem(preferenceKey, choice); } catch { /* This page only. */ }
  };
  const clearRumStorage = () => {
    for (const name of ["cwr_s", "cwr_u"]) {
      document.cookie = `${name}=; Max-Age=0; path=/; SameSite=Strict; Secure`;
      document.cookie = `${name}=; Max-Age=0; path=/; domain=${location.hostname}; SameSite=Strict; Secure`;
    }
    for (const key of ["cwr_c", "cwr_i"]) {
      try { localStorage.removeItem(key); } catch { /* Storage may be disabled. */ }
    }
  };

  const startRum = () => {
    if (running || readChoice() !== "accepted") return;
    running = true;
    const config = {
      sessionSampleRate: 1,
      identityPoolId: "eu-west-2:a6677c3c-5f21-4857-a8dd-43c53884936b",
      endpoint: "https://dataplane.rum.eu-west-2.amazonaws.com",
      telemetries: [],
      allowCookies: true,
      userIdRetentionDays: 0,
      enableXRay: false,
      recordResourceUrl: false,
      cookieAttributes: { domain: location.hostname, path: "/", sameSite: "Strict", secure: true }
    };
    const client = window.AwsRumClient = {
      q: [], n: "cwr", i: monitorId, v: "1.0.0", r: "eu-west-2", c: config
    };
    window.cwr = (command, payload) => client.q.push({ c: command, p: payload });
    const script = document.createElement("script");
    script.async = true;
    script.src = "https://client.rum.us-east-1.amazonaws.com/3.0.0/cwr.js";
    document.head.append(script);
  };

  const panel = document.createElement("section");
  panel.className = "atlas-analytics-panel";
  panel.setAttribute("aria-label", "Website analytics choice");
  panel.innerHTML = '<p><strong>Help us understand visits?</strong> If you allow analytics, AWS CloudWatch RUM counts your website session and page views using a short-lived session cookie. AWS also receives basic browser and device details. There is no advertising tracking. You can change your choice at any time. <a href="/dashboard.html#privacy">Learn more</a>.</p><div class="atlas-analytics-actions"><button type="button" data-analytics-choice="accepted">Allow analytics</button><button type="button" data-analytics-choice="declined">No thanks</button></div>';
  const settings = document.createElement("button");
  settings.type = "button";
  settings.className = "atlas-analytics-settings";
  settings.textContent = "Analytics settings";
  settings.addEventListener("click", () => {
    panel.hidden = false;
    settings.hidden = true;
  });
  panel.addEventListener("click", (event) => {
    const choice = event.target.closest("[data-analytics-choice]")?.dataset.analyticsChoice;
    if (!choice) return;
    const wasRunning = running;
    saveChoice(choice);
    panel.hidden = true;
    settings.hidden = false;
    if (choice === "accepted") startRum();
    else {
      clearRumStorage();
      // An already loaded RUM client is stopped by unloading this page.
      if (wasRunning) location.reload();
    }
  });
  document.body.append(panel, settings);
  const choice = readChoice();
  panel.hidden = choice === "accepted" || choice === "declined";
  settings.hidden = !panel.hidden;
  if (choice === "accepted") startRum();
})();
