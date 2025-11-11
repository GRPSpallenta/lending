(function () {
  function gotoLendingIfHome() {
    if (typeof frappe === "undefined" || !frappe.router || !frappe.get_route) return;
    try {
      const route = frappe.get_route();
      const isHome = !route || !route.length || route[0] === "home";
      if (isHome) {
        frappe.set_route("lending");
      }
    } catch (e) {
      // no-op
    }
  }

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  ready(() => {
    gotoLendingIfHome();
    if (window.frappe && frappe.router && frappe.router.on) {
      frappe.router.on("change", gotoLendingIfHome);
    }
  });
})();
