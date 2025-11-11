import frappe

@frappe.whitelist()
def sidebar_status():
    info = {
        "boot_patched": bool(getattr(frappe.flags, "lending_sidebar_patched", False)),
        "provider_locations": [],
    }
    # Probe bound functions
    try:
        from frappe.desk.doctype import workspace as ws_pkg  # type: ignore
        ws_mod = getattr(ws_pkg, "workspace", None)
        if ws_mod:
            info["provider_locations"].append(
                {
                    "module": "frappe.desk.doctype.workspace.workspace",
                    "has_get_sidebar_items": hasattr(ws_mod, "get_sidebar_items"),
                    "has_get_workspace_sidebar_items": hasattr(ws_mod, "get_workspace_sidebar_items"),
                }
            )
    except Exception:
        pass
    try:
        import frappe.desk.desktop as desktop  # type: ignore
        info["provider_locations"].append(
            {
                "module": "frappe.desk.desktop",
                "has_get_workspace_sidebar_items": hasattr(desktop, "get_workspace_sidebar_items"),
            }
        )
    except Exception:
        pass
    return info
