from typing import Any, Dict
import httpx
import structlog
from gloaks.modules.base import ReconModule

logger = structlog.get_logger()

class GeolocationModule(ReconModule):
    @property
    def name(self) -> str:
        return "geolocation"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Retrieves geolocation data for a target IP/Domain using ip-api.com."

    async def run(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch geolocation data asynchronously."""
        provider = config.get("provider", "ip-api")
        timeout = config.get("timeout", 5.0)
        
        # In a real implementation we would support multiple providers
        # For now, we stick to ip-api.com as per previous version
        url = f"http://ip-api.com/json/{target}"
        
        logger.info("Starting geolocation scan", target=target, provider=provider)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=timeout)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "fail":
                    logger.warning("Geolocation lookup failed", reason=data.get("message"))
                    return {"error": data.get("message")}
                
                return {
                    "country": data.get("country"),
                    "city": data.get("city"),
                    "isp": data.get("isp"),
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                    "ip": data.get("query")
                }
                
        except httpx.RequestError as exc:
            logger.error(f"Geolocation request failed: {exc}")
            return {"error": str(exc)}
            
