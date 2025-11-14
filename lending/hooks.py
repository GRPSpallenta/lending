app_name = "lending"
app_title = "Lending"
app_publisher = "Frappe Technologies Pvt. Ltd."
app_description = "Open Source Lending software"
app_email = "contact@frappe.io"
app_license = "GNU General Public License (v3)"
required_apps = ["erpnext"]

from typing import Dict, Any, List
from urllib.parse import quote
import frappe

ALLOWED_ROOT = {"Lending", "Accounting", "CRM", "Users"}
SUPPRESS_ROOTS = {
    "Loan origination",
    "Loan Origination",
    "Applications",
    "Disbursements",
    "Repayments",
    "Demands",
    "Repayment Schedule",
    "Financial Reports",
}


def _group_under_settings(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    allowed = []
    others = []
    for it in items:
        label = (it.get("label") or it.get("name") or "").strip()
        if label in ALLOWED_ROOT:
            allowed.append(it)
        else:
            if label not in SUPPRESS_ROOTS:
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
    # Guard against recursion if core_get points back to this function (due to patches)
    if getattr(core_get, "__module__", "") == __name__:
        # Build minimal items from Workspace docs
        ws_list = frappe.get_all(
            "Workspace",
            filters={"public": 1, "is_hidden": 0},
            fields=["name", "label", "icon", "module", "parent_page"],
        )
        roots = [
            {
                "name": w["name"],
                "label": w.get("label") or w["name"],
                "icon": w.get("icon") or "",
                "module": w.get("module") or "",
                "is_hidden": 0,
                "public": 1,
            }
            for w in ws_list
            if not (w.get("parent_page") or "").strip()
        ]
        data = {"items": roots}
    else:
        data = core_get(*args, **kwargs)
    try:
        frappe.logger("lending").info(
            "sidebar_override called: items_in=%s", len((data or {}).get("items") or [])
        )
    except Exception:
        pass
    items = data.get("items") or []
    items = _group_under_settings(items)
    items = _attach_children(items)
    data["items"] = items
    return data


def _boot_patch_sidebar(session):
    """Monkey-patch workspace sidebar providers at boot to guarantee override usage."""
    try:
        from frappe.desk.doctype import workspace as ws_pkg  # type: ignore
        ws_mod = getattr(ws_pkg, "workspace", None)
        if ws_mod:
            try:
                ws_mod.get_sidebar_items = get_workspace_sidebar_items  # type: ignore
            except Exception:
                pass
            try:
                ws_mod.get_workspace_sidebar_items = get_workspace_sidebar_items  # type: ignore
            except Exception:
                pass
        # Also patch legacy location
        try:
            import frappe.desk.desktop as desktop
            desktop.get_workspace_sidebar_items = get_workspace_sidebar_items  # type: ignore
        except Exception:
            pass
        frappe.flags.lending_sidebar_patched = True
        frappe.logger("lending").info("sidebar providers monkey-patched at boot")
    except Exception:
        # Avoid breaking login/boot on any error
        pass
app_logo_url = "/assets/lending/images/grp-spallenta-logo.png"

def _route_for_link(link: Dict[str, Any]) -> str | None:
    lt = (link.get("link_type") or "").strip()
    to = (link.get("link_to") or link.get("label") or "").strip()
    if not to:
        return None
    if lt == "DocType":
        return f"/app/{frappe.scrub(to)}"
    if lt == "Report":
        return f"/app/query-report/{quote(to)}"
    if lt == "Dashboard":
        return f"/app/dashboard/{frappe.scrub(to)}"
    if lt == "Workspace":
        return f"/app/{frappe.scrub(to)}"
    return None


def _children_from_workspace(ws_name: str) -> List[Dict[str, Any]]:
    try:
        if not frappe.db.exists("Workspace", ws_name):
            return []
        ws = frappe.get_doc("Workspace", ws_name)
        rows = list(ws.get("links") or [])
    except Exception:
        return []

    groups: List[Dict[str, Any]] = []
    current: Dict[str, Any] | None = None

    def ensure_current(label: str):
        nonlocal current
        current = {
            "label": label or "Links",
            "is_expandable": 1,
            "type": "Module",
            "items": [],
        }
        groups.append(current)

    for r in rows:
        rtype = (r.get("type") or "").strip()
        if rtype == "Card Break":
            ensure_current(r.get("label") or "Group")
        elif rtype == "Link":
            if current is None:
                ensure_current("Links")
            item: Dict[str, Any] = {
                "label": r.get("label") or r.get("link_to") or "",
                "type": "Link",
                "link_type": r.get("link_type") or "",
                "link_to": r.get("link_to") or "",
            }
            route = _route_for_link(r)
            if route:
                item["route"] = route
            current["items"].append(item)

    return groups


def _attach_children(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for it in items:
        label = (it.get("label") or it.get("name") or "").strip()
        if label in ALLOWED_ROOT:
            # Special categorization for Lending
            if label == "Lending":
                children = _children_for_lending()
            else:
                children = _children_from_workspace(label)
            if children:
                it["is_expandable"] = 1
                it["items"] = children
        elif label == "Settings":
            # Expand each Settings child module using its Workspace links
            child_items = []
            for child in (it.get("items") or []):
                c_label = (child.get("label") or child.get("name") or "").strip()
                c = dict(child)
                c_children = _children_from_workspace(c_label)
                if c_children:
                    c["is_expandable"] = 1
                    c["items"] = c_children
                child_items.append(c)
            it["items"] = child_items
    return items


def _children_for_lending() -> List[Dict[str, Any]]:
    """
    Parse Lending workspace and convert all card breaks and shortcuts 
    into a hierarchical sidebar menu structure.
    """
    try:
        if not frappe.db.exists("Workspace", "Lending"):
            return []
        ws = frappe.get_doc("Workspace", "Lending")
        rows = list(ws.get("links") or [])
    except Exception:
        return []

    groups: List[Dict[str, Any]] = []
    current_group: Dict[str, Any] | None = None
    
    # First, add shortcuts section from workspace.shortcuts
    try:
        sc_rows = list(ws.get("shortcuts") or [])
    except Exception:
        sc_rows = []
    
    if sc_rows:
        sc_items: List[Dict[str, Any]] = []
        for s in sc_rows:
            lbl = (s.get("label") or s.get("link_to") or "").strip()
            if not lbl:
                continue
            item = {
                "label": lbl,
                "type": "Link",
                "link_type": s.get("type") or s.get("link_type") or "",
                "link_to": s.get("link_to") or "",
            }
            route = _route_for_link({
                "link_type": item["link_type"],
                "link_to": item["link_to"],
                "label": lbl,
            })
            if route:
                item["route"] = route
            sc_items.append(item)
        
        if sc_items:
            groups.append({
                "label": "Shortcuts",
                "is_expandable": 1,
                "type": "Module",
                "items": sc_items,
            })
    
    # Process all card breaks and their links from workspace.links
    for row in rows:
        row_type = (row.get("type") or "").strip()
        
        if row_type == "Card Break":
            # Start a new group
            group_label = (row.get("label") or "").strip()
            if group_label:
                current_group = {
                    "label": group_label,
                    "is_expandable": 1,
                    "type": "Module",
                    "items": [],
                }
                groups.append(current_group)
        
        elif row_type == "Link":
            # Skip hidden links
            if row.get("hidden"):
                continue
                
            # Add link to current group
            if current_group is not None:
                lbl = (row.get("label") or row.get("link_to") or "").strip()
                if not lbl:
                    continue
                    
                item = {
                    "label": lbl,
                    "type": "Link",
                    "link_type": row.get("link_type") or "",
                    "link_to": row.get("link_to") or "",
                }
                route = _route_for_link(row)
                if route:
                    item["route"] = route
                current_group["items"].append(item)
    
    # Remove empty groups
    groups = [g for g in groups if g.get("items")]
    
    # Fallback to default grouping if nothing matched
    if not groups:
        return _children_from_workspace("Lending")
    
    return groups

# Include custom CSS and JS to tweak Desk presentation
app_include_css = [
    "/assets/lending/css/lending_theme.css",
]
app_include_js = [
    "/assets/lending/js/landing_redirect.js",
    "/assets/lending/js/sidebar_filter.js",
    "/assets/lending/js/workspace_buttons.js",
    "lending.bundle.js",
]

# Ensure scripts load specifically on Desk too
desk_include_js = [
    "lending.bundle.js",
]

# Note: no server overrides for sidebar to avoid recursion in website/desk boot

add_to_apps_screen = [
    {
        "name": "lending",
        "logo": "/assets/lending/images/grp-spallenta-logo.png",
        "title": "Lending",
        "route": "/app/lending",
        "has_permission": "lending.app_utils.check_app_permission",
    }
]

# Brand for Desk header/sidebar
brand_html = (
    '<img class="app-logo" src="/assets/lending/images/grp-spallenta-logo.png" alt="GRP Spallenta"/>'
)

# Website context to ensure favicon and splash/logo use GRP Spallenta branding
website_context = {
    "favicon": "/assets/lending/images/favicon-32.png",
    "splash_image": "/assets/lending/images/grp-spallenta-logo.png",
}

# Ensure our sidebar override is active
boot_session = "lending.hooks._boot_patch_sidebar"

override_whitelisted_methods = {
    "frappe.desk.doctype.workspace.workspace.get_workspace_sidebar_items": "lending.hooks.get_workspace_sidebar_items",
    "frappe.desk.doctype.workspace.workspace.get_sidebar_items": "lending.hooks.get_workspace_sidebar_items",
    "frappe.desk.desktop.get_workspace_sidebar_items": "lending.hooks.get_workspace_sidebar_items",
}

audit_trail_doctypes = [
    # doctypes that make GL entries require Audit Trail to be maintained
    # as per the laws applicable to Companies in India
    "Loan Balance Adjustment",
    "Loan Disbursement",
    "Loan Interest Accrual",
    "Loan Refund",
    "Loan Repayment",
    "Loan Write Off",
	"Loan Disbursement",
	"Loan Interest Accrual",
	"Loan Refund",
	"Loan Repayment",
	"Loan Write Off",
]

voucher_subtypes = "lending.loan_management.doctype.loan.loan.get_voucher_subtypes"

before_tests = "lending.tests.test_utils.before_tests"

export_python_type_annotations = True

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/lending/css/lending.css"
# NOTE: app_include_js defined above as list including bundle and custom scripts

# fixtures
fixtures = [
	{"dt": "Role", "filters": [["role_name", "like", "Loan %"]]},
	{"dt": "Workflow", "filters": [["name", "=", "Loan Application Workflow"]]},
	{"dt": "Workflow State", "filters": [["name", "not in", ("Rejected", "Approved", "Pending")]]},
	{
		"dt": "Workflow Action Master",
		"filters": [["name", "not in", ("Reject", "Approve", "Review")]],
	},
]


# include js, css files in header of web template
# web_include_css = "/assets/lending/css/lending.css"
# web_include_js = "/assets/lending/js/lending.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "lending/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "lending.utils.jinja_methods",
# 	"filters": "lending.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "lending.install.before_install"
after_install = "lending.install.after_install"

# Uninstallation
# ------------

before_uninstall = "lending.install.before_uninstall"
# after_uninstall = "lending.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "lending.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Company": {
		"validate": "lending.overrides.company.validate_loan_tables",
	},
	"Sales Invoice": {
		"on_submit": [
			"lending.overrides.sales_invoice.generate_demand",
			"lending.overrides.sales_invoice.update_waived_amount_in_demand",
			"lending.overrides.sales_invoice.make_partner_charge_gl_entries",
			"lending.overrides.sales_invoice.make_suspense_gl_entry_for_charges",
		],
		"on_cancel": "lending.overrides.sales_invoice.cancel_demand",
		"validate": "lending.overrides.sales_invoice.validate",
	},
	"Custom Field": {
		"before_insert": "lending.overrides.custom_field.update_dimensions",
	},
}

