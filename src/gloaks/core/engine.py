import asyncio
import structlog
from typing import List, Dict, Any, Type, Optional
from gloaks.core.config import GloaksConfig
from gloaks.modules.base import ReconModule
from gloaks.modules.geolocation import GeolocationModule
from gloaks.modules.port_scanner import PortScanModule
from gloaks.modules.http_analysis import HttpAnalysisModule
from gloaks.modules.dns_enum import DnsEnumModule

logger = structlog.get_logger()

class GloaksEngine:
    def __init__(self, config: GloaksConfig, http_client: Optional[Any] = None):
        self.config = config
        self.http_client = http_client
        self.results = {}
        self.modules: List[ReconModule] = [
            GeolocationModule(),
            PortScanModule(),
            HttpAnalysisModule(http_client=http_client),
            DnsEnumModule()
        ]

    async def run(self, target: str, cancellation_token: Optional[asyncio.Event] = None) -> Dict[str, Any]:
        """Run all registered modules against the target."""
        logger.info("Starting comprehensive scan", target=target)
        
        results = {
            "target": target,
            "modules": {}
        }
        
        async def run_module_wrapper(module: ReconModule):
            if cancellation_token and cancellation_token.is_set():
                logger.info("Scan cancelled before module start", module=module.name)
                return module.name, {"status": "cancelled"}
                
            try:
                # Extract module-specific config
                module_config = {}
                if module.name == "geolocation":
                    module_config = self.config.geolocation.model_dump()
                elif module.name == "port_scan":
                    module_config = self.config.port_scan.model_dump()
                
                # Check cancellation again before running potentially long task
                if cancellation_token and cancellation_token.is_set():
                     return module.name, {"status": "cancelled"}

                # Run the module
                # Ideally, modules should also accept cancellation_token, 
                # but for now we rely on them checking it or wrapper handling it
                # or just standard task cancellation if we cancel the gather.
                # But here we are using a token cooperatively.
                
                # To support TRUE cancellation, we might need to wrap in a task and cancel it 
                # if the event is set, but here we just check before.
                
                data = await module.run(target, module_config)
                return module.name, data
            except asyncio.CancelledError:
                logger.info("Module cancelled", module=module.name)
                return module.name, {"status": "cancelled"}
            except Exception as e:
                logger.exception("Module failed", module=module.name)
                return module.name, {"error": str(e)}

        # Run all modules concurrently
        # We wrap in shield to allow us to handle cancellation manually if needed, 
        # or just standard gather.
        
        tasks = [run_module_wrapper(m) for m in self.modules]
        
        # If using a token, we might want to wait for either tasks or token?
        # But for now, the token is passed in.
        
        try:
            if cancellation_token:
                # If we want to abort *immediately* on token set, we need to monitor it.
                # But for this iteration, we check at start of wrappers. 
                # To be more responsive, we'd need to modify modules.
                pass
                
            module_results = await asyncio.gather(*tasks)
            
            for name, data in module_results:
                results["modules"][name] = data

            logger.info("Scan completed", target=target)
            return results
        except asyncio.CancelledError:
            logger.info("Scan execution cancelled")
            raise
