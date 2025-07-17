import pandas as pd
import os

def examine_excel_file(file_path):
    print(f"\n=== Examining {os.path.basename(file_path)} ===")
    
    try:
        xl_file = pd.ExcelFile(file_path)
        
        print(f"Sheet names: {xl_file.sheet_names}")
        
        for sheet_name in xl_file.sheet_names:
            print(f"\n--- Sheet: {sheet_name} ---")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            
            print("\nFirst 5 rows:")
            print(df.head())
            
            print(f"\nData types:")
            print(df.dtypes)
            
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                print(f"\nNumeric column stats:")
                print(df[numeric_cols].describe())
                
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

file1 = "/home/ubuntu/attachments/418624df-adb6-499d-b079-ab07e0c61330/Sales+from+A+to+Sunshine+8.xlsx"
file2 = "/home/ubuntu/attachments/01dcbd43-dddd-487e-b716-3453dce10246/Sales+from+Sunshine+9+to+Z.xlsx"

examine_excel_file(file1)
examine_excel_file(file2)
