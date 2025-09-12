from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
import re

class RowError(BaseModel):
    sheet: str
    row_index: int
    column: Optional[str] = None
    error_code: str
    message: str
    value: Optional[Any] = None

class FileIssue(BaseModel):
    filename: str
    errors: List[RowError] = []

class SalesRow(BaseModel):
    Type: str
    Date: datetime
    Name: str
    Item: str
    Qty: int
    Sales_Price: float
    Amount: float
    Num: Optional[str] = None

    @validator('Type')
    def type_allowed(cls, v):
        allowed = {'Invoice', 'Sales Receipt'}
        if v not in allowed:
            raise ValueError(f"Type must be one of {allowed}")
        return v

    @validator('Qty', pre=True)
    def coerce_qty(cls, v):
        try:
            return int(float(v))
        except Exception:
            raise ValueError("Qty must be an integer")

    @validator('Sales_Price', 'Amount', pre=True)
    def coerce_money(cls, v):
        try:
            return float(v)
        except Exception:
            raise ValueError("Must be numeric")

class CustomerRow(BaseModel):
    Customer: str
    Address: Optional[str] = ""
    Main_Phone: Optional[str] = None

    @validator('Customer')
    def non_empty_customer(cls, v):
        if not v or str(v).strip() == "":
            raise ValueError("Customer name is required")
        return str(v).strip()

class ImportSummary(BaseModel):
    total_rows: int
    success_rows: int
    error_rows: int
    duplicates_skipped: int
    file_hash: str
    errors: List[RowError] = []
