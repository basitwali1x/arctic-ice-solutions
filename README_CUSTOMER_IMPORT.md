# Customer Import Documentation

## Overview
This document describes the import of 582 customers from the "West La Ice Customer List new.xlsx" file into the Arctic Ice Solutions system.

## Excel File Structure
The provided Excel file contains 4 sheets:
- **jasper**: 46 customers for Jasper Warehouse (loc_4)
- **leesville**: Empty sheet 
- **lufkin**: Empty sheet
- **all**: 581 customers to be distributed across locations

## Import Strategy

### 1. Jasper Customers (46 customers)
- Direct import from 'jasper' sheet to loc_4 (Jasper Warehouse)
- These customers are already properly categorized by location

### 2. All Sheet Customers (581 customers)
- Analyzed customer addresses to determine appropriate location assignments
- Distribution logic based on geographic proximity:

#### Location Assignment Rules:
- **loc_1 (Leesville HQ & Production)**: Louisiana customers near Leesville, DeRidder, Many, Zwolle
- **loc_2 (Lake Charles Distribution)**: Louisiana customers near Lake Charles, Sulphur, Westlake, Vinton  
- **loc_3 (Lufkin Distribution)**: Texas customers near Lufkin, Huntsville, Crockett, Livingston
- **loc_4 (Jasper Warehouse)**: Texas customers near Jasper, Newton, Hemphill, Woodville

#### Default Assignments:
- Unclear Texas addresses → Lufkin (loc_3) - main distribution center
- Unclear Louisiana addresses → Leesville (loc_1) - headquarters
- Unclear addresses → Lufkin (loc_3) - largest distribution center

## Import Process

### 1. Backend API Setup
```bash
cd ~/repos/arctic-ice-solutions/backend
poetry run fastapi dev app/main.py --host 0.0.0.0 --port 8000
```

### 2. Run Import Script
```bash
cd ~/repos/arctic-ice-solutions
python3 import_customers.py
```

### 3. Verify Results
```bash
python3 verify_import.py
```

## Expected Results
- **Total Customers**: 582
- **Jasper (loc_4)**: 46 customers (from jasper sheet)
- **Distribution from 'all' sheet**: 581 customers across all 4 locations
- **Deduplication**: Automatic removal of any duplicate customers

## Files Created
- `import_customers.py`: Main import script with address analysis
- `verify_import.py`: Verification script to check import results
- `README_CUSTOMER_IMPORT.md`: This documentation file

## System Integration
The import uses the existing bulk import system:
- **API Endpoint**: `/api/customers/bulk-import`
- **Processing Function**: `process_customer_excel_files()` in `excel_import.py`
- **Deduplication**: Built-in logic prevents duplicate customers
- **Data Storage**: Customers saved to `customers.json` and `customers_db`

## Verification Checklist
- [ ] Total customer count equals 582
- [ ] Customers properly distributed across 4 locations
- [ ] No duplicate customers created
- [ ] All customer data fields populated correctly
- [ ] Customers visible in frontend Customer Management page
