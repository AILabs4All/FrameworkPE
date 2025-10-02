from .base_prompt import BasePromptPlugin
from typing import Dict, Any, List
import pandas as pd

class SelfHintPlugin(BasePromptPlugin):
    """Plugin para Self Hint Prompting."""
    
    def execute(self, prompt: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Implementa Self Hint Prompting.
        O modelo gera seu próprio plano e então refina baseado nas próprias respostas.
        """
        max_iter = kwargs.get("max_iter", 4)
        limite_qualidade = kwargs.get("limite_qualidade", 0.9)
        
        # Adiciona formatação de saída
        output_format = """
        If classification is not possible, return:
        Category: Unknown
        Explanation: Unknown
        
        OUTPUT:
        Category: [NIST code]
        Explanation: [Justification for the chosen category]
        """
        
        # Primeira fase: Gera plano
        plano = "Let's first understand the problem and devise a plan to solve the problem. Then, let's carry out the plan and solve the problem step by step."
        prompt_inicial = f"{prompt} {plano}"
        
        # Captura ID do incidente
        incident_id = kwargs.get('incident_id')
        
        # Gera plano intermediário
        plano_intermediario = self.model_plugin.send_prompt(prompt_inicial, mode="shp", incident_id=incident_id)
        
        # Executa plano inicial
        response = self.model_plugin.send_prompt(f"{prompt_inicial} {output_format}", mode="shp", incident_id=incident_id)
        categoria_anterior = self.extract_security_incidents(response)["Category"]
        
        resultados = []
        informacoes_das_colunas = self.build_incident_info(data_row, columns)
        
        # Loop de refinamento
        for i in range(max_iter):
            # Refina com base na categoria anterior
            prompt_reflexao = f"{prompt} {plano_intermediario} The category is: {categoria_anterior} {output_format}"
            response = self.model_plugin.send_prompt(prompt_reflexao, mode="shp", incident_id=incident_id)
            
            incident = self.extract_security_incidents(response)
            categoria_atual = incident["Category"]
            
            # Verifica critérios de parada
            rouge_score = self.calculate_rouge_score(categoria_anterior, categoria_atual)
            
            if (i + 1 == max_iter) or rouge_score >= limite_qualidade:
                resultados.append({
                    "id": incident_id,
                    "informacoes_das_colunas": informacoes_das_colunas,
                    "categoria": categoria_atual,
                    "explicacao": incident["Explanation"],
                    "rouge": rouge_score,
                    "iteracao": i + 1
                })
                return resultados
            else:
                # Prepara próxima iteração
                categoria_anterior = categoria_atual
                prompt_inicial = f"{prompt} {plano} The category is: {categoria_anterior}"
                plano_intermediario = self.model_plugin.send_prompt(prompt_inicial, mode="shp", incident_id=incident_id)
        
        return resultados
    
    def get_name(self) -> str:
        """Retorna o nome da técnica."""
        return "self_hint"
    
    def get_description(self) -> str:
        """Retorna descrição da técnica."""
        return "Self Hint Prompting - O modelo gera seu próprio plano e se auto-refina"