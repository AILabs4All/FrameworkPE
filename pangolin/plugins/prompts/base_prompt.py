from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd
import re
import json
from utils.logger import setup_logger



class BasePromptPlugin(ABC):
    """Classe base para todos os plugins de técnicas de prompt."""
    
    def __init__(self, model_plugin, task_config: dict = None):
        self.model_plugin = model_plugin
        self.task = task_config or {}
        self.logger = setup_logger(self.__class__.__name__)
    
    @abstractmethod
    def execute(self, prompt: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Executa a técnica de prompt específica."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Retorna o nome da técnica de prompt."""
        pass
    
    def build_input_text(self, row: pd.Series, columns: List[str] = None) -> str:
        """Constrói string de entrada baseada no input_builder configurado."""
        input_template = self.task.get("input_builder", "")
        if input_template:
            # Substitui os placeholders usando os valores da linha
            format_dict = {col: str(row.get(col, "[ausente]")) for col in row.index}
            try:
                return input_template.format(**format_dict)
            except KeyError as e:
                self.logger.warning(f"Placeholder {e} do input_builder não encontrado nos dados.")
                return input_template

        # Fallback genérico caso não tenha template
        cols_to_use = columns if columns else row.index
        return " / ".join([
            f"{col}: {row[col]}" if pd.notnull(row[col]) else f"{col}: [ausente]"
            for col in cols_to_use
        ])
    
    def extract_answer(self, texto: str) -> Dict[str, str]:
        """Extrai a resposta utilizando a configuração de extração (json ou regex)."""
        extraction = self.task.get("extraction", {})
        method = extraction.get("method", "json")
        
        unknown_cat = self.task.get("unknown_category", "UNKNOWN")

        if method == "json":
            try:
                # Remove espaços limpos e blocos de markdown de json (ex: ```json)
                cleaned = texto.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                
                dados = json.loads(cleaned)
                return {
                    "category": str(dados.get("category", unknown_cat)).strip(),
                    "explanation": str(dados.get("explanation", "unknown")).strip()
                }
            except json.JSONDecodeError:
                pass
        
        # Fallback ou método template_regex
        cat_group = extraction.get("category_group", "category")
        exp_group = extraction.get("explanation_group", "explanation")
        
        # Regex baseada na expectativa de pares Chave: Valor
        padrao = r"(?:\*\*Category:\*\*|Category:)\s*(.*?)\s*(?:\*\*Explanation:\*\*|Explanation:)\s*(.*?)(?=\n|$)"
        if "regex_pattern" in extraction:
             padrao = extraction["regex_pattern"]

        matches = re.findall(padrao, texto, re.DOTALL | re.IGNORECASE)
        
        if matches:
            ultima = matches[-1]
            return {
                "category": ultima[0].replace("*", "").strip(),
                "explanation": ultima[1].replace("*", "").strip()
            }
        
        return {"category": unknown_cat, "explanation": "unknown"}

def _clean_category(texto: str) -> str:
    texto = texto.replace("*", "").replace("\n", "").strip()
    return texto
