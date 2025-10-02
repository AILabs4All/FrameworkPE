from .base_prompt import BasePromptPlugin
from typing import Dict, Any, List
import pandas as pd

class ProgressiveHintPlugin(BasePromptPlugin):
    """Plugin para Progressive Hint Prompting."""
    
    def execute(self, prompt: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Implementa Progressive Hint Prompting.
        Gera dicas progressivas usando o próprio LLM com base na resposta anterior.
        """
        max_hints = kwargs.get("max_hints", 4)
        limite_rouge = kwargs.get("limite_rouge", 0.9)
        
        # Adiciona formatação de saída ao prompt
        output_format = """
        If classification is not possible, return:
        Category: Unknown
        Explanation: Unknown
        
        OUTPUT:
        Category: [NIST code]
        Explanation: [Justification for the chosen category]
        """
        
        full_prompt = f"{prompt} {output_format}"
        
        # Primeira resposta
        incident_id = kwargs.get('incident_id')
        resposta = self.model_plugin.send_prompt(full_prompt, mode="php", incident_id=incident_id)
        resposta_anterior = resposta
        
        resultados = []
        informacoes_das_colunas = self.build_incident_info(data_row, columns)
        
        # Se max_hints é 0, retorna apenas a primeira resposta
        if max_hints == 0:
            categoria_info = self.extract_security_incidents(resposta)
            resultados.append({
                "id": incident_id,
                "informacoes_das_colunas": informacoes_das_colunas,
                "categoria": categoria_info["Category"],
                "explicacao": categoria_info["Explanation"],
                "rouge": 0.0,
                "iteracao": 0
            })
            return resultados
        
        # Loop de hints progressivos
        for i in range(max_hints):
            # Gera dica baseada na resposta anterior
            categoria_anterior = self.extract_security_incidents(resposta_anterior)["Category"]
            dica = f"Hint: The category is near: {categoria_anterior}"
            
            # Novo prompt com dica
            hint_prompt = f"{dica} {full_prompt}"
            nova_resposta = self.model_plugin.send_prompt(hint_prompt, mode="php", incident_id=incident_id)
            
            # Calcula ROUGE Score
            categoria_atual = self.extract_security_incidents(nova_resposta)["Category"]
            rouge_score = self.calculate_rouge_score(categoria_anterior, categoria_atual)
            
            # Verifica critérios de parada
            if (i + 1) == max_hints or rouge_score >= limite_rouge:
                categoria_info = self.extract_security_incidents(nova_resposta)
                resultados.append({
                    "id": incident_id,
                    "informacoes_das_colunas": informacoes_das_colunas,
                    "categoria": categoria_info["Category"],
                    "explicacao": categoria_info["Explanation"],
                    "rouge": rouge_score,
                    "iteracao": i + 1
                })
                break
            
            # Atualiza resposta anterior
            resposta_anterior = nova_resposta
        
        return resultados
    
    def get_name(self) -> str:
        """Retorna o nome da técnica."""
        return "progressive_hint"
    
    def get_description(self) -> str:
        """Retorna descrição da técnica."""
        return "Progressive Hint Prompting - Gera dicas progressivas para melhorar a classificação"