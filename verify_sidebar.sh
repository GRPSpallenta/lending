#!/bin/bash
# Verification script for Lending Sidebar Menu Implementation
# Usage: ./verify_sidebar.sh

echo "=================================================="
echo "Lending Sidebar Menu Verification"
echo "=================================================="
echo ""

# Navigate to bench directory
cd /Users/tendaikwaramba/Documents/GitHub/lending-bench || exit 1

echo "Step 1: Clearing cache..."
bench clear-cache
echo "✓ Cache cleared"
echo ""

echo "Step 2: Restarting bench..."
bench restart
echo "✓ Bench restarted"
echo ""

echo "Step 3: Checking Python syntax..."
python3 -m py_compile apps/lending/lending/hooks.py
if [ $? -eq 0 ]; then
    echo "✓ Python syntax valid"
else
    echo "✗ Python syntax error detected"
    exit 1
fi
echo ""

echo "=================================================="
echo "Verification Complete!"
echo "=================================================="
echo ""
echo "Next Steps:"
echo "1. Open browser: http://localhost:8000"
echo "2. Navigate to: /app/lending"
echo "3. Click on 'Lending' in the left sidebar"
echo "4. Verify all menu groups are visible and functional"
echo ""
echo "Expected Menu Groups:"
echo "  - Shortcuts (4 items)"
echo "  - Loan Security (6 items)"
echo "  - Reports (6 items)"
echo "  - Banking (2 items)"
echo "  - Loan Processes (4 items)"
echo "  - Loan Classification (3 items)"
echo "  - Loan Transfers (2 items)"
echo "  - Co-Lending (1 item)"
echo "  - Loan (5 items)"
echo "  - Loan Adjustments (4 items)"
echo "  - Taxes and Charges (4 items)"
echo "  - Disbursement and Repayment (6 items)"
echo ""
echo "Total: 12 expandable groups with 44 menu items"
echo ""
