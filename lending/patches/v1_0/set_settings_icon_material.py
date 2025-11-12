import frappe

def execute():
    name = frappe.db.get_value("Workspace", {"label": "Settings"})
    if name:
        frappe.db.set_value("Workspace", name, "icon", "material-outline:settings")
        frappe.clear_cache()
