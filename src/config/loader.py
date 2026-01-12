"""Configuration loader for YAML/JSON files"""

import json
import yaml
from pathlib import Path
from typing import Union
from .schema import DomainConfig


def load_config(config_path: Union[str, Path]) -> DomainConfig:
    """
    Load and validate configuration from YAML or JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Validated DomainConfig instance
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    # Load file based on extension
    with open(config_path, "r", encoding="utf-8") as f:
        if config_path.suffix.lower() in [".yaml", ".yml"]:
            config_data = yaml.safe_load(f)
        elif config_path.suffix.lower() == ".json":
            config_data = json.load(f)
        else:
            raise ValueError(
                f"Unsupported config file format: {config_path.suffix}. "
                "Use .yaml, .yml, or .json"
            )
    
    # Validate and return
    return DomainConfig(**config_data)

