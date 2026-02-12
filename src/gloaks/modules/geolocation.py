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
        
        if not self.api_key:
             logger.warning("No API key configured for Geolocation module. Results may be limited and HTTP will be used for the free tier.")

        # API endpoint (Enforce HTTPS for paid tier, fallback to HTTP for free tier)
        # The free API (ip-api.com) only supports HTTP.
        # The paid API (pro.ip-api.com) requires HTTPS and an API key.
        url = f"https://pro.ip-api.com/json/{target}?key={self.api_key}" if self.api_key else f"http://ip-api.com/json/{target}"
        
        logger.info("Starting geolocation scan", target=target, provider=provider, url=url)
        
        try:
            # Use shared client if available, otherwise context managed fallback
            if self.http_client:
                response = await self.http_client.get(url, timeout=timeout)
                response.raise_for_status()
                data = response.json()
                return self._parse_response(data)
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=timeout)
                    response.raise_for_status()
                    data = response.json()
                    return self._parse_response(data)
                
        except httpx.RequestError as exc:
            logger.error("Geolocation request failed", error=str(exc))
            return {"error": str(exc)}

    def _parse_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
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
            
