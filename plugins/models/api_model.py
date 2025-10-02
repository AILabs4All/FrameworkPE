"""Implementação de modelo via API usando LiteLLM."""

from __future__ import annotations

import os
from typing import Any, Dict

import litellm

from .base_model import BaseModel


class APIModel(BaseModel):
    """Modelo para provedores acessados via API (OpenAI, Hugging Face, etc)."""

    PROVIDER_ENV_MAP = {
        "openai": "OPENAI_API_KEY",
        "azure_openai": "AZURE_OPENAI_API_KEY",
        "huggingface": "HUGGINGFACE_API_KEY",
        "cohere": "COHERE_API_KEY",
    }

    PROVIDER_BASE_ENV_MAP = {
        "openai": "OPENAI_BASE_URL",
        "azure_openai": "AZURE_OPENAI_BASE_URL",
    }

    PROVIDER_PREFIX = {
        "huggingface": "huggingface/",
    }

    def setup_model(self) -> None:
        self.api_key = self._resolve_secret(self.config.get("api_key"))
        self.api_base = self.config.get("base_url") or self.config.get("api_base")
        self.deployment = self.config.get("deployment")
        self.extra_params: Dict[str, Any] = self.config.get("extra_params", {})

        env_key = self.PROVIDER_ENV_MAP.get(self.provider)
        if env_key and self.api_key:
            os.environ.setdefault(env_key, self.api_key)

        env_base = self.PROVIDER_BASE_ENV_MAP.get(self.provider)
        if env_base and self.api_base:
            os.environ.setdefault(env_base, self.api_base)

        self.logger.info(
            "Modelo API configurado: provider=%s, model=%s",
            self.provider,
            self.model_name,
        )

    def send_prompt(self, prompt: str, **kwargs: Any) -> str:
        mode = kwargs.get("mode", "default")

        try:
            self._apply_rate_limit(kwargs.get("rate_limit"))
            input_tokens = self.count_tokens(prompt)

            model_identifier = self._get_model_identifier()
            messages = kwargs.get(
                "messages",
                [{"role": "user", "content": prompt}],
            )

            completion_kwargs: Dict[str, Any] = {
                "model": model_identifier,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            }

            if self.api_key:
                completion_kwargs["api_key"] = self.api_key
            if self.api_base:
                completion_kwargs["api_base"] = self.api_base
            if self.deployment:
                completion_kwargs["deployment_id"] = self.deployment

            completion_kwargs.update(self.extra_params)
            completion_kwargs.update(
                {k: v for k, v in kwargs.items() if k not in completion_kwargs and k != "mode"}
            )

            response = litellm.completion(**completion_kwargs)
            content = self._extract_content(response)
            output_tokens = self.count_tokens(content)
            self._log_interaction(prompt, content, input_tokens, output_tokens, mode, kwargs.get('incident_id'))
            return content
        except Exception as exc:
            self.logger.error("Falha ao chamar modelo API: %s", exc)
            return f"Erro ao chamar modelo API: {exc}"

    def _extract_content(self, response: Any) -> str:
        try:
            message = response.choices[0].message
            if isinstance(message, dict):
                return message.get("content", "") or ""
            return getattr(message, "content", "") or ""
        except Exception:
            return getattr(response, "content", "") or ""

    def _get_model_identifier(self) -> str:
        prefix = self.PROVIDER_PREFIX.get(self.provider, "")
        return f"{prefix}{self.model_name}" if prefix else self.model_name

    @staticmethod
    def _resolve_secret(value: Any) -> Any:
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var)
        return value
