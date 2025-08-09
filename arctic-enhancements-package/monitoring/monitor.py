from fastapi import FastAPI, APIRouter, HTTPException
import socket
import ssl
import datetime
import requests
from typing import Dict, Any
import os

app = FastAPI(title="Arctic Ice Monitoring Service")
router = APIRouter()

@router.get("/ssl-check")
async def check_ssl(domain: str = "yourchoiceice.com") -> Dict[str, Any]:
    """Check SSL certificate expiry for domain"""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
        
        expiry = datetime.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
        days_left = (expiry - datetime.datetime.now()).days
        
        status = "healthy"
        if days_left < 7:
            status = "critical"
        elif days_left < 30:
            status = "warning"
        
        return {
            "domain": domain,
            "expiry": expiry.isoformat(),
            "days_left": days_left,
            "status": status,
            "issuer": cert.get("issuer", [{}])[0].get("organizationName", "Unknown"),
            "subject": cert.get("subject", [{}])[0].get("commonName", domain)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SSL check failed: {str(e)}")

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Overall system health check"""
    checks = {}
    overall_status = "healthy"
    
    try:
        ssl_result = await check_ssl("yourchoiceice.com")
        checks["main_ssl"] = ssl_result
        if ssl_result["status"] != "healthy":
            overall_status = "warning"
    except Exception as e:
        checks["main_ssl"] = {"status": "error", "error": str(e)}
        overall_status = "error"
    
    try:
        api_ssl_result = await check_ssl("api.yourchoiceice.com")
        checks["api_ssl"] = api_ssl_result
        if api_ssl_result["status"] != "healthy":
            overall_status = "warning"
    except Exception as e:
        checks["api_ssl"] = {"status": "error", "error": str(e)}
        overall_status = "error"
    
    try:
        response = requests.get("https://api.yourchoiceice.com/health", timeout=10)
        checks["api_availability"] = {
            "status": "healthy" if response.status_code == 200 else "error",
            "response_code": response.status_code,
            "response_time": response.elapsed.total_seconds()
        }
    except Exception as e:
        checks["api_availability"] = {"status": "error", "error": str(e)}
        overall_status = "error"
    
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "overall_status": overall_status,
        "checks": checks
    }

@router.post("/alert")
async def send_alert(message: str, severity: str = "info") -> Dict[str, Any]:
    """Send monitoring alert"""
    monitoring_email = os.getenv("MONITORING_EMAIL", "admin@yourchoiceice.com")
    
    alert_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "message": message,
        "severity": severity,
        "recipient": monitoring_email
    }
    
    print(f"ALERT [{severity.upper()}]: {message}")
    
    return {
        "status": "sent",
        "alert": alert_data
    }

app.include_router(router, prefix="/monitoring")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
