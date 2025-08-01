# Data Import Setup Guide

## Google Sheets Integration

### Prerequisites
1. Google Cloud Project with Sheets API enabled
2. Service Account with appropriate permissions
3. Service Account JSON key file

### Setup Steps

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Google Sheets API**
   - Navigate to APIs & Services > Library
   - Search for "Google Sheets API"
   - Click "Enable"

3. **Create Service Account**
   - Go to APIs & Services > Credentials
   - Click "Create Credentials" > "Service Account"
   - Fill in service account details
   - Download the JSON key file

4. **Configure Environment**
   - Copy the entire JSON content from the downloaded file
   - Set `GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON` in your `.env` file
   - The JSON should be on a single line (escape quotes if needed)

5. **Share Spreadsheet**
   - Open your Google Sheet
   - Click "Share"
   - Add the service account email (found in the JSON file)
   - Give "Viewer" or "Editor" permissions

### Testing Connection
Use the test endpoint to verify your setup:
```
GET /api/import/test-google-sheets
```

## Excel Import

### Supported Formats
1. **Standard Sales Data**
   - Required columns: Type, Date, Name, Amount, Item, Qty, Sales Price, Num
   - Type should be "Invoice" or "Sales Receipt"

2. **Timesheet Format**
   - Customer names in first column
   - 8lb quantities in column 3
   - 20lb quantities in column 4

3. **Customer List Format**
   - Required column: Customer
   - Optional columns: Address, Main Phone

### File Requirements
- Supported formats: .xlsx, .xls, .xlsm
- Files should not be password protected
- Data should start from row 1 with headers

## Troubleshooting

### Google Sheets Errors
- **Authentication Failed**: Check service account JSON format
- **Spreadsheet Not Found**: Verify sharing permissions
- **Invalid URL**: Ensure URL format is correct
- **No Data Found**: Check that sheet has headers and data

### Excel Import Errors
- **No Valid Data**: Verify column names and data format
- **File Type Error**: Ensure file has correct extension
- **Empty File**: Check that file contains actual data

### Common Issues
1. **Environment Variables**: Ensure all required env vars are set
2. **Permissions**: Check file/sheet access permissions
3. **Data Format**: Verify data matches expected format
4. **Network**: Ensure internet connectivity for Google Sheets

## Data Validation

The import system validates:
- Required columns are present
- Data types are correct
- Dates are valid
- Numeric values are properly formatted
- Duplicate customers are removed

## Location Mapping

Data is imported to specific locations:
- loc_1: Leesville HQ & Production
- loc_2: Lake Charles Distribution  
- loc_3: Lufkin Distribution
- loc_4: Jasper Warehouse

Each import operation requires specifying the target location.
