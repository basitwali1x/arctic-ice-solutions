#!/usr/bin/env python3

import pandas as pd
import sys
import os

def examine_excel_file(file_path):
    """Examine the structure of the Excel file"""
    try:
        print(f"Examining Excel file: {file_path}")
        print("=" * 50)
        
        excel_file = pd.ExcelFile(file_path)
        print(f"Sheet names: {excel_file.sheet_names}")
        print()
        
        for sheet_name in excel_file.sheet_names:
            print(f"Sheet: {sheet_name}")
            print("-" * 30)
            
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            print("\nFirst 5 rows:")
            print(df.head())
            print("\nData types:")
            print(df.dtypes)
            print("\n" + "=" * 50 + "\n")
            
    except Exception as e:
        print(f"Error examining file: {e}")
        return False
    
    return True

if __name__ == "__main__":
    file_path = "/home/ubuntu/attachments/29eaa1ae-7e6d-4a83-9bcf-a0d8177d108c/West+La+Ice+Customer+List.xlsx"
    
    if os.path.exists(file_path):
        examine_excel_file(file_path)
    else:
        print(f"File not found: {file_path}")
        sys.exit(1)
