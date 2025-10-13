"""Plugin para Free Prompting - Técnica de prompt direto e flexível."""

from .base_prompt import BasePromptPlugin
from typing import Dict, Any, List, Optional
import pandas as pd
import json


class FreePromptPlugin(BasePromptPlugin):
    """
    Plugin para Free Prompting.
    
    Esta técnica envia prompts diretamente ao modelo sem modificações complexas,
    mas oferece flexibilidade para diferentes estratégias de prompt através de
    configurações opcionais.
    """
    
    def __init__(self, model_plugin, **params):
        """
        Inicializa o plugin FreePrompt.
        
        Args:
            model_plugin: Plugin do modelo a ser usado
            **params: Parâmetros de configuração:
                - use_examples: Se deve incluir exemplos no prompt (default: True)
                - use_structured_output: Se deve forçar saída estruturada (default: True)
                - use_context_hints: Se deve incluir dicas contextuais (default: False)
                - temperature_override: Override da temperatura do modelo (opcional)
        """
        super().__init__(model_plugin)
        self.use_examples = params.get("use_examples", True)
        self.use_structured_output = params.get("use_structured_output", True) 
        self.use_context_hints = params.get("use_context_hints", False)
        self.temperature_override = params.get("temperature_override")
        
    def get_name(self) -> str:
        """Retorna o nome da técnica de prompt."""
        return "free_prompt"
    
    def execute(self, prompt: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Implementa Free Prompting com opções configuráveis.
        
        Args:
            prompt: Prompt base (geralmente ignorado, usa prompt próprio)
            data_row: Linha de dados do incidente
            columns: Colunas a serem incluídas
            **kwargs: Parâmetros adicionais
                
        Returns:
            Lista com as respostas do modelo
        """
        incident = self.build_incident_info(data_row, columns)
        incident_id = kwargs.get('incident_id')
        
        # Constrói o prompt completo
        full_prompt = self._build_free_prompt(incident)
        
        # Configurações de envio
        send_kwargs = {
            "mode": "free_prompt",
            "incident_id": incident_id
        }
        
        # Override de temperatura se especificado
        if self.temperature_override is not None:
            send_kwargs["temperature"] = self.temperature_override
            
        # Envia o prompt
        response = self.model_plugin.send_prompt(full_prompt, **send_kwargs)
        
        # Processa a resposta
        processed_response = self._process_response(response)
        
        return [{
            "Response": response,
            "Processed": processed_response,
            "Category": processed_response.get("Category", "Unknown"),
            "Explanation": processed_response.get("Explanation", "Unknown")
        }]
    
    def _build_free_prompt(self, incident: str) -> str:
        """Constrói o prompt completo baseado nas configurações."""
        
        # Prompt base
        base_prompt = """You are a cybersecurity expert specializing in incident classification.
Your task is to analyze security incidents and categorize them according to NIST guidelines."""
        
        # Adiciona contexto de categorias
        categories_info = self._get_categories_info()
        
        # Adiciona exemplos se configurado
        examples_section = ""
        if self.use_examples:
            examples_section = self._get_examples_section()
        
        # Adiciona dicas contextuais se configurado
        context_hints = ""
        if self.use_context_hints:
            context_hints = self._get_context_hints(incident)
        
        # Seção de output
        output_format = self._get_output_format()
        
        # Monta o prompt final
        full_prompt = f"""{base_prompt}

{categories_info}

{examples_section}

{context_hints}

INCIDENT TO CLASSIFY:
{incident}

{output_format}"""
        
        return full_prompt.strip()
    
    def _get_categories_info(self) -> str:
        """Retorna informações sobre as categorias NIST."""
        return """NIST SECURITY INCIDENT CATEGORIES:

• CAT1: Account Compromise – Unauthorized access to user or administrator accounts
  Examples: credential phishing, SSH brute force, OAuth token theft

• CAT2: Malware – Infection by malicious code
  Examples: ransomware, Trojan horse, macro virus

• CAT3: Denial of Service Attack – Making systems unavailable
  Examples: volumetric DoS/DDoS (UDP flood, SYN flood), HTTP/HTTPS attacks

• CAT4: Data Leak – Unauthorized disclosure of sensitive data
  Examples: database theft, leaked credentials

• CAT5: Vulnerability Exploitation – Using technical flaws for attacks
  Examples: CVE exploitation, RCE, SQL injection, exposed services

• CAT6: Insider Abuse – Malicious actions by internal users
  Examples: copying confidential data, sabotage

• CAT7: Social Engineering – Deception to gain access or data
  Examples: phishing, vishing, CEO fraud

• CAT8: Physical Incident – Impact due to unauthorized physical access
  Examples: laptop theft, data center break-in

• CAT9: Unauthorized Modification – Improper changes to systems or data
  Examples: defacement, record manipulation

• CAT10: Misuse of Resources – Unauthorized use for other purposes
  Examples: cryptocurrency mining, malware distribution

• CAT11: Third-Party Issues – Security failures by suppliers
  Examples: SaaS breach, supply chain attack

• CAT12: Intrusion Attempt – Unconfirmed attacks
  Examples: network scans, brute force attempts, blocked exploits"""
    
    def _get_examples_section(self) -> str:
        """Retorna seção com exemplos de classificação."""
        return """CLASSIFICATION EXAMPLES:

Example 1:
Incident: "Multiple failed SSH login attempts detected from external IP 192.168.1.100"
Category: CAT12
Explanation: Network scanning and brute force attempts represent intrusion attempts that were blocked/detected but not successful.

Example 2:
Incident: "Ransomware detected on workstation, files encrypted with .crypto extension"
Category: CAT2
Explanation: Clear malware infection with ransomware, representing malicious code that has successfully infected the system.

Example 3:
Incident: "Employee accessed and downloaded customer database without authorization"
Category: CAT6
Explanation: Internal user performing unauthorized actions, representing insider abuse of access privileges."""
    
    def _get_context_hints(self, incident: str) -> str:
        """Gera dicas contextuais baseadas no incidente."""
        incident_lower = incident.lower()
        hints = []
        
        # Keywords para diferentes categorias
        if any(word in incident_lower for word in ["failed", "login", "attempt", "brute", "password"]):
            hints.append("• Consider if this is an intrusion attempt (CAT12) or successful compromise (CAT1)")
            
        if any(word in incident_lower for word in ["malware", "virus", "ransomware", "trojan"]):
            hints.append("• This appears to involve malicious software (CAT2)")
            
        if any(word in incident_lower for word in ["ddos", "dos", "flood", "unavailable"]):
            hints.append("• Consider denial of service attack classification (CAT3)")
            
        if any(word in incident_lower for word in ["data", "leak", "disclosure", "breach"]):
            hints.append("• Evaluate if this is unauthorized data disclosure (CAT4)")
            
        if any(word in incident_lower for word in ["exploit", "vulnerability", "cve", "injection"]):
            hints.append("• This may involve vulnerability exploitation (CAT5)")
            
        if hints:
            return f"ANALYSIS HINTS:\n" + "\n".join(hints)
        
        return ""
    
    def _get_output_format(self) -> str:
        """Retorna formato de saída esperado."""
        if self.use_structured_output:
            return """REQUIRED OUTPUT FORMAT:
Category: [CAT1-CAT12 or Unknown]
Explanation: [Detailed justification for the chosen category]

If the incident cannot be clearly classified, use:
Category: Unknown
Explanation: Insufficient information or incident doesn't match standard categories"""
        else:
            return "Provide your classification and reasoning."
    
    def _process_response(self, response: str) -> Dict[str, str]:
        """
        Processa a resposta do modelo para extrair categoria e explicação.
        
        Args:
            response: Resposta bruta do modelo
            
        Returns:
            Dicionário com Category e Explanation processadas
        """
        # Tenta usar o método da classe base primeiro
        processed = self.extract_security_incidents(response)
        
        # Se não conseguiu extrair, tenta métodos alternativos
        if processed.get("Category") == "unknown" or processed.get("Explanation") == "unknown":
            processed = self._fallback_extraction(response)
        
        return processed
    
    def _fallback_extraction(self, response: str) -> Dict[str, str]:
        """Método alternativo para extrair informações da resposta."""
        try:
            # Tenta encontrar padrões alternativos
            lines = response.strip().split('\n')
            category = "Unknown"
            explanation = "Unknown"
            
            for line in lines:
                line = line.strip()
                if line.upper().startswith('CATEGORY') or line.upper().startswith('CAT'):
                    # Extrai categoria
                    if ':' in line:
                        category_part = line.split(':', 1)[1].strip()
                        if category_part:
                            category = category_part
                elif line.upper().startswith('EXPLANATION') or line.upper().startswith('JUSTIFICATION'):
                    # Extrai explicação
                    if ':' in line:
                        explanation_part = line.split(':', 1)[1].strip()
                        if explanation_part:
                            explanation = explanation_part
            
            # Se ainda não encontrou, usa a resposta completa como explicação
            if explanation == "Unknown" and category != "Unknown":
                explanation = response.strip()
            
            return {
                "Category": self._extract_cat(category),
                "Explanation": explanation
            }
            
        except Exception as e:
            self.logger.warning(f"Erro no fallback extraction: {e}")
            return {
                "Category": "Unknown", 
                "Explanation": f"Error processing response: {response[:100]}..."
            }