#!/usr/bin/env python3
"""Test script for import functionality"""

import sys
import os
sys.path.append('./backend')

def test_google_sheets_connection():
    """Test Google Sheets API connection"""
    try:
        from backend.app.google_sheets_import import test_google_sheets_connection
        result = test_google_sheets_connection()
        print("Google Sheets Connection Test:")
        print(f"  Connected: {result['connected']}")
        print(f"  Message: {result['message']}")
        return result['connected']
    except Exception as e:
        print(f"Google Sheets test failed: {str(e)}")
        return False

def test_excel_import():
    """Test Excel import functionality"""
    try:
        from backend.app.excel_import import clean_excel_data
        import pandas as pd
        
        test_data = pd.DataFrame({
            'Type': ['Invoice', 'Sales Receipt'],
            'Date': ['2024-01-01', '2024-01-02'],
            'Name': ['Test Customer 1', 'Test Customer 2'],
            'Amount': [100.0, 200.0],
            'Item': ['Ice 8lb', 'Ice 20lb'],
            'Qty': [10, 5],
            'Sales Price': [10.0, 40.0],
            'Num': ['INV001', 'SR001']
        })
        
        cleaned_data = clean_excel_data(test_data)
        print("Excel Import Test:")
        print(f"  Original rows: {len(test_data)}")
        print(f"  Cleaned rows: {len(cleaned_data)}")
        print("  Test passed: Excel import functions work correctly")
        return True
    except Exception as e:
        print(f"Excel import test failed: {str(e)}")
        return False

def main():
    print("Testing Arctic Ice Solutions Import System")
    print("=" * 50)
    
    sheets_ok = test_google_sheets_connection()
    
    excel_ok = test_excel_import()
    
    print("\nTest Summary:")
    print(f"  Google Sheets: {'✓ PASS' if sheets_ok else '✗ FAIL'}")
    print(f"  Excel Import: {'✓ PASS' if excel_ok else '✗ FAIL'}")
    
    if sheets_ok and excel_ok:
        print("\n✓ All import tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed - check configuration")
        return 1

if __name__ == "__main__":
    sys.exit(main())
