from .base_prompt import BasePromptPlugin
from .config.prompt_config import HtpConfig
from typing import Dict, Any, List, Optional
import pandas as pd


class HypothesisTestingPlugin(BasePromptPlugin):
    """Testa hipóteses para cada categoria definida no schema."""

    def __init__(self, config: HtpConfig, model_plugin, task_config: Optional[dict] = None):
        super().__init__(model_plugin, task_config)
        self.config = config

    def execute(self,
                prompt: str,
                data_row: pd.Series,
                columns: List[str],
                **kwargs) -> List[Dict[str, Any]]:
        max_iter = int(kwargs.get("max_iter", self.config.max_iter))
        threshold = float(kwargs.get("quality_threshold", self.config.quality_threshold))
        key_words = self.config.key_words
        prompt_template = self.config.prompt_text
        output_format = self.config.output_format or ""

        incident_text = self.build_input_text(data_row, columns)
        incident_id = kwargs.get("incident_id")
        categories = [cat for cat in key_words.keys() if cat.upper() != "UNKNOWN"]

        results = []
        for i, category in enumerate(categories):
            if i >= max_iter:
                break

            keywords_str = ", ".join(key_words[category])
            prompt_llm = prompt_template.format(
                input_framework=prompt,
                category=category,
                keywords_str=keywords_str,
                output_format=output_format
            )

            response = self.model_plugin.send_prompt(prompt_llm, mode="htp", incident_id=incident_id)
            extracted = self.extract_answer(response)
            result_cat = extracted.get("category", "UNKNOWN")

            score = self.calculate_rouge_score(result_cat, category)
            if score >= threshold:
                results.append({
                    "id": incident_id,
                    "informacoes_das_colunas": incident_text,
                    "categoria": result_cat,
                    "explicacao": extracted.get("explanation", ""),
                    "categoria_testada": category,
                    "rouge": score,
                    "iteracao": i + 1
                })
                return results

        results.append({
            "id": incident_id,
            "informacoes_das_colunas": incident_text,
            "categoria": "UNKNOWN",
            "explicacao": "Nenhuma categoria foi confirmada através do teste de hipóteses",
            "categoria_testada": "ALL",
            "rouge": 0.0,
            "iteracao": max_iter
        })
        return results

    def get_name(self) -> str:
        return self.config.acronym

    def get_description(self) -> str:
        return self.config.description
