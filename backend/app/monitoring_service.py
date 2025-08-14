from datetime import datetime
import socket
import ssl
from typing import Dict, Any

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
                issuer_info = cert.get('issuer', [{}])[0] if isinstance(cert.get('issuer'), list) else {}
                result["issuer"] = str(issuer_info.get('organizationName', 'Unknown'))

    except Exception as e:
        result["error"] = f"SSL check failed: {str(e)}"

    return result
