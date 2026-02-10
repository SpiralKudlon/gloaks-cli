import yaml
import re
import socket
import asyncio
from typing import List, Optional, Dict
import structlog
from urllib.parse import urlparse
import sys

logger = structlog.get_logger()

class ScopeValidator:
    def __init__(self, scope_file: Optional[str] = None):
        self.scope_file = scope_file
        self.allowed_domains = []
        self.allowed_ips = []
        self.excluded_domains = []
        
        if scope_file:
            self._load_scope()

    def _load_scope(self):
        """Load scope definition from YAML file."""
        try:
            with open(self.scope_file, 'r') as f:
                data = yaml.safe_load(f)
                
            self.allowed_domains = data.get('allow', {}).get('domains', [])
            self.allowed_ips = data.get('allow', {}).get('ips', [])
            self.excluded_domains = data.get('exclude', {}).get('domains', [])
            
            logger.info("Scope loaded", 
                        allowed_domains=len(self.allowed_domains), 
                        allowed_ips=len(self.allowed_ips))
        except (yaml.YAMLError, OSError) as e:
            logger.error("Failed to load scope file", error=str(e))
            # raise # Don't raise in constructor for tests if file invalid, but in real app handle better

    async def _resolve_ip(self, target: str) -> Optional[str]:
        """Resolve IP asynchronously to avoid blocking."""
        try:
            # Use asyncio's getaddrinfo which runs in a thread pool (safe for async)
            # or use aiodns if available. For simplicity and stdlib reliance:
            loop = asyncio.get_running_loop()
            info = await loop.getaddrinfo(target, None, family=socket.AF_INET)
            return info[0][4][0] if info else None
        except socket.gaierror:
            return None
        except Exception as e:
            logger.warning("DNS resolution failed in scope validator", target=target, error=str(e))
            return None

    async def is_target_allowed(self, target: str) -> bool:
        """Check if a target is authorized for scanning."""
        if not self.scope_file:
            return True
            
        # Resolve target to IP if possible
        target_ip = await self._resolve_ip(target)

        # Check Exclusions first
        if target in self.excluded_domains:
            logger.warning("Target explicitly excluded", target=target)
            return False

        # Check Allow List
        if target in self.allowed_domains:
            return True
        
        if target_ip and target_ip in self.allowed_ips:
            return True

        # Wildcard matching for domains
        for domain in self.allowed_domains:
            if domain.startswith("*."):
                suffix = domain[2:]
                # Strict wildcard: must be a subdomain (ending with .suffix)
                if target.endswith("." + suffix):
                    return True

        logger.warning("Target not in authorized scope", target=target)
        return False
