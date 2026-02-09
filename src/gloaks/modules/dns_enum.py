import asyncio
import aiodns
import structlog
from typing import Any, Dict, List
from gloaks.modules.base import ReconModule

logger = structlog.get_logger()

class DnsEnumModule(ReconModule):
    @property
    def name(self) -> str:
        return "dns_enumeration"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Enumerates DNS records (A, AAAA, MX, NS, TXT)."

    async def run(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform DNS enumeration."""
        resolver = aiodns.DNSResolver(loop=asyncio.get_running_loop())
        record_types = ["A", "AAAA", "MX", "NS", "TXT"]
        results = {}
        
        logger.info("Starting DNS enumeration", target=target)
        
        async def query(record_type: str):
            try:
                res = await resolver.query(target, record_type)
                # Parse results based on type
                parsed = []
                if record_type in ["A", "AAAA"]:
                    parsed = [r.host for r in res]
                elif record_type == "MX":
                    parsed = [{"host": r.host, "priority": r.priority} for r in res]
                elif record_type == "NS":
                    parsed = [r.host for r in res]
                elif record_type == "TXT":
                    parsed = [r.text.decode('utf-8') if isinstance(r.text, bytes) else r.text for r in res]
                
                results[record_type] = parsed
            except aiodns.error.DNSError:
                # Record not found or error
                results[record_type] = []
            except Exception as e:
                logger.debug(f"DNS query error for {record_type}: {e}")
                results[record_type] = []

        await asyncio.gather(*[query(rt) for rt in record_types])
        
        return results