accounting_dimension_doctypes = [
	"Loan",
	"Loan Disbursement",
	"Loan Interest Accrual",
	"Loan Demand",
	"Loan Repayment",
	"Loan Refund",
	"Sales Invoice",
	"Journal Entry",
]

repost_allowed_doctypes = [
	"Loan Repayment",
	"Loan Disbursement",
]
# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily_long": [
		"lending.loan_management.doctype.process_loan_interest_accrual.process_loan_interest_accrual.schedule_accrual",
		"lending.loan_management.doctype.process_loan_demand.process_loan_demand.process_daily_loan_demands",
		"lending.loan_management.doctype.process_loan_security_shortfall.process_loan_security_shortfall.create_process_loan_security_shortfall",
		"lending.loan_management.doctype.process_loan_classification.process_loan_classification.create_process_loan_classification",
		"lending.loan_management.doctype.loan.loan.auto_close_loc_loans",
	],
	"monthly_long": [
		"lending.loan_management.doctype.process_loan_restructure_limit.process_loan_restructure_limit.calculate_monthly_restructure_limit",
	],
}

bank_reconciliation_doctypes = [
	"Loan Repayment",
	"Loan Disbursement",
]

# Overriding Methods
# ------------------------------
get_matching_queries = "lending.loan_management.utils.get_matching_queries"

get_amounts_not_reflected_in_system_for_bank_reconciliation_statement = "lending.loan_management.utils.get_amounts_not_reflected_in_system_for_bank_reconciliation_statement"

get_payment_entries_for_bank_clearance = (
	"lending.loan_management.utils.get_payment_entries_for_bank_clearance"
)

get_entries_for_bank_clearance_summary = (
	"lending.loan_management.utils.get_entries_for_bank_clearance_summary"
)

get_entries_for_bank_reconciliation_statement = (
	"lending.loan_management.utils.get_entries_for_bank_reconciliation_statement"
)

# ERPNext doctypes for Global Search
global_search_doctypes = {
	"Default": [
		{"doctype": "Loan", "index": 44},
	],
}

update_gl_dict_with_app_based_fields = ["lending.overrides.gl_entry.update_value_date_in_gl_dict"]

#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "lending.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["lending.utils.before_request"]
# after_request = ["lending.utils.after_request"]

# Job Events
# ----------
# before_job = ["lending.utils.before_job"]
# after_job = ["lending.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"lending.auth.validate"
# ]
