from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd
import re
import json
from utils.logger import setup_logger

class BasePromptPlugin(ABC):
    """Classe base para todos os plugins de técnicas de prompt."""
    
    def __init__(self, model_plugin):
        self.model_plugin = model_plugin
        self.logger = setup_logger(self.__class__.__name__)
    
    @abstractmethod
    def execute(self, prompt: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Executa a técnica de prompt específica."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Retorna o nome da técnica de prompt."""
        pass
    
    def build_incident_info(self, row: pd.Series, columns: List[str]) -> str:
        """Constrói string com informações do incidente."""
        return " / ".join([
            f"{coluna}: {row[coluna]}" if coluna in row and pd.notnull(row[coluna]) 
            else f"{coluna}: [valor ausente]" 
            for coluna in columns
        ])
    
    def extract_security_incidents(self, texto: str) -> Dict[str, str]:
        """Extrai categoria e explicação do texto usando regex."""

        
        # Verifica se é JSON válido
        try:
            dados = json.loads(texto)
            if "Category" in dados and "Explanation" in dados:
                return {
                    "Category": dados["Category"].strip(),
                    "Explanation": dados["Explanation"].strip()
                }
        except json.JSONDecodeError:
            pass
        
        # Caso não seja JSON, usa regex
        padrao = r"(?:\*\*Category:\*\*|Category:)\s*(.*?)\s*(?:\*\*Explanation:\*\*|Explanation:|Explanation:)\s*(.*?)(?=\n|$)"
        matches = re.findall(padrao, texto, re.DOTALL)
        
        if matches:
            ultima_ocorrencia = matches[-1]
            return {
                "Category": self._extract_cat(ultima_ocorrencia[0].replace("*", "").replace("\n", "").strip()),
                "Explanation": ultima_ocorrencia[1].replace("*", "").replace("\n", "").strip()
            }
        else:
            return {"Category": "unknown", "Explanation": "unknown"}
    
    def _extract_cat(self, texto: str) -> str:
        """Extrai código CAT (CAT1 a CAT12) do texto."""
        
        match = re.search(r'\bCAT([1-9]|1[0-2])\b', texto.upper())
        if match:
            return f"CAT{match.group(1)}"
        return texto
    
    def calculate_rouge_score(self, resposta_anterior: str, nova_resposta: str) -> float:
        """Calcula o ROUGE Score entre duas respostas."""
        try:
            from rouge_score import rouge_scorer
            scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
            scores = scorer.score(resposta_anterior, nova_resposta)
            return scores['rougeL'].fmeasure
        except ImportError:
            self.logger.warning("Rouge Score não disponível. Usando comparação simples.")
            return 1.0 if resposta_anterior.lower() == nova_resposta.lower() else 0.0