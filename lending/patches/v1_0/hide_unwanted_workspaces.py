import frappe

ALLOWED = {"Lending", "Accounting", "CRM", "Users", "Settings"}


def execute():
    # Hide all public Workspaces not in ALLOWED
    workspaces = frappe.get_all(
        "Workspace",
        filters={"public": 1},
        fields=["name", "label", "is_hidden"],
    )
    for ws in workspaces:
        label = (ws.get("label") or ws.get("name") or "").strip()
        if label in ALLOWED:
            if ws.get("is_hidden"):
                frappe.db.set_value("Workspace", ws["name"], "is_hidden", 0)
        else:
            if not ws.get("is_hidden"):
                frappe.db.set_value("Workspace", ws["name"], "is_hidden", 1)
    frappe.clear_cache()
