from pathlib import Path
from typing import Any

import yaml

from app.config.settings import Settings


def load_yaml_config(config_path: str = "config/config.yaml") -> dict[str, Any]:
    """Loads configuration from a YAML file."""
    path = Path(config_path)
    if not path.is_absolute():
        # Resolve relative to the project root (assuming we run from project root)
        path = Path.cwd() / path

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_settings(config_path: str = "config/config.yaml") -> Settings:
    """Loads YAML config and instantiates the Pydantic Settings model."""
    yaml_data = load_yaml_config(config_path)
    return Settings(**yaml_data)
