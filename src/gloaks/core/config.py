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

from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource, YamlConfigSettingsSource
from typing import Type, Tuple, Dict, Any

class GloaksConfig(BaseSettings):
    block_out_of_scope: bool = True
    log: LogConfig = Field(default_factory=LogConfig)
    geolocation: GeolocationConfig = Field(default_factory=GeolocationConfig)
    port_scan: PortScanConfig = Field(default_factory=PortScanConfig)
    scope_file: Optional[str] = None

    model_config = SettingsConfigDict(
        env_prefix="GLOAKS_",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        # Return sources: Init (args) > Env > YAML (Custom) > Defaults
        return (
            init_settings,
            env_settings,
            YamlConfigSettingsSource(settings_cls),
            dotenv_settings,
            file_secret_settings,
        )

class YamlConfigSettingsSource(PydanticBaseSettingsSource):
    """
    A simple settings source that loads from a YAML file.
    It looks for 'config_path' in init kwargs or defaults to standard locations.
    """
    def get_field_value(
        self, field: Any, field_name: str
    ) -> Tuple[Any, str, bool]:
        # This method is required by abstract base class but we can implement __call__ directly
        # or use helper methods. Pydantic V2 sources are a bit complex to implement fully correct 
        # for nested models without 'pydantic-settings' extras which might check 'yaml'.
        # But 'pydantic-settings' package doesn't include YamlSource by default unless 'pydantic-settings[yaml]' is installed?
        # Check imports: 'from pydantic_settings import ...' 
        # Actually our project has PyYAML and pydantic-settings. 
        # Let's Implement a simpler custom source that reads our specific file locations.
        pass

    def __call__(self) -> Dict[str, Any]:
        # Logic from original load_config to find the file
        config_path = None
        # We don't easily have access to 'config_path' arg passed to load_config here 
        # unless we stash it globally or pass it in init_settings?
        # A simpler way for this codebase without over-engineering Pydantic sources:
        # Just update load_config to NOT pass dict as init kwargs, but instead set it as a default?
        # Or better:
        # 1. Load YAML to dict.
        # 2. Instantiate Config, letting Pydantic read Env Vars.
        # 3. BUT Pydantic Env vars only populate fields if they are missing? 
        # No, Env overrides defaults.
        # If we pass YAML as init kwargs, it overrides Env.
        
        # So we want: Env > YAML > Defaults.
        # Use Pydantic to read Env.
        # Use YAML to provide "Defaults" that override code defaults?
        
        # We can implement a Custom Source that reads the YAML file.
        # We need to find the YAML file path.
        
        paths_to_check = [
            # We can't easily get the dynamic 'config_path' argument here without context.
            "config/default.yaml",
            os.path.expanduser("~/.gloaks/config.yaml"),
            "/etc/gloaks/config.yaml"
        ]
        
        file_data = {}
        for path in paths_to_check:
             if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        data = yaml.safe_load(f)
                        if data:
                            file_data.update(data)
                    break
                except Exception:
                    pass
        return file_data

def load_config(config_path: Optional[str] = None) -> GloaksConfig:
    """Load configuration with precedence: Env > Config File > Defaults."""
    
    # 1. Load YAML data first to act as "Defaults from file"
    yaml_db = {}
    
    paths_to_check = []
    if config_path:
        paths_to_check.append(config_path)
    paths_to_check.extend([
        "config/default.yaml",
        os.path.expanduser("~/.gloaks/config.yaml"),
        "/etc/gloaks/config.yaml"
    ])
    
    for path in paths_to_check:
        if path and os.path.exists(path):
            try:
                with open(path, "r") as f:
                    file_data = yaml.safe_load(f)
                    if file_data:
                        yaml_db.update(file_data)
                break
            except (yaml.YAMLError, OSError) as e:
                print(f"Warning: Failed to load config from {path}: {e}")

    # 2. Instantiate Config.
    # To make Env > YAML, we cannot pass YAML as init kwargs directly if we want Env to win?
    # Actually, BaseSettings priorities: Init > Env > ...
    
    # Workaround:
    # Create config from Env (defaults).
    # Then merge? No, that's messy.
    
    # Proper way: Pass YAML data as a fallback?
    # Or rely on the fact that we can construct the object with YAML data, 
    # AND tell Pydantic to overlay Env vars on top.
    
    # There isn't a simple flag "EnvOverridesInit".
    
    # Solution: Custom Settings Source is the way, but dynamically passing the path is hard.
    # Hybrid approach:
    # Load YAML.
    # Instantiate Config with YAML data AND _env_settings handles the rest?
    # No.
    
    # Let's use the 'pydantic_settings.PydanticBaseSettingsSource' approch 
    # but strictly for the CLI tool.
    
    # Let's just manually update the yaml_db with env vars if they exist, 
    # mimicking Pydantic's behavior, before passing to init?
    # That's re-implementing Pydantic.
    
    # Let's use the `_secrets` argument or similar? No.
    
    # Let's go with the Custom Source but inject the path via a class var or global (ugly but works)
    # OR helper function.
    
    return GloaksConfig.from_yaml(config_path)


# Redefining GloaksConfig to use a simplified factory method pattern
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

    @classmethod
    def from_yaml(cls, config_path: Optional[str] = None) -> "GloaksConfig":
        # 1. Load YAML
        yaml_data = {}
        paths = []
        if config_path: paths.append(config_path)
        paths.extend(["config/default.yaml", os.path.expanduser("~/.gloaks/config.yaml"), "/etc/gloaks/config.yaml"])
        
        for p in paths:
            if p and os.path.exists(p):
                try:
                    with open(p, "r") as f:
                        d = yaml.safe_load(f)
                        if d: yaml_data.update(d)
                    break
                except Exception: pass
        
        # 2. To allow Env > YAML, we can't pass YAML as **kwargs.
        # But we can use a custom source that returns this yaml_data.
        
        # Dynamic subclassing to inject source?
        
        class ConfigWithYaml(cls):
            @classmethod
            def settings_customise_sources(
                cls,
                settings_cls,
                init_settings,
                env_settings,
                dotenv_settings,
                file_secret_settings,
            ):
                return (
                    init_settings,
                    env_settings, 
                    lambda: yaml_data, # Source that returns our loaded yaml
                    file_secret_settings,
                )
        
        return ConfigWithYaml()

def load_config(config_path: Optional[str] = None) -> GloaksConfig:
    return GloaksConfig.from_yaml(config_path)
