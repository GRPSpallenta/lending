from datetime import date, timedelta
import os
import json

import frappe
from frappe.utils.user import is_website_user


def check_app_permission():
	if frappe.session.user == "Administrator":
		return True

	if is_website_user():
		return False

	return True


def daterange(start_date: date, end_date: date):
	days = int((end_date - start_date).days)
	for n in range(days + 1):
		yield start_date + timedelta(n)


def list_workspace_icons():
    """Utility to inspect current Workspace icon values.
    Returns list of dicts with label and icon.
    """
    rows = frappe.get_all("Workspace", fields=["label", "icon", "public", "is_hidden"], order_by="label")
    # print for bench execute visibility
    try:
        print(rows)
    except Exception:
        pass
    return rows


@frappe.whitelist()
def sync_lending_workspace_from_file():
    """Force-sync the 'Lending' Workspace from its JSON in this app.
    This is version-safe where sync_workspaces isn't available.
    """
    # Resolve file path inside the app
    app_path = frappe.get_app_path("lending")
    ws_path = os.path.join(
        app_path,
        "lending",
        "loan_management",
        "workspace",
        "lending",
        "lending.json",
    )
    if not os.path.exists(ws_path):
        frappe.throw(f"Workspace JSON not found at {ws_path}")

    with open(ws_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    name = data.get("name") or data.get("label") or "Lending"
    # Upsert Workspace doc
    if frappe.db.exists("Workspace", name):
        doc = frappe.get_doc("Workspace", name)
    else:
        doc = frappe.new_doc("Workspace")
        doc.name = name

    # Copy selected fields from file
    for field in [
        "app",
        "charts",
        "content",
        "custom_blocks",
        "icon",
        "indicator_color",
        "is_hidden",
        "label",
        "links",
        "module",
        "number_cards",
        "public",
        "quick_lists",
        "restrict_to_domain",
        "roles",
        "shortcuts",
        "title",
        "type",
    ]:
        if field in data:
            setattr(doc, field, data[field])

    # Ensure visibility
    doc.public = 1
    doc.is_hidden = 0

    # Save
    doc.flags.ignore_version = True
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"updated": name, "path": ws_path}


@frappe.whitelist()
def sidebar_summary():
    from lending.hooks import get_workspace_sidebar_items
    data = get_workspace_sidebar_items()
    items = data.get("items") or []
    roots = [(i.get("label") or i.get("name") or "").strip() for i in items]
    lending = next((i for i in items if (i.get("label") or i.get("name")) == "Lending"), {})
    groups = [g.get("label") for g in (lending.get("items") or [])]
    shortcuts = next((g for g in (lending.get("items") or []) if (g.get("label") == "Shortcuts")), {})
    shortcut_labels = [i.get("label") for i in (shortcuts.get("items") or [])]
    try:
        print({"roots": roots, "groups": groups, "shortcuts": shortcut_labels})
    except Exception:
        pass
    return {"roots": roots, "groups": groups, "shortcuts": shortcut_labels}
