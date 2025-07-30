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

file_path = "/home/ubuntu/attachments/29eaa1ae-7e6d-4a83-9bcf-a0d8177d108c/West+La+Ice+Customer+List.xlsx"

examine_excel_file(file_path)
