import re
import socket
import ipaddress
from typing import Optional, Tuple

class InputValidator:
    # Regex for standard domain names (per RFC 1035/1123)
    DOMAIN_REGEX = re.compile(
        r'^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$'
    )

    @staticmethod
    def is_valid_ip(target: str) -> bool:
        """Check if target is a valid IPv4 or IPv6 address."""
        try:
            ipaddress.ip_address(target)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_domain(target: str) -> bool:
        """Check if target is a valid domain name."""
        if not target:
            return False
        if len(target) > 253:
            return False
        return bool(InputValidator.DOMAIN_REGEX.match(target))

    @staticmethod
    def validate_target(target: str) -> Tuple[bool, Optional[str]]:
        """Validate target is either a valid IP or Domain.
        
        Returns:
            Tuple(is_valid, error_message)
        """
        if InputValidator.is_valid_ip(target):
            return True, None
        
        if InputValidator.is_valid_domain(target):
            return True, None
            
        return False, f"Invalid target format: '{target}'. Must be a valid domain or IP address."
