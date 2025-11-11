import frappe
from typing import Dict, Any, List

# Allowed root labels
ALLOWED_ROOT = {"Lending", "Accounting", "CRM", "Home"}


def _group_under_settings(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    allowed = []
    others = []
    for it in items:
        label = (it.get("label") or it.get("name") or "").strip()
        if label in ALLOWED_ROOT:
            allowed.append(it)
        else:
            others.append(it)

    if not others:
        return items

    settings = {
        "label": "Settings",
        "icon": "settings",
        "is_expandable": 1,
        "items": others,
        "type": "Module",
        "name": "Settings",
    }

    # Order: Home (if any), Lending, Accounting, CRM, then Settings
    ordered = []
    def pick(lbl):
        for i in allowed:
            if (i.get("label") or i.get("name")) == lbl:
                ordered.append(i)
                break

    for lbl in ["Home", "Lending", "Accounting", "CRM"]:
        pick(lbl)

    ordered.append(settings)
    return ordered


@frappe.whitelist()
def get_workspace_sidebar_items() -> Dict[str, Any]:
    """
    Override of Frappe's sidebar items provider. Fetches original data and rewrites the
    'items' collection to include only Lending, Accounting, CRM, Home at root and groups
    all others under a synthetic 'Settings' group.
    """
    # Import lazily to avoid circular imports
    from frappe.desk.desktop import get_workspace_sidebar_items as core_get

    data = core_get()

    # Expected structure: { 'items': [ ... ] }
    items = data.get("items") or []
    data["items"] = _group_under_settings(items)
    return data
