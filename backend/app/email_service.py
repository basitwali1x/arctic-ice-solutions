import os
import logging
from typing import Dict, List, Optional, Any
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@arcticeicesolutions.com")
        self.client = None
        
        if self.api_key:
            self.client = SendGridAPIClient(api_key=self.api_key)
        else:
            logger.warning("SendGrid API key not configured. Email functionality will be disabled.")
    
    def is_configured(self) -> bool:
        return self.client is not None
    
    async def send_invoice_email(
        self,
        customer_email: str,
        customer_name: str,
        invoice_data: Dict[str, Any],
        signature_data: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.is_configured():
            logger.error("Email service not configured")
            return {"success": False, "error": "Email service not configured"}
        
        try:
            subject = f"Invoice #{invoice_data.get('invoice_number', 'N/A')} - Arctic Ice Solutions"
            
            html_content = self._generate_invoice_html(customer_name, invoice_data, signature_data)
            
            message = Mail(
                from_email=self.from_email,
                to_emails=customer_email,
                subject=subject,
                html_content=html_content
            )
            
            if signature_data:
                signature_attachment = Attachment(
                    FileContent(signature_data.split(',')[1]),
                    FileName("delivery_signature.png"),
                    FileType("image/png"),
                    Disposition("attachment")
                )
                message.attachment = signature_attachment
            
            response = self.client.send(message)
            
            logger.info(f"Invoice email sent successfully to {customer_email}")
            return {
                "success": True,
                "message": "Invoice email sent successfully",
                "status_code": response.status_code
            }
            
        except Exception as e:
            logger.error(f"Failed to send invoice email: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_invoice_html(
        self,
        customer_name: str,
        invoice_data: Dict[str, Any],
        signature_data: Optional[str] = None
    ) -> str:
        signature_html = ""
        if signature_data:
            signature_html = f"""
            <div style="margin-top: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
                <h3 style="color: #2c5aa0; margin-bottom: 10px;">Delivery Confirmation</h3>
                <p><strong>Customer Signature:</strong></p>
                <img src="{signature_data}" alt="Customer Signature" style="max-width: 300px; border: 1px solid #ccc; padding: 5px;">
                <p style="font-size: 12px; color: #666; margin-top: 10px;">
                    Signature captured on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                </p>
            </div>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Invoice - Arctic Ice Solutions</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #2c5aa0; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .invoice-details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ background-color: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f8f9fa; }}
                .total {{ font-weight: bold; font-size: 18px; color: #2c5aa0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Arctic Ice Solutions</h1>
                <p>Premium Ice Delivery Services</p>
            </div>
            
            <div class="content">
                <h2>Invoice #{invoice_data.get('invoice_number', 'N/A')}</h2>
                
                <div class="invoice-details">
                    <p><strong>Bill To:</strong> {customer_name}</p>
                    <p><strong>Invoice Date:</strong> {invoice_data.get('date', datetime.now().strftime('%B %d, %Y'))}</p>
                    <p><strong>Delivery Date:</strong> {invoice_data.get('delivery_date', 'N/A')}</p>
                    <p><strong>Route:</strong> {invoice_data.get('route_number', 'N/A')}</p>
                    <p><strong>Driver:</strong> {invoice_data.get('driver_name', 'N/A')}</p>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th>Quantity</th>
                            <th>Unit Price</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Ice Bags Delivered</td>
                            <td>{invoice_data.get('quantity', 1)}</td>
                            <td>${invoice_data.get('unit_price', 0):.2f}</td>
                            <td>${invoice_data.get('total_amount', 0):.2f}</td>
                        </tr>
                    </tbody>
                </table>
                
                <div style="text-align: right; margin-top: 20px;">
                    <p class="total">Total Amount: ${invoice_data.get('total_amount', 0):.2f}</p>
                    <p><strong>Payment Method:</strong> {invoice_data.get('payment_method', 'N/A').upper()}</p>
                </div>
                
                {signature_html}
                
                <div style="margin-top: 30px; padding: 15px; background-color: #e8f4fd; border-radius: 5px;">
                    <h3 style="color: #2c5aa0; margin-bottom: 10px;">Thank You for Your Business!</h3>
                    <p>We appreciate your continued trust in Arctic Ice Solutions for your ice delivery needs.</p>
                    <p>For questions about this invoice, please contact us at:</p>
                    <p><strong>Phone:</strong> (555) 123-4567 | <strong>Email:</strong> support@arcticeicesolutions.com</p>
                </div>
            </div>
            
            <div class="footer">
                <p>&copy; 2025 Arctic Ice Solutions. All rights reserved.</p>
                <p>This is an automated invoice. Please retain for your records.</p>
            </div>
        </body>
        </html>
        """

email_service = EmailService()
