from .base_prompt import BasePromptPlugin
from .config.prompt_config import ProgressiveRectificationConfig
from typing import Dict, Any, List, Optional
import pandas as pd


class ProgressiveRectificationPlugin(BasePromptPlugin):
    """Progressive Rectification Prompting — valida e retifica via mascaramento de palavras-chave."""

    def __init__(self, config: ProgressiveRectificationConfig, model_plugin, task_config: Optional[dict] = None):
        super().__init__(model_plugin, task_config)
        self.config = config

    def execute(self, prompt: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        max_iter = int(kwargs.get("max_iter", self.config.max_iter))
        threshold = float(kwargs.get("quality_threshold", self.config.quality_threshold))
        masking_template = (
            self.config.masking_template
            or self.config.templates.get("masking_template", "")
        )
        rectification_template = (
            self.config.rectification_template
            or self.config.templates.get("rectification_template", "")
        )
        output_format = self.config.output_format or ""
        incident_text = self.build_input_text(data_row, columns)
        incident_id = kwargs.get("incident_id")

        initial_prompt = self.config.prompt_text.format(
            input_framework=prompt,
            output_format=output_format
        )
        response = self.model_plugin.send_prompt(initial_prompt, mode="prp", incident_id=incident_id)
        initial = self.extract_answer(response)
        current_category = initial.get("category", "Unknown")
        rejected: List[str] = []

        for attempt in range(max_iter):
            subcategories = self.config.key_words.get(current_category.upper(), [])
            for subcategory in subcategories:
                masked_prompt = masking_template.format(
                    subcategory=subcategory,
                    input_framework=prompt
                )
                self.model_plugin.send_prompt(masked_prompt, mode="prp", incident_id=incident_id)

                rect_prompt = rectification_template.format(
                    input_framework=prompt,
                    rejected_category=", ".join(rejected + [current_category]),
                    output_format=output_format
                )
                response = self.model_plugin.send_prompt(rect_prompt, mode="prp", incident_id=incident_id)
                extracted = self.extract_answer(response)
                new_category = extracted.get("category", "Unknown")
                score = self.calculate_rouge_score(current_category, new_category)

                if score >= threshold:
                    return [{
                        "id": incident_id,
                        "informacoes_das_colunas": incident_text,
                        "categoria": new_category,
                        "explicacao": extracted.get("explanation", initial.get("explanation", "Unknown")),
                        "qualidade": score,
                        "iteracao": attempt + 1
                    }]
                rejected.append(current_category)
                current_category = new_category

        return [{
            "id": incident_id,
            "informacoes_das_colunas": incident_text,
            "categoria": current_category,
            "explicacao": initial.get("explanation", "Unknown"),
            "qualidade": 0.0,
            "iteracao": max_iter
        }]

    def get_name(self) -> str:
        return self.config.acronym

    def get_description(self) -> str:
        return self.config.description
