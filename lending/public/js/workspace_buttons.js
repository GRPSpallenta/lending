(function(){
  try{ console.log("[lending] workspace_buttons loaded"); }catch(e){}
  function isWorkspacePage(){
    const route = (window.location.hash || window.location.pathname || "").toLowerCase();
    const hasWorkspaceRoot = !!document.querySelector(".workspace, .page-content .workspace-builder, .page-content .workspace");
    const inApp = /\/app\//.test(route);
    return inApp && hasWorkspaceRoot;
  }

  function findHeaderActions(){
    // Try several common header action containers used across Frappe versions
    const selectors = [
      ".page-head .page-actions",
      ".page-actions",
      ".page-head .actions",
      ".title-area .actions",
      ".page-head .page-actions-block",
    ];
    for (const sel of selectors){
      const el = document.querySelector(sel);
      if (el) return el;
    }
    return null;
  }

  function text(el){
    return (el.innerText || el.textContent || "").trim();
  }

  function matchLabelLike(el, label){
    const t = text(el).toLowerCase();
    const lbl = label.toLowerCase();
    if (!t) return false;
    return t === lbl || t.startsWith(lbl) || t.includes(` ${lbl}`) || t.includes(`${lbl} `);
  }

  function isButton(el){
    if (!el) return false;
    const tag = (el.tagName || "").toLowerCase();
    if (tag === "button") return true;
    if (tag === "a" && (el.classList.contains("btn") || el.getAttribute("role") === "button")) return true;
    return false;
  }

  function findWorkspaceContainer(){
    return (
      document.querySelector(".workspace") ||
      document.querySelector(".page-content .workspace") ||
      document.querySelector(".page-content")
    );
  }

  function findCandidateButtons(){
    const scope = findWorkspaceContainer() || document;
    const all = Array.from(scope.querySelectorAll("button, a.btn, a[role='button']"));
    return all.filter(isButton);
  }

  function locateButton(candidates, names){
    // names: ["Edit", "New"]
    for (const el of candidates){
      const t = text(el);
      const dl = el.getAttribute("data-label") || "";
      const title = el.getAttribute("title") || "";
      for (const name of names){
        if (
          matchLabelLike(el, name) ||
          dl.toLowerCase() === name.toLowerCase() ||
          title.toLowerCase() === name.toLowerCase()
        ){
          return el;
        }
      }
    }
    return null;
  }

  function moveButtons(){
    if (!isWorkspacePage()) return false;

    // 1) Prefer the global page header actions if available
    const headerActions = findHeaderActions();

    // 2) Also prepare a dedicated workspace header within the page content (right aligned)
    let contentHeader = document.querySelector(".desk-page .page-main-content .workspace-header");
    if (!contentHeader){
      const pageContent = document.querySelector(".desk-page .page-main-content") || document.querySelector(".page-content") || document.querySelector(".workspace");
      if (pageContent){
        contentHeader = document.createElement("div");
        contentHeader.className = "workspace-header";
        contentHeader.style.display = "flex";
        contentHeader.style.justifyContent = "flex-end";
        contentHeader.style.gap = "8px";
        contentHeader.style.margin = "10px 0";
        // place at the very top of content area
        pageContent.prepend(contentHeader);
        try{ console.debug("[lending] workspace_buttons: injected .workspace-header into page content"); }catch(e){}
      }
    }

    if (!headerActions && !contentHeader){
      try{ console.debug("[lending] workspace_buttons: no header containers available"); }catch(e){}
      // still proceed to pick buttons to ensure next mutation move can place them
    }

    const candidates = findCandidateButtons();
    if (!candidates.length) return false;

    const editBtn = locateButton(candidates, ["Edit"]);
    const newBtn  = locateButton(candidates, ["New", "+ New", "Create New"]);

    let moved = false;

    function styleBtn(btn){
      if (!btn) return;
      // Keep existing classes; just ensure spacing when placed in header
      btn.style.marginLeft = btn.style.marginLeft || "6px";
    }

    function place(btn){
      if (!btn) return false;
      styleBtn(btn);
      if (headerActions && !headerActions.contains(btn)){
        headerActions.appendChild(btn);
        return true;
      }
      if (contentHeader && !contentHeader.contains(btn)){
        contentHeader.appendChild(btn);
        return true;
      }
      return false;
    }

    if (editBtn && place(editBtn)){
      moved = true;
      try{ console.debug("[lending] workspace_buttons: moved Edit to header container"); }catch(e){}
    }
    if (newBtn && place(newBtn)){
      moved = true;
      try{ console.debug("[lending] workspace_buttons: moved New to header container"); }catch(e){}
    }

    return moved;
  }

  function ready(fn){
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn); else fn();
  }

  ready(function(){
    let tries = 0;
    const attempt = function(){
      tries += 1;
      if (moveButtons() || tries > 60) clearInterval(iv);
    };
    const iv = setInterval(attempt, 250);

    const mo = new MutationObserver(function(){ moveButtons(); });
    mo.observe(document.body, { childList: true, subtree: true });
  });
})();
