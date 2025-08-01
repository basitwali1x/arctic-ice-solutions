import pandas as pd
import sys

def analyze_excel_file(file_path, file_name):
    """Analyze an Excel file and extract route information"""
    print(f'=== {file_name} ===')
    
    try:
        xl_file = pd.ExcelFile(file_path)
        print(f'Available sheets: {xl_file.sheet_names}')
        
        results = {}
        
        for sheet_name in xl_file.sheet_names:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f'\nSheet: {sheet_name}')
                print(f'Shape: {df.shape}')
                print(f'Columns: {list(df.columns)}')
                
                if not df.empty:
                    df_str = df.astype(str)
                    
                    steve_rows = df_str[df_str.apply(lambda row: row.str.contains('steve|Steve|STEVE', case=False, na=False).any(), axis=1)]
                    francis_rows = df_str[df_str.apply(lambda row: row.str.contains('francis|Francis|FRANCIS', case=False, na=False).any(), axis=1)]
                    
                    if not steve_rows.empty:
                        print(f'\nFound Steve references in {sheet_name}:')
                        print(steve_rows.to_string())
                        
                    if not francis_rows.empty:
                        print(f'\nFound Francis references in {sheet_name}:')
                        print(francis_rows.to_string())
                
                print('\nFirst few rows:')
                print(df.head(5).to_string())
                
                results[sheet_name] = {
                    'shape': df.shape,
                    'columns': list(df.columns),
                    'has_steve': not steve_rows.empty if not df.empty else False,
                    'has_francis': not francis_rows.empty if not df.empty else False
                }
                
            except Exception as e:
                print(f'Error reading sheet {sheet_name}: {e}')
                results[sheet_name] = {'error': str(e)}
                
        return results
        
    except Exception as e:
        print(f'Error processing {file_name}: {e}')
        return {'error': str(e)}

print("Analyzing Excel files for Lake Charles drivers Steve and Francis...")
print("=" * 80)

lake_charles_results = analyze_excel_file(
    '/home/ubuntu/attachments/edbd745d-cd57-440b-8654-c08fcc9056b4/ROUTE+SHEETS2025-LAKE+CHARLES.xlsx',
    'LAKE CHARLES ROUTE SHEET'
)

print('\n' + '=' * 80 + '\n')

smitty_results = analyze_excel_file(
    '/home/ubuntu/attachments/367e454e-c6b9-47e4-beda-9c10aba35f3f/Route+Sheets+2025-DRIVER+SMITTY-CP.xlsx',
    'SMITTY ROUTE SHEET'
)

print('\n' + '=' * 80)
print('SUMMARY')
print('=' * 80)
print(f'Lake Charles file analysis: {lake_charles_results}')
print(f'Smitty file analysis: {smitty_results}')
