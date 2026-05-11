from .base_prompt import BasePromptPlugin
from .config.prompt_config import ProgressiveHintConfig
from typing import Dict, Any, List, Optional
import pandas as pd


class ProgressiveHintPlugin(BasePromptPlugin):
    """Progressive Hint Prompting — refina a resposta com dicas progressivas."""

    def __init__(self, config: ProgressiveHintConfig, model_plugin, task_config: Optional[dict] = None):
        super().__init__(model_plugin, task_config)
        self.config = config

    def execute(self, prompt: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        max_hints = int(kwargs.get("max_hints", self.config.max_hints))
        threshold = float(kwargs.get("quality_threshold", self.config.quality_threshold))
        hint_template = self.config.hint_template or self.config.templates.get("hint_template", "")
        output_format = self.config.output_format or ""
        incident_text = self.build_input_text(data_row, columns)
        incident_id = kwargs.get("incident_id")

        initial_prompt = self.config.prompt_text.format(
            input_framework=prompt,
            output_format=output_format
        )
        response = self.model_plugin.send_prompt(initial_prompt, mode="php", incident_id=incident_id)
        extracted = self.extract_answer(response)
        previous_category = extracted.get("category", "Unknown")

        if max_hints == 0:
            return [{
                "id": incident_id,
                "informacoes_das_colunas": incident_text,
                "categoria": previous_category,
                "explicacao": extracted.get("explanation", "Unknown"),
                "rouge": 0.0,
                "iteracao": 0
            }]

        for i in range(max_hints):
            hint_context = {
                "previous_category": previous_category,
                "input_framework": prompt,
                "output_format": output_format
            }
            hint_prompt = hint_template.format(**hint_context) if hint_template else initial_prompt
            response = self.model_plugin.send_prompt(hint_prompt, mode="php", incident_id=incident_id)
            extracted = self.extract_answer(response)
            current_category = extracted.get("category", "Unknown")
            score = self.calculate_rouge_score(previous_category, current_category)

            if (i + 1) == max_hints or score >= threshold:
                return [{
                    "id": incident_id,
                    "informacoes_das_colunas": incident_text,
                    "categoria": current_category,
                    "explicacao": extracted.get("explanation", "Unknown"),
                    "rouge": score,
                    "iteracao": i + 1
                }]
            previous_category = current_category

        return [{
            "id": incident_id,
            "informacoes_das_colunas": incident_text,
            "categoria": previous_category,
            "explicacao": "Limite de hints atingido sem convergência",
            "rouge": 0.0,
            "iteracao": max_hints
        }]

    def get_name(self) -> str:
        return self.config.acronym

    def get_description(self) -> str:
        return self.config.description
