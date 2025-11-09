import frappe
from frappe.utils import nowdate, add_months
from frappe import _

# Idempotent demo data seeder for Lending
# Usage:
# bench --site <site> execute lending.demo.seed.run --kwargs '{"company":"<Company Name>", "suffix":"Demo"}'


def _get_or_create_customer(name: str = "Demo Customer"):
    if frappe.db.exists("Customer", {"customer_name": name}):
        return frappe.get_doc("Customer", {"customer_name": name}).name
    c = frappe.new_doc("Customer")
    c.customer_name = name
    c.type = "Company"
    c.insert()
    return c.name


def _pick_account(company: str, account_type: str | None = None, root_type: str | None = None):
    filters = {"company": company, "is_group": 0}
    if account_type:
        filters["account_type"] = account_type
    if root_type:
        filters["root_type"] = root_type
    name = frappe.db.get_value("Account", filters, "name")
    if not name:
        # fallback to any leaf account in company
        name = frappe.db.get_value("Account", {"company": company, "is_group": 0}, "name")
    if not name:
        frappe.throw(_("No leaf accounts found in company {0}. Please complete Chart of Accounts setup.").format(company))
    return name


def _get_or_create_loan_product(company: str, product_code: str):
    if frappe.db.exists("Loan Product", product_code):
        return frappe.get_doc("Loan Product", product_code).name

    lp = frappe.new_doc("Loan Product")
    lp.product_code = product_code
    lp.product_name = product_code
    lp.company = company
    lp.is_term_loan = 1
    lp.maximum_loan_amount = 1000000
    lp.rate_of_interest = 18

    # Accounts - pick reasonable defaults from CoA
    lp.payment_account = _pick_account(company, account_type="Cash", root_type="Asset") or _pick_account(company, root_type="Asset")
    lp.loan_account = _pick_account(company, root_type="Asset")
    lp.interest_income_account = _pick_account(company, account_type="Income Account", root_type="Income") or _pick_account(company, root_type="Income")
    lp.penalty_income_account = _pick_account(company, root_type="Income")

    lp.insert()
    return lp.name


def _get_or_create_security(security_code: str = "GOLD-24K", haircut: float = 10.0, original_value: float = 200000):
    if frappe.db.exists("Loan Security", {"loan_security_code": security_code}):
        return frappe.get_doc("Loan Security", {"loan_security_code": security_code}).name
    # Ensure a Loan Security Type exists
    lst = frappe.db.get_value("Loan Security Type", {"loan_security_type_name": "Gold"}, "name")
    if not lst:
        lst_doc = frappe.new_doc("Loan Security Type")
        lst_doc.loan_security_type_name = "Gold"
        lst_doc.insert()
        lst = lst_doc.name

    sec = frappe.new_doc("Loan Security")
    sec.loan_security_code = security_code
    sec.loan_security_name = security_code
    sec.loan_security_type = lst
    sec.haircut = haircut
    sec.original_security_value = original_value
    sec.utilized_security_value = 0
    sec.insert()

    # Price for security
    if not frappe.db.exists("Loan Security Price", {"loan_security": sec.name}):
        sp = frappe.new_doc("Loan Security Price")
        sp.loan_security = sec.name
        sp.price = original_value
        sp.posting_date = nowdate()
        sp.insert()
    return sec.name


def _get_company_currency(company: str) -> str:
    cur = frappe.db.get_value("Company", company, "default_currency")
    if not cur:
        cur = frappe.db.get_single_value("Global Defaults", "default_currency")
    return cur or "USD"


def create_demo_flow(company: str, suffix: str = "Demo"):
    customer = _get_or_create_customer(f"{suffix} Customer")
    product = _get_or_create_loan_product(company, f"{suffix}-PL")
    security = _get_or_create_security()

    # Loan Application
    la_name = frappe.db.get_value("Loan Application", {"description": f"{suffix} Application"}, "name")
    if not la_name:
        la = frappe.new_doc("Loan Application")
        la.company = company
        la.applicant_type = "Customer"
        la.first_name = suffix
        la.last_name = "Applicant"
        la.applicant = customer
        la.posting_date = nowdate()
        la.is_secured_loan = 1
        la.is_term_loan = 1
        la.loan_product = product
        la.rate_of_interest = 18
        la.repayment_method = "Repay Over Number of Periods"
        la.repayment_periods = 12
        la.loan_amount = 100000
        la.append("proposed_pledges", {
            "loan_security": security,
            "qty": 1,
            "loan_security_price": 200000,
            "haircut": 10,
        })
        la.insert()
        la.submit()
        la_name = la.name

    # Loan from application
    loan_name = frappe.db.get_value("Loan", {"loan_application": la_name}, "name")
    if not loan_name:
        from lending.loan_management.doctype.loan_application.loan_application import create_loan
        loan = create_loan(la_name, submit=1)
        loan_name = loan.name

    # Disbursement
    disb_name = frappe.db.get_value("Loan Disbursement", {"against_loan": loan_name}, "name")
    if not disb_name:
        disb = frappe.new_doc("Loan Disbursement")
        disb.against_loan = loan_name
        disb.company = company
        disb.disbursement_date = nowdate()
        disb.repayment_method = "Repay Over Number of Periods"
        disb.repayment_frequency = "Monthly"
        disb.tenure = 12
        disb.disbursed_amount = 100000
        disb.insert()
        disb.submit()
        disb_name = disb.name

    # One mock repayment entry (Normal Repayment)
    rep_name = frappe.db.get_value("Loan Repayment", {"against_loan": loan_name}, "name")
    if not rep_name:
        rep = frappe.new_doc("Loan Repayment")
        rep.against_loan = loan_name
        rep.company = company
        rep.posting_date = nowdate()
        rep.repayment_type = "Normal Repayment"
        rep.amount_paid = 10000
        rep.insert()
        rep.submit()

    return {
        "customer": customer,
        "loan_product": product,
        "loan_application": la_name,
        "loan": loan_name,
        "disbursement": disb_name,
    }


def ensure_help_page(company: str):
    slug = "lending-demo-guide"
    title = "Lending Demo Guide"
    body = (
        "# Lending App Demo Guide\n\n"
        "## Overview\n"
        "This guide walks you through the end-to-end loan flow using the seeded demo data.\n\n"
        "## Steps\n"
        "1. Open the Loan Application created for the demo and review pledges.\n"
        "2. Review the mapped Loan document.\n"
        "3. Open the Loan Disbursement and its generated Repayment Schedule.\n"
        "4. Review the Loan Repayment entry.\n\n"
        "## Key Doctypes\n"
        "- Loan Product\n- Loan Application\n- Loan\n- Loan Disbursement\n- Loan Repayment\n- Loan Demand (generated)\n\n"
        f"This demo was generated for company: {company}.\n"
    )
    # Use Web Page (built-in) for KB-like page
    if frappe.db.exists("Web Page", slug):
        wp = frappe.get_doc("Web Page", slug)
        wp.published = 1
        wp.title = title
        wp.main_section = body
        wp.save()
        return wp.name
    wp = frappe.new_doc("Web Page")
    wp.route = slug
    wp.title = title
    wp.published = 1
    wp.main_section = body
    wp.insert()
    return wp.name


def run(company: str, suffix: str = "Demo"):
    frappe.flags.ignore_permissions = True
    out = create_demo_flow(company, suffix)
    kb = ensure_help_page(company)
    frappe.db.commit()
    return {**out, "help_page": kb}
