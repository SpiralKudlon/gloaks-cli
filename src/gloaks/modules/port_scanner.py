import asyncio
import socket
import structlog
from typing import Any, Dict, List
from gloaks.modules.base import ReconModule

logger = structlog.get_logger()

class PortScanModule(ReconModule):
    @property
    def name(self) -> str:
        return "port_scan"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Scans for open TCP ports using asyncio."

    async def run(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute concurrent port scan."""
        ports = config.get("default_ports", [80, 443])
        timeout = config.get("timeout", 1.0)
        concurrency = config.get("concurrency", 100)
        
        logger.info(f"Starting port scan on {len(ports)} ports", target=target, concurrency=concurrency)
        
        semaphore = asyncio.Semaphore(concurrency)
        open_ports = []
        
        async def scan_port(port: int):
            async with semaphore:
                try:
                    conn = asyncio.open_connection(target, port)
                    reader, writer = await asyncio.wait_for(conn, timeout=timeout)
                    
                    # If we get here, the port is open
                    logger.debug(f"Port open: {port}")
                    open_ports.append({
                        "port": port,
                        "state": "open",
                        "protocol": "tcp"
                    })
                    
                    writer.close()
                    await writer.wait_closed()
                except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
                     # Port is closed or filtered
                     pass
                except Exception as e:
                    logger.debug(f"Error scanning port {port}: {e}")

        # Create tasks
        tasks = [scan_port(port) for port in ports]
        await asyncio.gather(*tasks)
        
        # Sort results by port number
        open_ports.sort(key=lambda x: x["port"])
        
        return {"open_ports": open_ports, "scanned_count": len(ports)}
