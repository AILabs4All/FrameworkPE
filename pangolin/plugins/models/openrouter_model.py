"""Plugin de modelo para OpenRouter via LiteLLM."""

from __future__ import annotations

from typing import Any, Dict

from .api_model import APIModel


DEFAULT_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterModel(APIModel):
    """Acessa modelos do OpenRouter com chave e endpoint próprios.

    O campo ``name`` deve conter o identificador do modelo no OpenRouter,
    incluindo o prefixo da organização quando aplicável, por exemplo
    ``openai/gpt-5.2``.
    """

    def __init__(self, config: Dict[str, Any]):
        normalized_config = dict(config)
        normalized_config["provider"] = "openrouter"
        if not normalized_config.get("base_url") and not normalized_config.get("api_base"):
            normalized_config["base_url"] = DEFAULT_OPENROUTER_BASE_URL

        extra_params = dict(normalized_config.get("extra_params", {}))
        headers = dict(extra_params.get("extra_headers", {}))

        site_url = normalized_config.pop("site_url", None)
        app_name = normalized_config.pop("app_name", None)
        headers.update(normalized_config.pop("extra_headers", {}))

        if site_url:
            headers.setdefault("HTTP-Referer", site_url)
        if app_name:
            headers.setdefault("X-OpenRouter-Title", app_name)
        if headers:
            extra_params["extra_headers"] = headers

        normalized_config["extra_params"] = extra_params
        super().__init__(normalized_config)
