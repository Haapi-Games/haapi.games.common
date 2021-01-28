"""Haapi Games Common."""
import os
import typing
from collections import ChainMap
from typing import Any
from typing import Dict


def get_config(configs: Dict[str, Dict[Any, Any]]) -> typing.ChainMap[Any, Any]:
    """Convenience function for merging different configs.

    Merges together based on os.environ, env variable, and default config.
    os.environ takes preference, the environment variable config, then defaults

    Args:
        configs: A that will be used to merge based on the ENVIRONMENT

    Returns:
        ChainMap: ChainMap of os.environ, environment config, default config
    """
    env_var = os.environ.get("ENVIRONMENT")
    environment = env_var.upper() if env_var is not None else ""
    environment_config: Dict[Any, Any] = (
        configs[environment] if configs.get(environment) is not None else {}
    )
    return ChainMap(os.environ, environment_config, configs["DEFAULT"])
