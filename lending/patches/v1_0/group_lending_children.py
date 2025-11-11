import frappe


def execute():
    # Ensure the top-level parent exists and is public
    lending_ws = frappe.db.get_value("Workspace", {"label": "Lending"}, ["name", "public"], as_dict=True)
    if not lending_ws:
        return
    if not lending_ws.public:
        frappe.db.set_value("Workspace", lending_ws.name, "public", 1)

    # Move all public workspaces that belong to this app under 'Lending', excluding 'Lending' itself
    workspaces = frappe.get_all(
        "Workspace",
        filters={"app": "lending", "public": 1},
        fields=["name", "label", "parent_page"],
    )

    for ws in workspaces:
        if ws.get("label") == "Lending":
            continue
        if ws.get("parent_page") != "Lending":
            frappe.db.set_value("Workspace", ws["name"], "parent_page", "Lending")

    frappe.clear_cache()
