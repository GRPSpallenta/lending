import frappe

def execute():
    if not frappe.db.exists("Workspace", {"label": "Users"}):
        ws = frappe.get_doc({
            "doctype": "Workspace",
            "label": "Users",
            "title": "Users",
            "public": 1,
            "icon": "users",
            "type": "Workspace",
            "content": "[]",
        })
        ws.insert(ignore_permissions=True)
