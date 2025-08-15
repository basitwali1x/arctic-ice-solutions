from datetime import datetime
import socket
import ssl
from typing import Dict, Any, List
from fastapi import APIRouter

class MonitoringService:
    def __init__(self):
        self.domains_to_monitor = [
            "yourchoiceice.com",
            "api.yourchoiceice.com",
            "arcticicesolutions.com"
        ]
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get overall system health status"""
        ssl_results = []
        for domain in self.domains_to_monitor:
            ssl_results.append(self.check_ssl_certificate(domain))
        
        healthy_domains = sum(1 for result in ssl_results if result["status"] == "healthy")
        
        return {
            "overall_status": "healthy" if healthy_domains == len(self.domains_to_monitor) else "warning",
            "domains_monitored": len(self.domains_to_monitor),
            "healthy_domains": healthy_domains,
            "ssl_certificates": ssl_results,
            "last_check": datetime.utcnow().isoformat()
        }
    
    def check_ssl_certificate(self, domain: str) -> Dict[str, Any]:
        """Check SSL certificate for a domain"""
        return check_ssl_expiry(domain)

router = APIRouter()
monitoring_service = MonitoringService()

def check_ssl_expiry(domain: str, port: int = 443) -> Dict[str, Any]:
    """Check SSL certificate expiry with proper type safety"""
    context = ssl.create_default_context()
    result = {
        "domain": domain,
        "status": "error",
        "days_remaining": None,
        "expiry_date": None,
        "issuer": "Unknown"
    }

    try:
        with socket.create_connection((domain, port)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                if not cert:
                    raise ValueError("No certificate returned")
                
                # Safe expiry date extraction
                if 'notAfter' in cert:
                    expiry_date = datetime.strptime(
                        str(cert['notAfter']), 
                        '%b %d %H:%M:%S %Y %Z'
                    )
                    result.update({
                        "status": "healthy",
                        "days_remaining": (expiry_date - datetime.utcnow()).days,
                        "expiry_date": expiry_date.isoformat()
                    })

                # Safe issuer extraction
                issuer_data = cert.get('issuer', [])
                if isinstance(issuer_data, list) and len(issuer_data) > 0:
                    issuer_info = issuer_data[0]
                    if isinstance(issuer_info, dict):
                        result["issuer"] = str(issuer_info.get('organizationName', 'Unknown'))
                    else:
                        result["issuer"] = "Unknown"
                else:
                    result["issuer"] = "Unknown"

    except Exception as e:
        result["error"] = f"SSL check failed: {str(e)}"

    return result

@router.get("/ssl-check/{domain}")
async def check_ssl_status(domain: str):
    """Check SSL certificate status for a domain"""
    return check_ssl_expiry(domain)
