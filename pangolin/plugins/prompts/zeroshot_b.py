from .base_prompt import BasePromptPlugin
from .config.prompt_config import ZeroShotConfig
from typing import Dict, Any, List, Optional
import pandas as pd


class ZeroShotPlugin(BasePromptPlugin):
    """Zero-Shot Prompting — classificação direta sem exemplos, dirigida pelo schema."""

    def __init__(self, config: ZeroShotConfig, model_plugin, task_config: Optional[dict] = None):
        super().__init__(model_plugin, task_config)
        self.config = config

    def execute(self, prompt: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        incident_text = self.build_input_text(data_row, columns)
        incident_id = kwargs.get("incident_id")

        categories_info = "\n".join([
            f"- {cat.get('code', '')}: {cat.get('name', '')} - {cat.get('description', '')}"
            for cat in self.config.categories
        ])
        context = {
            "system_prompt": self.config.system_prompt,
            "categories_info": categories_info,
            "input_framework": incident_text,
            "output_format": self.config.output_format or "",
        }
        full_prompt = self.config.prompt_text.format(**context)

        response = self.model_plugin.send_prompt(full_prompt, mode="zeroshot", incident_id=incident_id)
        extracted = self.extract_answer(response)

        return [{
            "id": incident_id,
            "informacoes_das_colunas": incident_text,
            "categoria": extracted.get("category", "Unknown"),
            "explicacao": extracted.get("explanation", "Unknown"),
            "rouge": 0.0,
            "iteracao": 1,
        }]

    def get_name(self) -> str:
        return self.config.acronym

    def get_description(self) -> str:
        return self.config.description
