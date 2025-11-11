import frappe

SAFE_TOP_LEVEL = {"Lending", "Accounting", "CRM", "Home"}


def execute():
    # Ensure Settings workspace exists
    settings_name = frappe.db.get_value(
        "Workspace", {"label": "Settings"}, "name"
    )
    if not settings_name:
        ws = frappe.get_doc({
            "doctype": "Workspace",
            "label": "Settings",
            "title": "Settings",
            "public": 1,
            "icon": "settings",
            "type": "Workspace",
            "content": "[]",
        })
        ws.insert(ignore_permissions=True)
        settings_name = ws.name
    
    # Move all other public workspaces under Settings
    workspaces = frappe.get_all(
        "Workspace",
        filters={"public": 1},
        fields=["name", "label", "parent_page"],
    )

    for ws in workspaces:
        label = ws.get("label") or ""
        if label in SAFE_TOP_LEVEL:
            continue
        # Skip the Settings workspace itself
        if label == "Settings":
            continue
        if ws.get("parent_page") != "Settings":
            frappe.db.set_value("Workspace", ws["name"], "parent_page", "Settings")

    frappe.clear_cache()
