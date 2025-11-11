import frappe

def execute():
    name = frappe.db.get_value("Workspace", {"label": "Settings"})
    if name:
        # Use the standard gear icon token used across Frappe
        frappe.db.set_value("Workspace", name, "icon", "settings")
        frappe.clear_cache()
