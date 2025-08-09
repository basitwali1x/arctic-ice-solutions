from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import google.generativeai as genai
import os
from typing import Dict, List, Any
import json
from io import BytesIO

app = FastAPI(title="Arctic Ice AI Data Imports")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourchoiceice.com", "https://api.yourchoiceice.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

@app.post("/import/excel")
async def import_excel_with_ai(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Import Excel file with AI-powered field mapping"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be Excel format")
    
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))
        
        columns = df.columns.tolist()
        sample_data = df.head(3).to_dict('records')
        
        prompt = f"""
        Analyze this Excel data and suggest field mappings for an ice manufacturing business:
        
        Columns: {columns}
        Sample data: {sample_data}
        
        Map these to standard fields: customer_name, order_date, quantity, product_type, delivery_address, total_amount
        
        Return JSON format with suggested mappings and confidence scores.
        """
        
        response = model.generate_content(prompt)
        ai_suggestions = response.text
        
        return {
            "status": "success",
            "filename": file.filename,
            "rows_found": len(df),
            "columns": columns,
            "ai_suggestions": ai_suggestions,
            "preview_data": sample_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel import failed: {str(e)}")

@app.post("/import/quickbooks")
async def import_quickbooks_with_ai(company_id: str) -> Dict[str, Any]:
    """Import QuickBooks data with AI field mapping"""
    try:
        
        mock_qb_data = {
            "customers": [
                {"Id": "1", "Name": "Walmart Supercenter", "CompanyName": "Walmart Inc."},
                {"Id": "2", "Name": "HEB Grocery", "CompanyName": "HEB LP"}
            ],
            "invoices": [
                {"Id": "1", "CustomerRef": {"value": "1"}, "TotalAmt": 2450.00, "TxnDate": "2024-01-15"}
            ]
        }
        
        prompt = f"""
        Transform this QuickBooks data for an ice manufacturing business:
        {json.dumps(mock_qb_data, indent=2)}
        
        Suggest how to map this to our system fields and identify any data quality issues.
        """
        
        response = model.generate_content(prompt)
        ai_analysis = response.text
        
        return {
            "status": "success",
            "company_id": company_id,
            "data_found": mock_qb_data,
            "ai_analysis": ai_analysis,
            "redirect_uri": "https://yourchoiceice.com/auth/callback"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QuickBooks import failed: {str(e)}")

@app.post("/import/google-sheets")
async def import_google_sheets_with_ai(sheet_url: str) -> Dict[str, Any]:
    """Import Google Sheets data with AI field mapping"""
    try:
        if "docs.google.com/spreadsheets" not in sheet_url:
            raise HTTPException(status_code=400, detail="Invalid Google Sheets URL")
        
        mock_sheets_data = {
            "range": "Sheet1!A1:F100",
            "values": [
                ["Customer", "Date", "Quantity", "Product", "Address", "Total"],
                ["Walmart #1234", "2024-01-15", "50", "Ice Bags", "123 Main St", "$2450.00"],
                ["HEB Store #567", "2024-01-16", "30", "Block Ice", "456 Oak Ave", "$1800.00"]
            ]
        }
        
        prompt = f"""
        Analyze this Google Sheets data for an ice manufacturing business:
        {json.dumps(mock_sheets_data, indent=2)}
        
        Suggest field mappings and data validation rules. Identify any inconsistencies.
        """
        
        response = model.generate_content(prompt)
        ai_suggestions = response.text
        
        return {
            "status": "success",
            "sheet_url": sheet_url,
            "data_preview": mock_sheets_data,
            "ai_suggestions": ai_suggestions,
            "rows_found": len(mock_sheets_data["values"]) - 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Sheets import failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai-imports"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
