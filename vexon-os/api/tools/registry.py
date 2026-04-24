import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)

_registry: Dict[str, Dict[str, Any]] = {}

def register_tool(name: str, description: str, parameters: Dict[str, Any]):
    def decorator(func: Callable):
        _registry[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "func": func
        }
        return func
    return decorator

def get_tool(name: str):
    return _registry.get(name)

def list_tools():
    return [
        {
            "name": info["name"],
            "description": info["description"],
            "parameters": info["parameters"]
        }
        for info in _registry.values()
    ]
