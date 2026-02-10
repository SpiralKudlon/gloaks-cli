import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml

class LogConfig(BaseSettings):
    level: str = "INFO"
    format: str = "json"
    file: Optional[str] = None

class GeolocationConfig(BaseSettings):
    provider: str = "ip-api"
    timeout: float = 5.0
    api_key: Optional[str] = None

class PortScanConfig(BaseSettings):
    default_ports: List[int] = [21, 22, 80, 443, 8080]
    timeout: float = 1.0
    concurrency: int = 50

class GloaksConfig(BaseSettings):
    block_out_of_scope: bool = True
    log: LogConfig = Field(default_factory=LogConfig)
    geolocation: GeolocationConfig = Field(default_factory=GeolocationConfig)
    port_scan: PortScanConfig = Field(default_factory=PortScanConfig)
    scope_file: Optional[str] = None

    model_config = SettingsConfigDict(
        env_prefix="GLOAKS_",
        env_nested_delimiter="__",
        case_sensitive=False
    )

def load_config(config_path: Optional[str] = None) -> GloaksConfig:
    """Load configuration from a YAML file and environment variables."""
    # Start with defaults
    config_data = {}
    
    # Load from file if provided or default exists
    paths_to_check = [
        config_path,
        "config/default.yaml",
        os.path.expanduser("~/.gloaks/config.yaml"),
        "/etc/gloaks/config.yaml"
    ]
    
    for path in paths_to_check:
        if path and os.path.exists(path):
            try:
                with open(path, "r") as f:
                    file_data = yaml.safe_load(f)
                    if file_data:
                        # Deep merge logic would go here, for now simple override
                        config_data.update(file_data)
                break # Stop at first valid config file found for now
            except (yaml.YAMLError, OSError) as e:
                print(f"Warning: Failed to load config from {path}: {e}")

    # Pydantic Settings will handle env var overrides automatically 
    # capturing the file data as initial values is tricky with BaseSettings
    # unless we use a custom source. For simplicity in Phase 1, we instantiated
    # with data from file, and let env vars override if we mapped them manually,
    # but BaseSettings does env vars primarily.
    
    # A cleaner approach with pydantic-settings is to use the settings_customise_sources
    # hook, but for now we will instantiate the config object directly from merged data
    # and rely on Pydantic to validate. 
    # Note: This doesn't pull from ENV vars automatically if passing dict.
    # To support BOTH, we'd normally rely on Pydantic's automatic env loading.
    
    return GloaksConfig(**config_data)
