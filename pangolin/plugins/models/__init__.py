"""Plugins para acesso a provedores de modelos."""

from .api_model import APIModel
from .local_model import LocalModel
from .openrouter_model import OpenRouterModel

__all__ = ["APIModel", "LocalModel", "OpenRouterModel"]
