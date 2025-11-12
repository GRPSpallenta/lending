from datetime import date, timedelta

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
