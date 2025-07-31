import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from requests_oauthlib import OAuth2Session
import logging

logger = logging.getLogger(__name__)

class QuickBooksClient:
    def __init__(self):
        self.client_id = os.getenv("QUICKBOOKS_CLIENT_ID")
        self.client_secret = os.getenv("QUICKBOOKS_CLIENT_SECRET")
        self.redirect_uri = os.getenv("QUICKBOOKS_REDIRECT_URI", "http://localhost:8000/api/quickbooks/callback")
        self.sandbox_base_url = os.getenv("QUICKBOOKS_SANDBOX_BASE_URL", "https://sandbox-quickbooks.api.intuit.com")
        self.discovery_document_url = "https://appcenter.intuit.com/api/v1/connection/oauth2"
        self.scope = ["com.intuit.quickbooks.accounting"]
        
    def get_authorization_url(self, state: str = None) -> tuple[str, str]:
        oauth = OAuth2Session(
            self.client_id,
            scope=self.scope,
            redirect_uri=self.redirect_uri,
            state=state
        )
        authorization_url, state = oauth.authorization_url(
            "https://appcenter.intuit.com/connect/oauth2",
            access_type="offline"
        )
        return authorization_url, state
    
    def exchange_code_for_tokens(self, authorization_response: str, state: str = None) -> Dict[str, Any]:
        oauth = OAuth2Session(
            self.client_id,
            redirect_uri=self.redirect_uri,
            state=state
        )
        
        token = oauth.fetch_token(
            "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",
            authorization_response=authorization_response,
            client_secret=self.client_secret
        )
        
        return token
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        oauth = OAuth2Session(self.client_id)
        token = oauth.refresh_token(
            "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",
            refresh_token=refresh_token,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        return token
    
    def make_api_request(self, endpoint: str, access_token: str, realm_id: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        url = f"{self.sandbox_base_url}/v3/company/{realm_id}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"QuickBooks API request failed: {e}")
            raise
    
    def get_customers(self, access_token: str, realm_id: str) -> List[Dict[str, Any]]:
        try:
            response = self.make_api_request("customers", access_token, realm_id)
            return response.get("QueryResponse", {}).get("Customer", [])
        except Exception as e:
            logger.error(f"Failed to fetch customers: {e}")
            return []
    
    def create_customer(self, access_token: str, realm_id: str, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            qb_customer = {
                "Name": customer_data["name"],
                "CompanyName": customer_data.get("company_name", customer_data["name"]),
                "BillAddr": {
                    "Line1": customer_data.get("address", ""),
                    "City": customer_data.get("city", ""),
                    "CountrySubDivisionCode": customer_data.get("state", ""),
                    "PostalCode": customer_data.get("zip_code", "")
                },
                "PrimaryPhone": {
                    "FreeFormNumber": customer_data.get("phone", "")
                },
                "PrimaryEmailAddr": {
                    "Address": customer_data.get("email", "")
                }
            }
            
            response = self.make_api_request("customer", access_token, realm_id, "POST", {"Customer": qb_customer})
            return response.get("Customer", {})
        except Exception as e:
            logger.error(f"Failed to create customer: {e}")
            raise
    
    def get_invoices(self, access_token: str, realm_id: str) -> List[Dict[str, Any]]:
        try:
            response = self.make_api_request("invoices", access_token, realm_id)
            return response.get("QueryResponse", {}).get("Invoice", [])
        except Exception as e:
            logger.error(f"Failed to fetch invoices: {e}")
            return []
    
    def create_invoice(self, access_token: str, realm_id: str, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            qb_invoice = {
                "CustomerRef": {
                    "value": invoice_data["customer_ref_id"]
                },
                "TxnDate": invoice_data.get("date", datetime.now().strftime("%Y-%m-%d")),
                "Line": [
                    {
                        "Amount": invoice_data["total_amount"],
                        "DetailType": "SalesItemLineDetail",
                        "SalesItemLineDetail": {
                            "ItemRef": {
                                "value": "1",
                                "name": "Services"
                            },
                            "Qty": invoice_data.get("quantity", 1),
                            "UnitPrice": invoice_data.get("unit_price", invoice_data["total_amount"])
                        }
                    }
                ]
            }
            
            response = self.make_api_request("invoice", access_token, realm_id, "POST", {"Invoice": qb_invoice})
            return response.get("Invoice", {})
        except Exception as e:
            logger.error(f"Failed to create invoice: {e}")
            raise
    
    def get_payments(self, access_token: str, realm_id: str) -> List[Dict[str, Any]]:
        try:
            response = self.make_api_request("payments", access_token, realm_id)
            return response.get("QueryResponse", {}).get("Payment", [])
        except Exception as e:
            logger.error(f"Failed to fetch payments: {e}")
            return []
    
    def create_payment(self, access_token: str, realm_id: str, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            qb_payment = {
                "CustomerRef": {
                    "value": payment_data["customer_ref_id"]
                },
                "TotalAmt": payment_data["amount"],
                "TxnDate": payment_data.get("date", datetime.now().strftime("%Y-%m-%d")),
                "Line": [
                    {
                        "Amount": payment_data["amount"],
                        "LinkedTxn": [
                            {
                                "TxnId": payment_data.get("invoice_id"),
                                "TxnType": "Invoice"
                            }
                        ]
                    }
                ]
            }
            
            response = self.make_api_request("payment", access_token, realm_id, "POST", {"Payment": qb_payment})
            return response.get("Payment", {})
        except Exception as e:
            logger.error(f"Failed to create payment: {e}")
            raise
    
    def get_company_info(self, access_token: str, realm_id: str) -> Dict[str, Any]:
        try:
            response = self.make_api_request("companyinfo/1", access_token, realm_id)
            return response.get("QueryResponse", {}).get("CompanyInfo", [{}])[0]
        except Exception as e:
            logger.error(f"Failed to fetch company info: {e}")
            return {}

def map_arctic_customer_to_qb(arctic_customer: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": arctic_customer.get("name", ""),
        "company_name": arctic_customer.get("name", ""),
        "address": arctic_customer.get("address", ""),
        "city": arctic_customer.get("city", ""),
        "state": arctic_customer.get("state", ""),
        "zip_code": arctic_customer.get("zip_code", ""),
        "phone": arctic_customer.get("phone", ""),
        "email": arctic_customer.get("email", "")
    }

def map_arctic_order_to_qb_invoice(arctic_order: Dict[str, Any], customer_ref_id: str) -> Dict[str, Any]:
    return {
        "customer_ref_id": customer_ref_id,
        "date": arctic_order.get("order_date", datetime.now().strftime("%Y-%m-%d")),
        "total_amount": arctic_order.get("total_amount", 0),
        "quantity": arctic_order.get("quantity", 1),
        "unit_price": arctic_order.get("unit_price", arctic_order.get("total_amount", 0))
    }

def map_arctic_payment_to_qb(arctic_payment: Dict[str, Any], customer_ref_id: str, invoice_id: str = None) -> Dict[str, Any]:
    return {
        "customer_ref_id": customer_ref_id,
        "amount": arctic_payment.get("amount", 0),
        "date": arctic_payment.get("payment_date", datetime.now().strftime("%Y-%m-%d")),
        "invoice_id": invoice_id
    }
