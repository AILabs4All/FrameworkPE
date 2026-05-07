from .base_prompt import BasePromptPlugin
from .config import htp_config.HtpConfig as HtpConfig
from typing import Dict, Any, List, Optional
import pandas as pd

class HypothesisTestingPlugin(BasePromptPlugin):
    def __init__(self, config: HtpConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config

    def execute(self,
                prompt: str,
                data_row: pd.Series,
                columns: List[str],
                **kwargs) -> List[Dict[str, Any]]:
        # Parâmetros: preferência do kwargs, senão do config
        max_iter = int(kwargs.get("max_iter", self.config.max_iteracao))
        limite_qualidade = float(kwargs.get("limite_qualidade", self.config.limite_qualidade))
        key_words = self.config.key_words
        prompt_template = self.config.prompt_text

        incident = self.build_input_text(data_row, columns)
        # Itera sobre todas as categorias definidas, exceto 'UNKNOWN'
        categories = [cat for cat in key_words.keys() if cat.upper() != "UNKNOWN"]

        results = []
        i = 0
        while i < len(categories) and i < max_iter:
            category = categories[i]
            keywords = key_words[category]  # já é uma lista
            keywords_str = ', '.join(keywords)

            # Preenche o template com os dados dinâmicos
            prompt_llm = prompt_template.format(
                input_framework=prompt,
                category=category,
                keywords_str=keywords_str
            )

            incident_id = kwargs.get('incident_id')
            hipoteses = self.model_plugin.send_prompt(prompt_llm, mode="htp", incident_id=incident_id)
            incident_info = self.extract_security_incidents(hipoteses)
            result_cat = incident_info['Category']

            rouge_score = self.calculate_rouge_score(result_cat, category)
            if rouge_score >= limite_qualidade:
                results.append({
                    "id": incident_id,
                    "informacoes_das_colunas": incident,
                    "categoria": result_cat,
                    "explicacao": incident_info['Explanation'],
                    "categoria_testada": category,
                    "rouge": rouge_score,
                    "iteracao": i + 1
                })
                return results

            i += 1

        # Nenhuma categoria confirmada
        results.append({
            "id": incident_id,
            "informacoes_das_colunas": incident,
            "categoria": "UNKNOWN",
            "explicacao": "Nenhuma categoria foi confirmada através do teste de hipóteses",
            "categoria_testada": "ALL",
            "rouge": 0.0,
            "iteracao": max_iter
        })
        return results

    def get_name(self) -> str:
        return self.config.acronimo  # ou self.config.name

    def get_description(self) -> str:
        return self.config.description