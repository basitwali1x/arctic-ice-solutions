import pandas as pd
import json

def extract_route_data_focused(file_path, file_name):
    """Extract route data with focus on actual content, not just structure"""
    print(f'=== {file_name} ===')
    
    try:
        xl_file = pd.ExcelFile(file_path)
        print(f'Available sheets: {xl_file.sheet_names}')
        
        route_data = {}
        
        for sheet_name in xl_file.sheet_names:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                if df.empty:
                    continue
                
                print(f'\n--- Sheet: {sheet_name} ---')
                print(f'Shape: {df.shape}')
                
                df = df.dropna(how='all').dropna(axis=1, how='all')
                
                if df.empty:
                    print('Sheet is empty after cleaning')
                    continue
                
                meaningful_data = []
                
                for idx, row in df.iterrows():
                    row_data = []
                    for col in df.columns:
                        val = row[col]
                        if pd.notna(val) and str(val).strip() != '':
                            row_data.append(str(val).strip())
                    
                    if row_data:  # Only include rows with actual data
                        meaningful_data.append(row_data)
                
                if meaningful_data:
                    print(f'Found {len(meaningful_data)} rows with data')
                    
                    for i, row_data in enumerate(meaningful_data[:10]):
                        print(f'Row {i+1}: {row_data}')
                    
                    if len(meaningful_data) > 10:
                        print(f'... and {len(meaningful_data) - 10} more rows')
                    
                    route_data[sheet_name] = meaningful_data
                else:
                    print('No meaningful data found')
                    
            except Exception as e:
                print(f'Error reading sheet {sheet_name}: {e}')
                
        return route_data
        
    except Exception as e:
        print(f'Error processing {file_name}: {e}')
        return {}

print("Extracting route data for Lake Charles drivers...")
print("=" * 80)

lake_charles_data = extract_route_data_focused(
    '/home/ubuntu/attachments/edbd745d-cd57-440b-8654-c08fcc9056b4/ROUTE+SHEETS2025-LAKE+CHARLES.xlsx',
    'LAKE CHARLES ROUTE SHEET'
)

print('\n' + '=' * 80 + '\n')

smitty_data = extract_route_data_focused(
    '/home/ubuntu/attachments/367e454e-c6b9-47e4-beda-9c10aba35f3f/Route+Sheets+2025-DRIVER+SMITTY-CP.xlsx',
    'SMITTY ROUTE SHEET'
)

with open('/home/ubuntu/lake_charles_routes.json', 'w') as f:
    json.dump(lake_charles_data, f, indent=2)

with open('/home/ubuntu/smitty_routes.json', 'w') as f:
    json.dump(smitty_data, f, indent=2)

print('\n' + '=' * 80)
print('ROUTE DATA EXTRACTION COMPLETE')
print('=' * 80)
print(f'Lake Charles sheets: {list(lake_charles_data.keys())}')
print(f'Smitty sheets: {list(smitty_data.keys())}')
print('\nData saved to lake_charles_routes.json and smitty_routes.json')
