"""Plugin de modelo Mock para testes."""

from typing import Any, Dict
from plugins.models.base_model import BaseModel

class MockModel(BaseModel):
    """Modelo Mock para testes que simula respostas."""
    
    def setup_model(self) -> None:
        """Configura modelo mock."""
        self.logger.info("Mock model configured")
    
    def send_prompt(self, prompt: str, **kwargs: Any) -> str:
        """Simula resposta do modelo."""
        # Simula uma resposta de classificação
        incident_id = kwargs.get('incident_id', 'unknown')
        self.logger.info(f"Processing incident {incident_id}")
        
        # Conta tokens simulados
        input_tokens = len(prompt.split()) 
        
        # Resposta simulada baseada em palavras-chave
        if "login" in prompt.lower() or "suspicious" in prompt.lower():
            response = "Category: CAT1\nExplanation: Account compromise attempt detected based on suspicious login patterns"
        elif "malware" in prompt.lower():
            response = "Category: CAT2\nExplanation: Malware infection detected based on system scanning results"
        elif "data" in prompt.lower() and "access" in prompt.lower():
            response = "Category: CAT4\nExplanation: Potential data leak detected through unusual access patterns"
        else:
            response = "Category: CAT12\nExplanation: Intrusion attempt detected - requires further investigation"
        
        output_tokens = len(response.split())
        
        # Log da interação 
        mode = kwargs.get('mode', 'mock')
        self._log_interaction(prompt, response, input_tokens, output_tokens, mode, incident_id)
        
        return response
    
    def health_check(self) -> bool:
        """Verifica se o modelo está funcionando."""
        return True