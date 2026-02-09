import asyncio
import structlog
from typing import List, Dict, Any, Type
from gloaks.core.config import GloaksConfig
from gloaks.modules.base import ReconModule
from gloaks.modules.geolocation import GeolocationModule
from gloaks.modules.port_scanner import PortScanModule
from gloaks.modules.http_analysis import HttpAnalysisModule
from gloaks.modules.dns_enum import DnsEnumModule

logger = structlog.get_logger()

class GloaksEngine:
    def __init__(self, config: GloaksConfig):
        self.config = config
        self.results = {}
        self.modules: List[ReconModule] = [
            GeolocationModule(),
            PortScanModule(),
            HttpAnalysisModule(),
            DnsEnumModule()
        ]

    async def run(self, target: str) -> Dict[str, Any]:
        """Run all registered modules against the target."""
        logger.info("Starting comprehensive scan", target=target)
        
        results = {
            "target": target,
            "modules": {}
        }
        
        async def run_module_wrapper(module: ReconModule):
            try:
                # Extract module-specific config
                # e.g., config.geolocation for GeolocationModule
                # For now simplify by passing related config section if exists, else empty
                module_config = {}
                if module.name == "geolocation":
                    module_config = self.config.geolocation.model_dump()
                elif module.name == "port_scan":
                    module_config = self.config.port_scan.model_dump()
                
                # Run the module
                data = await module.run(target, module_config)
                return module.name, data
            except Exception as e:
                logger.error(f"Module {module.name} failed", error=str(e))
                return module.name, {"error": str(e)}

        # Run all modules concurrently
        tasks = [run_module_wrapper(m) for m in self.modules]
        module_results = await asyncio.gather(*tasks)
        
        for name, data in module_results:
            results["modules"][name] = data

        logger.info("Scan completed", target=target)
        return results
