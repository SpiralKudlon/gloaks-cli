from abc import ABC, abstractmethod
from typing import Any, Dict
import structlog

logger = structlog.get_logger()

class ReconModule(ABC):
    """Base class for all reconnaissance modules."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Module name (e.g., 'port_scanner')."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Module version."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Brief description of what the module does."""
        pass

    @abstractmethod
    async def run(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute reconnaissance and return results.
        
        Args:
            target: The target domain or IP address.
            config: Module-specific configuration dictionary.
            
        Returns:
            A dictionary containing the results.
        """
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate module-specific configuration. 
        Override this if specific validation is needed.
        """
        return True
