"""
SoverGrid Config Parser & Validator
Reads and validates the sovergrid.yaml configuration file.

This is Project 1: The Local Config Validator.
If a required field is missing or malformed, throw a clean,
professional error message instead of a Python traceback.
"""

import os
import sys
from pathlib import Path
from typing import Any

from sovergrid.logger import get_logger

log = get_logger(__name__)

# Default config filename
CONFIG_FILENAME = "sovergrid.yaml"

# Required fields and their expected types
# Format: (dot-separated path, human-readable name, expected type)
REQUIRED_FIELDS = [
    ("app.name", "Application Name", str),
    ("compute.provider", "Compute Provider", str),
    ("compute.resources.cpu", "CPU Cores", int),
    ("compute.resources.memory", "Memory Allocation", str),
    ("build.port", "Application Port", int),
]

# Allowed values for specific fields
ALLOWED_VALUES = {
    "compute.provider": ["akash", "spheron", "golem"],
    "storage.provider": ["filecoin", "arweave", "ipfs"],
    "payment.token": ["USDC", "SVR"],
}


class ConfigError(Exception):
    """Raised when the sovergrid.yaml file is invalid."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Config Error [{field}]: {message}")


class SoverGridConfig:
    """
    Parses and validates a sovergrid.yaml configuration file.

    Usage:
        config = SoverGridConfig.load()
        print(config.app_name)
        print(config.compute_provider)
    """

    def __init__(self, raw_data: dict):
        self._raw = raw_data
        self._validate()

        # Expose clean attributes after validation
        self.app_name: str = self._get("app.name")
        self.app_description: str = self._get("app.description", "No description")
        self.compute_provider: str = self._get("compute.provider")
        self.compute_region: str = self._get("compute.region", "auto")
        self.cpu: int = self._get("compute.resources.cpu")
        self.memory: str = self._get("compute.resources.memory")
        self.storage_size: str = self._get("compute.resources.storage", "512Mi")
        self.storage_provider: str = self._get("storage.provider", "filecoin")
        self.dockerfile: str = self._get("build.dockerfile", "Dockerfile")
        self.port: int = self._get("build.port")
        self.payment_token: str = self._get("payment.token", "USDC")
        self.max_budget: float = self._get("payment.max_budget", 5.00)

    def _get(self, dotpath: str, default: Any = None) -> Any:
        """
        Safely retrieves a nested value from the config dictionary
        using dot notation (e.g., 'compute.resources.cpu').
        """
        keys = dotpath.split(".")
        current = self._raw

        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]

        return current

    def _validate(self):
        """
        Validates all required fields exist and have correct types.
        Raises ConfigError with a human-readable message on failure.
        """
        errors = []

        # Check required fields
        for dotpath, human_name, expected_type in REQUIRED_FIELDS:
            value = self._get(dotpath)

            if value is None:
                errors.append(
                    f'  Missing required field: "{human_name}" ({dotpath})'
                )
                continue

            if not isinstance(value, expected_type):
                errors.append(
                    f'  Invalid type for "{human_name}" ({dotpath}): '
                    f"expected {expected_type.__name__}, got {type(value).__name__}"
                )

        # Check allowed values
        for dotpath, allowed in ALLOWED_VALUES.items():
            value = self._get(dotpath)
            if value is not None and value not in allowed:
                errors.append(
                    f'  Invalid value for {dotpath}: "{value}". '
                    f"Allowed: {', '.join(allowed)}"
                )

        if errors:
            error_block = "\n".join(errors)
            log.error(
                f"Found {len(errors)} problem(s) in your {CONFIG_FILENAME}:\n"
                f"{error_block}\n\n"
                f"  Fix these issues and try again.\n"
                f"  Run 'sovergrid init' to generate a valid config template."
            )
            sys.exit(1)

        log.info(f'Config validated: app "{self._get("app.name")}" is ready.')

    @classmethod
    def load(cls, path: str = None) -> "SoverGridConfig":
        """
        Loads and parses the sovergrid.yaml file from the given path
        or the current working directory.
        """
        # Import yaml here so we get a clean error if it's missing
        try:
            import yaml
        except ImportError:
            log.error(
                "PyYAML is not installed. Run: pip install pyyaml"
            )
            sys.exit(1)

        if path is None:
            path = os.path.join(os.getcwd(), CONFIG_FILENAME)

        config_path = Path(path)

        if not config_path.exists():
            log.error(
                f"No {CONFIG_FILENAME} found in {config_path.parent}\n\n"
                f"  Run 'sovergrid init' to create one, or make sure you are\n"
                f"  in the root directory of your project."
            )
            sys.exit(1)

        if not config_path.is_file():
            log.error(f"{CONFIG_FILENAME} exists but is not a file.")
            sys.exit(1)

        try:
            with open(config_path, "r") as f:
                raw_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            log.error(
                f"Failed to parse {CONFIG_FILENAME}. Check your YAML syntax.\n"
                f"  Error: {e}"
            )
            sys.exit(1)

        if not isinstance(raw_data, dict) or not raw_data:
            log.error(
                f"{CONFIG_FILENAME} is empty or not a valid YAML dictionary."
            )
            sys.exit(1)

        log.debug(f"Loaded config from {config_path}")
        return cls(raw_data)

    def summary(self) -> str:
        """Returns a human-readable summary of the deployment config."""
        return (
            f"\n"
            f"  App:      {self.app_name}\n"
            f"  Compute:  {self.compute_provider} ({self.compute_region})\n"
            f"  CPU:      {self.cpu} core(s)\n"
            f"  Memory:   {self.memory}\n"
            f"  Storage:  {self.storage_provider}\n"
            f"  Port:     {self.port}\n"
            f"  Budget:   ${self.max_budget:.2f}/mo ({self.payment_token})\n"
        )
