/*
  Client-side desk sidebar reshaper.
  - Keep only Lending, Accounting, CRM at root.
  - Move everything else under a new Settings group.
*/

(function () {
  try { console.log("[lending] sidebar_filter loaded"); } catch (e) {}
  const ALLOW_ROOT = ["Lending", "Accounting", "CRM", "Users"];
  const SETTINGS_LABEL = "Settings";
  const LENDING_GROUP_LABEL = "Lending";
  const LENDING_CHILDREN = new Set([
    "Loan origination",
    "Loan Origination",
    "Applications",
    "Disbursements",
    "Repayments",
    "Demands",
    "Repayment Schedule",
    "Financial Reports",
  ]);

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
    try { console.debug("[lending] sidebar_filter: rootList found"); } catch (e) {}

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
          <span class="chev" aria-hidden="true" style="margin-left:auto; transition: transform 160ms ease; display:inline-block;">▸</span>
        </div>
        <div class="standard-sidebar-items nested" style="display:none;"></div>
      `;
      rootList.prepend(settings);
      const header = settings.querySelector(".sidebar-item-container");
      const nested = settings.querySelector(".standard-sidebar-items.nested");
      const chev = settings.querySelector(".chev");
      header.addEventListener("click", () => {
        const show = nested.style.display === "none";
        nested.style.display = show ? "block" : "none";
        if (chev) chev.style.transform = show ? "rotate(90deg)" : "rotate(0deg)";
      });
    }

    const nestedList = settings.querySelector(".standard-sidebar-items.nested");

    // Move other items into Settings
    others.forEach((li) => nestedList.appendChild(li));

    // Group specific children under Lending
    const lendingRoot = allowed.find((el) => {
      const lbl = el.querySelector(".sidebar-item-label, .item-label, a, span");
      return lbl && (lbl.textContent || "").trim() === LENDING_GROUP_LABEL;
    });
    if (lendingRoot) {
      let lendNested = lendingRoot.querySelector(":scope > .standard-sidebar-items.nested");
      if (!lendNested) {
        const wrap = lendingRoot.querySelector(":scope > .sidebar-item-container") || lendingRoot;
        let chev = lendingRoot.querySelector(":scope > .chev");
        if (!chev && wrap) {
          chev = document.createElement("span");
          chev.className = "chev";
          chev.style.cssText = "margin-left:auto; transition: transform 160ms ease; display:inline-block;";
          chev.textContent = "▸";
          wrap.appendChild(chev);
          wrap.addEventListener("click", () => {
            const show = lendNested.style.display === "none";
            lendNested.style.display = show ? "block" : "none";
            chev.style.transform = show ? "rotate(90deg)" : "rotate(0deg)";
          });
        }
        lendNested = document.createElement("div");
        lendNested.className = "standard-sidebar-items nested";
        lendNested.style.display = "none";
        lendingRoot.appendChild(lendNested);
      }

      // Move target roots into Lending nested
      Array.from(rootList.children).forEach((li) => {
        if (!li.classList.contains("standard-sidebar-item")) return;
        if (li === lendingRoot || li === settings) return;
        const labelEl = li.querySelector(".sidebar-item-label, .item-label, a, span");
        const label = labelEl ? (labelEl.textContent || "").trim() : "";
        if (LENDING_CHILDREN.has(label)) {
          lendNested.appendChild(li);
        }
      });
    }

    // Ensure allowed + Settings are at top
    // Ensure order: Settings first, then allowed in their current order
    rootList.prepend(settings);
    allowed.forEach((el) => rootList.appendChild(el));
    try { console.debug("[lending] sidebar_filter: applied, allowed=", allowed.length, "others=", others.length); } catch (e) {}

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

// --- Workspace buttons relocation (runs here because this script is confirmed to load) ---
(function(){
  try { console.log("[lending] workspace_buttons piggyback loaded"); } catch(e) {}

  function findHeaderActions(){
    const sels = [
      ".page-head .page-actions",
      ".page-actions",
      ".title-area .actions",
    ];
    for (const s of sels){ const el = document.querySelector(s); if (el) return el; }
    return null;
  }

  function getPageContent(){
    return document.querySelector(".desk-page .page-main-content") || document.querySelector(".page-content");
  }

  function injectWorkspaceHeader(){
    const content = getPageContent();
    if (!content) return null;
    let hdr = content.querySelector(":scope > .workspace-header");
    if (!hdr){
      hdr = document.createElement("div");
      hdr.className = "workspace-header";
      hdr.style.display = "flex";
      hdr.style.justifyContent = "flex-end";
      hdr.style.gap = "8px";
      hdr.style.margin = "10px 0";
      content.prepend(hdr);
      try { console.debug("[lending] injected .workspace-header"); } catch(e) {}
    }
    return hdr;
  }

  function text(el){ return (el && (el.innerText || el.textContent) || "").trim(); }

  function moveButtons(){
    // Only on Workspace pages that render a footer
    const footer = document.querySelector(".workspace-footer");
    if (!footer) return false;

    const headerActions = findHeaderActions();
    const localHeader  = injectWorkspaceHeader();
    if (!headerActions && !localHeader) return false;

    // Find Edit/New among footer buttons
    const btns = Array.from(footer.querySelectorAll("button, a.btn, a[role='button']"));
    if (!btns.length) return false;
    const editBtn = btns.find(b => /(^|\s)edit(\s|$)/i.test(text(b)));
    const newBtn  = btns.find(b => /(^|\s)new(\s|$)/i.test(text(b)) || /^\+\s*new$/i.test(text(b)));

    function place(target, btn){ if (target && btn && !target.contains(btn)) { target.appendChild(btn); return true; } return false; }

    let moved = false;
    if (editBtn) moved = place(headerActions, editBtn) || place(localHeader, editBtn) || moved;
    if (newBtn)  moved = place(headerActions, newBtn)  || place(localHeader, newBtn)  || moved;

    if (moved) { try { console.debug("[lending] moved workspace buttons to header"); } catch(e) {} }
    return moved;
  }

  function boot(){
    let tries = 0;
    const iv = setInterval(() => {
      tries += 1;
      if (tries <= 5) {
        try {
          const footerCount = document.querySelectorAll('.workspace-footer').length;
          const headerCount = document.querySelectorAll('.page-head .page-actions, .page-actions, .title-area .actions').length;
          const btnTexts = Array.from(document.querySelectorAll('.workspace-footer button, .workspace-footer a.btn, .workspace-footer a[role="button"]')).map(b => (b.innerText||b.textContent||'').trim());
          console.debug('[lending] diag: footer=', footerCount, 'header=', headerCount, 'btns=', btnTexts);
        } catch(e) {}
      }
      if (moveButtons() || tries > 60) clearInterval(iv);
    }, 300);
    const mo = new MutationObserver(() => moveButtons());
    mo.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
