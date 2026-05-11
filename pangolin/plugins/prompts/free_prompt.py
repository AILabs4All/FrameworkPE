from .base_prompt import BasePromptPlugin
from .config.prompt_config import FreePromptConfig
from typing import Dict, Any, List, Optional
import pandas as pd


class FreePromptPlugin(BasePromptPlugin):
    """Free Prompting — técnica flexível com exemplos e formatação configuráveis via schema."""

    def __init__(self, config: FreePromptConfig, model_plugin, task_config: Optional[dict] = None):
        super().__init__(model_plugin, task_config)
        self.config = config

    def execute(self, prompt: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        incident_text = self.build_input_text(data_row, columns)
        incident_id = kwargs.get("incident_id")

        context = {
            "system_prompt": self.config.system_prompt,
            "categories_info": self._build_categories_text(),
            "examples_section": self._build_examples_text(),
            "context_hints": self._build_context_hints(incident_text),
            "input_framework": incident_text,
            "output_format": self.config.output_format or "",
        }
        full_prompt = self.config.prompt_text.format(**context)

        send_kwargs: Dict[str, Any] = {"mode": "free_prompt", "incident_id": incident_id}
        if self.config.temperature_override is not None:
            send_kwargs["temperature"] = self.config.temperature_override

        response = self.model_plugin.send_prompt(full_prompt, **send_kwargs)
        extracted = self.extract_answer(response)

        return [{
            "id": incident_id,
            "informacoes_das_colunas": incident_text,
            "categoria": extracted.get("category", "Unknown"),
            "explicacao": extracted.get("explanation", "Unknown"),
            "rouge": 0.0,
            "iteracao": 1,
        }]

    def _build_categories_text(self) -> str:
        return "\n".join([
            f"- {cat.get('code', '')}: {cat.get('name', '')} - {cat.get('description', '')}"
            for cat in self.config.categories
        ])

    def _build_examples_text(self) -> str:
        if not self.config.examples or not self.config.use_examples:
            return ""
        return "\n\n".join([
            f"Example:\nIncident: {ex.get('incident')}\n"
            f"Category: {ex.get('category')}\nExplanation: {ex.get('explanation')}"
            for ex in self.config.examples
        ])

    def _build_context_hints(self, incident_text: str) -> str:
        if not self.config.use_context_hints:
            return ""
        hints_config = self.config.context_hints
        if not hints_config:
            return ""
        lower = incident_text.lower()
        hints = [
            item["hint"]
            for item in hints_config
            if any(w.lower() in lower for w in item.get("keywords", []))
        ]
        return "ANALYSIS HINTS:\n" + "\n".join(hints) if hints else ""

    def get_name(self) -> str:
        return self.config.acronym

    def get_description(self) -> str:
        return self.config.description
