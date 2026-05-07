"""Plugin para Zero-Shot Prompting - Técnica de prompt direto sem exemplos."""

from .base_prompt import BasePromptPlugin
from typing import Dict, Any, List
import pandas as pd


class ZeroShotPlugin(BasePromptPlugin):
    """
    Plugin para Zero-Shot Prompting.
    
    Esta técnica envia prompts diretamente ao modelo sem exemplos (zero-shot),
    apenas com a definição das categorias NIST e instruções claras.
    """
    
    def __init__(self, model_plugin, **params):
        """
        Inicializa o plugin ZeroShot.
        
        Args:
            model_plugin: Plugin do modelo a ser usado
            **params: Parâmetros de configuração (atualmente não utilizado)
        """
        super().__init__(model_plugin)
        # params não utilizado nesta implementação, mas mantido para compatibilidade
        _ = params
        
    def get_name(self) -> str:
        """Retorna o nome da técnica de prompt."""
        return "zeroshot"
    
    def execute(self, prompt: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Implementa Zero-Shot Prompting.
        
        Args:
            prompt: Prompt base (ignorado, usa prompt próprio)
            data_row: Linha de dados do incidente
            columns: Colunas a serem incluídas
            **kwargs: Parâmetros adicionais
                
        Returns:
            Lista com as respostas do modelo
        """
        incident = self.build_input_text(data_row, columns)
        incident_id = kwargs.get('incident_id')
        
        # Constrói o prompt zero-shot completo
        full_prompt = self._build_prompt(incident)
        
        # Configurações de envio
        send_kwargs = {
            "mode": "zeroshot",
            "incident_id": incident_id
        }
        
        # Envia o prompt
        response = self.model_plugin.send_prompt(full_prompt, **send_kwargs)
        
        # Processa a resposta
        processed_response = self.extract_answer(response)
        
        return [{
            "Response": response,
            "Processed": processed_response,
            "Category": processed_response.get("category", "Unknown"),
            "Explanation": processed_response.get("explanation", "Unknown")
        }]
    
    def _build_prompt(self, incident: str) -> str:
        system_prompt = self.task.get("system_prompt", "You are an expert.")
        categories = "
".join([f"- {cat}" for cat in self.task.get("categories", ["CAT1", "CAT2"])])
        output_format = self.task.get("output_format", "Provide Category and Explanation")
        
        prompt = f"{system_prompt}

### Categories
{categories}

---Input:
{incident}

---Output format:
{output_format}"
        return prompt.strip()