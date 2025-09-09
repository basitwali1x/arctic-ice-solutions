#!/usr/bin/env python3

import sys
import os
sys.path.append('app')

from pdf_import import extract_text_from_pdf, process_pdf_files, parse_invoice_pdf, parse_expense_pdf

def test_pdf_import_module():
    """Test that PDF import module loads and functions are available"""
    print("Testing PDF import module...")
    
    functions = [
        extract_text_from_pdf,
        process_pdf_files, 
        parse_invoice_pdf,
        parse_expense_pdf
    ]
    
    print("✓ All PDF import functions loaded successfully")
    
    test_text = """
    INVOICE #12345
    Date: 08/27/2025
    Bill To: Test Customer
    Amount: $150.00
    Total: $150.00
    """
    
    try:
        result = parse_invoice_pdf(test_text, "loc_1", "Leesville")
        print(f"✓ Invoice parsing test successful: {len(result['customers'])} customers, {len(result['orders'])} orders")
        print(f"  - Total amount: ${result['total_amount']}")
    except Exception as e:
        print(f"✗ Invoice parsing test failed: {e}")
    
    try:
        expense_text = """
        EXPENSE RECEIPT
        Date: 08/27/2025
        Vendor: Test Vendor
        Amount: $75.50
        Category: Fuel
        """
        result = parse_expense_pdf(expense_text, "loc_1", "Leesville")
        print(f"✓ Expense parsing test successful: {len(result['expenses'])} expenses")
        print(f"  - Total amount: ${result['total_amount']}")
    except Exception as e:
        print(f"✗ Expense parsing test failed: {e}")
    
    print("PDF import module test completed!")

if __name__ == "__main__":
    test_pdf_import_module()
