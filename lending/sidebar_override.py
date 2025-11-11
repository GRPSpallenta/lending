import frappe
from typing import Dict, Any, List

ALLOWED_ROOT = {"Lending", "Accounting", "CRM", "Users"}


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

    ordered = []

    def pick(lbl):
        for i in allowed:
            if (i.get("label") or i.get("name")) == lbl:
                ordered.append(i)
                break

    for lbl in ["Lending", "Accounting", "CRM", "Users"]:
        pick(lbl)

    ordered.append(settings)
    return ordered


def _resolve_core_provider():
    try:
        from frappe.desk.doctype.workspace.workspace import (
            get_workspace_sidebar_items as fn,
        )
        return fn
    except Exception:
        try:
            from frappe.desk.doctype.workspace.workspace import get_sidebar_items as fn
            return fn
        except Exception:
            from frappe.desk.desktop import get_workspace_sidebar_items as fn
            return fn


@frappe.whitelist()
def get_workspace_sidebar_items(*args, **kwargs) -> Dict[str, Any]:
    core_get = _resolve_core_provider()
    data = core_get(*args, **kwargs)
    items = data.get("items") or []
    data["items"] = _group_under_settings(items)
    return data
