from .base_prompt import BasePromptPlugin
from .config.prompt_config import SelfHintConfig
from typing import Dict, Any, List, Optional
import pandas as pd


class SelfHintPlugin(BasePromptPlugin):
    """Self Hint Prompting — o modelo cria um plano e se auto-refina iterativamente."""

    def __init__(self, config: SelfHintConfig, model_plugin, task_config: Optional[dict] = None):
        super().__init__(model_plugin, task_config)
        self.config = config

    def execute(self, prompt: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        max_iter = int(kwargs.get("max_iter", self.config.max_iter))
        threshold = float(kwargs.get("quality_threshold", self.config.quality_threshold))
        plan_instructions = (
            self.config.plan_instructions
            or self.config.templates.get("plan_instructions", "")
        )
        output_format = self.config.output_format or ""
        incident_text = self.build_input_text(data_row, columns)
        incident_id = kwargs.get("incident_id")

        initial_prompt = self.config.prompt_text.format(
            input_framework=prompt,
            plan_instructions=plan_instructions,
            output_format=output_format
        )
        # Primeira passagem: geração do plano (resultado descartado intencionalmente)
        self.model_plugin.send_prompt(initial_prompt, mode="shp", incident_id=incident_id)
        response = self.model_plugin.send_prompt(initial_prompt, mode="shp", incident_id=incident_id)
        previous_category = self.extract_answer(response).get("category", "Unknown")

        for i in range(max_iter):
            refinement_prompt = self.config.prompt_text.format(
                input_framework=prompt,
                plan_instructions=plan_instructions,
                previous_category=previous_category,
                output_format=output_format
            )
            response = self.model_plugin.send_prompt(refinement_prompt, mode="shp", incident_id=incident_id)
            extracted = self.extract_answer(response)
            category = extracted.get("category", "Unknown")
            score = self.calculate_rouge_score(previous_category, category)

            if (i + 1) == max_iter or score >= threshold:
                return [{
                    "id": incident_id,
                    "informacoes_das_colunas": incident_text,
                    "categoria": category,
                    "explicacao": extracted.get("explanation", "Unknown"),
                    "rouge": score,
                    "iteracao": i + 1
                }]
            previous_category = category

        return [{
            "id": incident_id,
            "informacoes_das_colunas": incident_text,
            "categoria": previous_category,
            "explicacao": "Limite de iterações atingido sem convergência",
            "rouge": 0.0,
            "iteracao": max_iter
        }]

    def get_name(self) -> str:
        return self.config.acronym

    def get_description(self) -> str:
        return self.config.description
