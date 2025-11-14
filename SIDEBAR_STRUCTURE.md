# Lending Sidebar Menu Structure

## Visual Hierarchy

```
Lending (expandable)
│
├── ▼ Shortcuts
│   ├── Company
│   ├── Loan Application
│   ├── Loan
│   └── Dashboard
│
├── ▼ Loan Security
│   ├── Loan Security Type
│   ├── Loan Security Price
│   ├── Loan Security
│   ├── Loan Security Assignment
│   ├── Loan Security Release
│   └── Loan Security Shortfall
│
├── ▼ Reports
│   ├── Loan Repayment and Closure
│   ├── Loan Security Status
│   ├── Loan Interest Report
│   ├── Loan Security Exposure
│   ├── Applicant-Wise Loan Security Exposure
│   └── Loan Security Status
│
├── ▼ Banking
│   ├── Bank
│   └── Bank Account
│
├── ▼ Loan Processes
│   ├── Process Loan Security Shortfall
│   ├── Process Loan Interest Accrual
│   ├── Process Loan Demand
│   └── Process Loan Classification
│
├── ▼ Loan Classification
│   ├── Loan Classification
│   ├── NPA Logs
│   └── Days Past Due Logs
│
├── ▼ Loan Transfers
│   ├── Branch
│   └── Loan Transfer
│
├── ▼ Co-Lending
│   └── Co Lending Partner
│
├── ▼ Loan
│   ├── Loan Category
│   ├── Loan Product
│   ├── Loan Application
│   ├── Loan
│   └── Loan Restructure
│
├── ▼ Loan Adjustments
│   ├── Loan Adjustment
│   ├── Loan Write Off
│   ├── Loan Refund
│   └── Loan Balance Adjustment
│
├── ▼ Taxes and Charges
│   ├── Applicant (Customer)
│   ├── Charge (Item)
│   ├── Invoices (Sales Invoice)
│   └── Taxes (Sales Taxes and Charges Template)
│
└── ▼ Disbursement and Repayment
    ├── Loan Disbursement
    ├── Loan Security Deposit
    ├── Loan Repayment Schedule
    ├── Loan Interest Accrual
    ├── Loan Demand
    └── Loan Repayment
```

## Link Types and Routes

### DocType Links
Format: `/app/{scrubbed-doctype-name}`

Examples:
- Loan Application → `/app/loan-application`
- Loan Security Type → `/app/loan-security-type`
- Bank Account → `/app/bank-account`

### Report Links
Format: `/app/query-report/{encoded-report-name}`

Examples:
- Loan Repayment and Closure → `/app/query-report/Loan%20Repayment%20and%20Closure`
- Loan Security Status → `/app/query-report/Loan%20Security%20Status`
- Loan Interest Report → `/app/query-report/Loan%20Interest%20Report`

### Dashboard Links
Format: `/app/dashboard/{scrubbed-dashboard-name}`

Examples:
- Dashboard → `/app/dashboard/loan-dashboard`

## Menu Group Details

### 1. Shortcuts (Quick Access)
**Purpose**: Frequently accessed items for quick navigation
**Items**: 4
**Type**: Mixed (DocType, Dashboard)

### 2. Loan Security
**Purpose**: Security management and collateral tracking
**Items**: 6
**Type**: DocType

### 3. Reports
**Purpose**: Analytical and status reports
**Items**: 6
**Type**: Query Reports

### 4. Banking
**Purpose**: Bank account and institution management
**Items**: 2
**Type**: DocType

### 5. Loan Processes
**Purpose**: Automated loan processing tasks
**Items**: 4
**Type**: DocType

### 6. Loan Classification
**Purpose**: Loan classification and NPA tracking
**Items**: 3
**Type**: DocType

### 7. Loan Transfers
**Purpose**: Branch transfers and loan movements
**Items**: 2
**Type**: DocType

### 8. Co-Lending
**Purpose**: Partner lending management
**Items**: 1
**Type**: DocType

### 9. Loan
**Purpose**: Core loan setup and management
**Items**: 5
**Type**: DocType

### 10. Loan Adjustments
**Purpose**: Loan corrections and balance adjustments
**Items**: 4
**Type**: DocType

### 11. Taxes and Charges
**Purpose**: Fee and tax management
**Items**: 4
**Type**: DocType (mapped to ERPNext core types)

### 12. Disbursement and Repayment
**Purpose**: Loan lifecycle transactions
**Items**: 6
**Type**: DocType

## Total Statistics

- **Total Groups**: 12
- **Total Menu Items**: 44
- **DocType Links**: 37
- **Report Links**: 6
- **Dashboard Links**: 1

## User Experience

### Before Implementation
- Shortcuts displayed as cards in workspace
- No hierarchical organization in sidebar
- All items visible on main workspace page

### After Implementation
- Clean hierarchical sidebar menu
- Logical grouping by function
- Expandable/collapsible groups
- Direct navigation from sidebar
- Workspace remains clean with charts and activity

## Benefits

1. **Better Organization**: Logical grouping by business function
2. **Quick Access**: All items accessible from sidebar
3. **Clean UI**: Workspace page less cluttered
4. **Consistent UX**: Follows Frappe/ERPNext sidebar patterns
5. **Scalable**: Easy to add new items by updating workspace JSON
6. **Maintainable**: Changes in workspace JSON automatically reflected

## Maintenance

To modify the menu structure:

1. Edit workspace JSON: `lending/loan_management/workspace/lending/lending.json`
2. Add/modify Card Breaks for groups
3. Add/modify Link items under groups
4. Clear cache: `bench clear-cache`
5. Restart: `bench restart`

The sidebar will automatically update to reflect changes.
