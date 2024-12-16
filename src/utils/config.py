import yaml
from pathlib import Path
from typing import Any, Dict


class Config:
    """Configuration management for the agent."""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.settings: Dict[str, Any] = {}
        self.load_configs()

    def load_configs(self):
        """Load all configuration files from the config directory."""
        for config_file in self.config_dir.glob("*.yaml"):
            with open(config_file, "r") as f:
                self.settings[config_file.stem] = yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation."""
        keys = key.split(".")
        value = self.settings

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def set(self, key: str, value: Any):
        """Set a configuration value using dot notation."""
        keys = key.split(".")
        target = self.settings

        for k in keys[:-1]:
            target = target.setdefault(k, {})

        target[keys[-1]] = value

    def save(self):
        """Save current configuration to files."""
        for config_name, config_data in self.settings.items():
            config_path = self.config_dir / f"{config_name}.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)
