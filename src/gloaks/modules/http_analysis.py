import httpx
from typing import Any, Dict, List, Optional
import structlog
from gloaks.modules.base import ReconModule

logger = structlog.get_logger()

class HttpAnalysisModule(ReconModule):
    def __init__(self, http_client: Optional[httpx.AsyncClient] = None):
        self.http_client = http_client

    @property
    def name(self) -> str:
        return "http_analysis"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Analyzes HTTP headers and checks for common security misconfigurations."

    async def run(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform HTTP header analysis."""
        timeout = config.get("timeout", 5.0)
        follow_redirects = config.get("follow_redirects", True)
        
        # Determine scheme - try HTTPS first
        url = f"https://{target}"
        
        logger.info("Starting HTTP analysis", target=target)
        
        try:
            # MITM Vulnerability Fix: verify=True to ensure SSL certificate validation
            # Use shared client if available, usually created in app/cli context
            client_context = None
            client = self.http_client
            
            if not client:
                 client = httpx.AsyncClient(verify=True, follow_redirects=follow_redirects)
                 client_context = client
            
            try:
                # If using shared client, we might need to adjust verify/redirects per request? 
                # Httpx client is immutable for some configs. 
                # We can't change verify on existing client easily per request if it differs using high level API?
                # Actually Client(verify=True) is default.
                # If shared client has different settings, we might need to respect them or create new one.
                # For this optimization, assuming shared client has secure defaults.
                
                try:
                    response = await client.get(url, timeout=timeout)
                except (httpx.ConnectError, httpx.TimeoutException):
                    # Fallback to HTTP
                    logger.info("HTTPS failed, falling back to HTTP", target=target)
                    url = f"http://{target}"
                    response = await client.get(url, timeout=timeout)

                headers = response.headers
                
                # Check for security headers
                security_headers = {
                    "Strict-Transport-Security": "strict_transport_security",
                    "Content-Security-Policy": "content_security_policy",
                    "X-Frame-Options": "x_frame_options",
                    "X-Content-Type-Options": "x_content_type_options",
                    "Referrer-Policy": "referrer_policy"
                }
                
                header_results = {}
                missing_headers = []
                
                for header_name, key in security_headers.items():
                    if header_name in headers:
                        header_results[key] = True
                    else:
                        header_results[key] = False
                        missing_headers.append(header_name)
            finally:
                if client_context:
                    await client_context.aclose()
                
            # Server technology detection
            technologies = []
            if "Server" in headers:
                technologies.append(f"Server: {headers['Server']}")
            if "X-Powered-By" in headers:
                technologies.append(f"Powered-By: {headers['X-Powered-By']}")

            return {
                "status_code": response.status_code,
                "url": str(response.url),
                "headers": dict(headers),
                "security_headers": header_results,
                "missing_headers": missing_headers,
                "technologies": technologies
            }

        except httpx.RequestError as exc:
            logger.error("HTTP analysis failed", error=str(exc))
            return {"error": str(exc)}
