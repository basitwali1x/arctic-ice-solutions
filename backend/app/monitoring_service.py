import ssl
import socket
import requests
from datetime import datetime, timedelta
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class MonitoringService:
    def __init__(self):
        self.domains_to_monitor = [
            "yourchoiceice.com",
            "www.yourchoiceice.com"
        ]
    
    def check_ssl_certificate(self, domain: str, port: int = 443) -> Dict:
        """Check SSL certificate expiry for domain"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
            expiry_str = cert['notAfter']
            expiry_date = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
            days_remaining = (expiry_date - datetime.utcnow()).days
            
            status = "healthy"
            if days_remaining < 7:
                status = "critical"
            elif days_remaining < 30:
                status = "warning"
            
            return {
                "domain": domain,
                "status": status,
                "days_remaining": days_remaining,
                "expiry_date": expiry_date.isoformat(),
                "issuer": cert.get('issuer', [{}])[0].get('organizationName', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"SSL check failed for {domain}: {e}")
            return {
                "domain": domain,
                "status": "error",
                "error": str(e)
            }
    
    def check_domain_health(self, domain: str) -> Dict:
        """Check if domain is accessible"""
        try:
            response = requests.get(f"https://{domain}", timeout=10)
            return {
                "domain": domain,
                "status": "healthy" if response.status_code == 200 else "warning",
                "response_code": response.status_code,
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                "domain": domain,
                "status": "error",
                "error": str(e)
            }
    
    def get_monitoring_summary(self) -> Dict:
        """Get overall monitoring summary"""
        ssl_results = []
        health_results = []
        
        for domain in self.domains_to_monitor:
            ssl_results.append(self.check_ssl_certificate(domain))
            health_results.append(self.check_domain_health(domain))
        
        return {
            "ssl_certificates": ssl_results,
            "domain_health": health_results,
            "last_check": datetime.utcnow().isoformat()
        }

monitoring_service = MonitoringService()
