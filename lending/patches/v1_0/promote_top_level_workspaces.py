import frappe

TOP_LEVEL = {"Lending", "Accounting", "CRM", "Users", "Settings"}


def execute():
    for label in TOP_LEVEL:
        name = frappe.db.get_value("Workspace", {"label": label})
        if not name:
            continue
        frappe.db.set_value("Workspace", name, "parent_page", "")
        frappe.db.set_value("Workspace", name, "public", 1)
        frappe.db.set_value("Workspace", name, "is_hidden", 0)
    frappe.clear_cache()
