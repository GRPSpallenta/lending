import frappe

def execute():
    # Ensure 'Users' and 'Settings' workspaces are public and visible
    for label in ("Users", "Settings"):
        name = frappe.db.get_value("Workspace", {"label": label})
        if name:
            # set public and unhide
            frappe.db.set_value("Workspace", name, "public", 1)
            frappe.db.set_value("Workspace", name, "is_hidden", 0)
        else:
            # create if missing
            doc = frappe.get_doc({
                "doctype": "Workspace",
                "label": label,
                "title": label,
                "public": 1,
                "type": "Workspace",
                "content": "[]",
            })
            doc.insert(ignore_permissions=True)
    frappe.clear_cache()
