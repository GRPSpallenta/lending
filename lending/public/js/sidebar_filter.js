/*
  Client-side desk sidebar reshaper.
  - Keep only Lending, Accounting, CRM at root.
  - Move everything else under a new Settings group.
*/

(function () {
  const ALLOW_ROOT = ["Lending", "Accounting", "CRM"];
  const SETTINGS_LABEL = "Settings";

  function getRootList() {
    // Typical structure: .desk-sidebar > .standard-sidebar-section > .standard-sidebar-items
    let rootList = document.querySelector(".desk-sidebar .standard-sidebar-section .standard-sidebar-items");
    if (rootList) return rootList;
    // Fallback: any first .standard-sidebar-items under .desk-sidebar
    rootList = document.querySelector(".desk-sidebar .standard-sidebar-items");
    return rootList || null;
  }

  function reshape() {
    const rootList = getRootList();
    if (!rootList) return false;

    // Collect items
    const items = Array.from(rootList.children).filter((el) => el.classList.contains("standard-sidebar-item"));
    if (!items.length) return false;

    // Separate allowed vs others
    const allowed = [];
    const others = [];
    items.forEach((li) => {
      const labelEl = li.querySelector(".sidebar-item-label, .item-label, a, span");
      const label = labelEl ? (labelEl.textContent || "").trim() : "";
      if (ALLOW_ROOT.includes(label) || label === "Home") {
        allowed.push(li);
      } else {
        others.push(li);
      }
    });

    if (!others.length) return true;

    // Build Settings collapsible
    let settings = rootList.querySelector(":scope > .standard-sidebar-item[data-custom-settings='1']");
    if (!settings) {
      settings = document.createElement("div");
      settings.className = "standard-sidebar-item nested-container";
      settings.setAttribute("data-custom-settings", "1");
      settings.innerHTML = `
        <div class="sidebar-item-container">
          <span class="sidebar-item-label">${SETTINGS_LABEL}</span>
          <span class="icon small" style="margin-left:auto">▾</span>
        </div>
        <div class="standard-sidebar-items nested" style="display:none;"></div>
      `;
      rootList.prepend(settings);
      const header = settings.querySelector(".sidebar-item-container");
      const nested = settings.querySelector(".standard-sidebar-items.nested");
      header.addEventListener("click", () => {
        const show = nested.style.display === "none";
        nested.style.display = show ? "block" : "none";
      });
    }

    const nestedList = settings.querySelector(".standard-sidebar-items.nested");

    // Move other items into Settings
    others.forEach((li) => nestedList.appendChild(li));

    // Ensure allowed + Settings are at top
    // Ensure order: Settings first, then allowed in their current order
    rootList.prepend(settings);
    allowed.forEach((el) => rootList.appendChild(el));

    return true;
  }

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  ready(() => {
    const ok = reshape();
    if (ok) return;
    // Retry a few times as Desk mounts
    let tries = 0;
    const iv = setInterval(() => {
      tries += 1;
      if (reshape() || tries > 20) clearInterval(iv);
    }, 300);

    // Also watch for SPA navigations
    const obs = new MutationObserver(() => reshape());
    obs.observe(document.body, { childList: true, subtree: true });
  });
})();
