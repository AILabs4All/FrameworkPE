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
        incident = self.build_incident_info(data_row, columns)
        incident_id = kwargs.get('incident_id')
        
        # Constrói o prompt zero-shot completo
        full_prompt = self._build_zeroshot_prompt(incident)
        
        # Configurações de envio
        send_kwargs = {
            "mode": "zeroshot",
            "incident_id": incident_id
        }
        
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
    
    def _build_zeroshot_prompt(self, incident: str) -> str:
        """Constrói o prompt zero-shot completo."""
        
        prompt = f"""You are a cybersecurity expert.

Your task:
Classify the following incident description into one of the predefined NIST categories (CAT1–CAT12),
and provide a concise justification for your choice.

---

### NIST Categories for Classification

- **CAT1: Account Compromise** – unauthorized access to user or administrator accounts.  
  Examples: credential phishing, SSH brute force, OAuth token theft.  
  Search terms: ["phishing", "brute force", "unauthorized access", "compromised password", "credential theft", "account compromise", "token", "oauth", "ssh", "suspicious login"]

- **CAT2: Malware** – infection by malicious code.  
  Examples: ransomware, Trojan horse, macro virus.  
  Search terms: ["malware", "ransomware", "trojan", "virus", "spyware", "rootkit", "infection", "malicious code"]

- **CAT3: Denial of Service Attack** – making systems unavailable.  
  Examples: volumetric DoS or DDoS (UDP flood, SYN flood, HTTP/HTTPS flood), attacks on APIs or websites, Mirai botnet.  
  Search terms: ["ddos", "dos", "denial of service", "flood", "syn flood", "udp flood", "botnet", "api outage", "site down"]

- **CAT4: Data Leak** – unauthorized disclosure of sensitive data.  
  Examples: database theft, leaked credentials.  
  Search terms: ["data leak", "exposed data", "leaked credentials", "sensitive information", "data exfiltration", "unauthorized disclosure"]

- **CAT5: Vulnerability Exploitation** – using technical flaws for attacks.  
  Examples: exploitation of CVE, RCE, SQL injection, or insecure service exposure (e.g., NTP monlist, DNS ANY, open Memcached).  
  Search terms: ["exploit", "vulnerability", "cve", "remote execution", "sql injection", "injection", "rce", "security flaw"]

- **CAT6: Insider Abuse** – malicious or negligent actions by internal users.  
  Examples: copying confidential data, sabotage, misuse of access.  
  Search terms: ["insider", "internal abuse", "employee", "internal leak", "sabotage", "intentional action", "staff"]

- **CAT7: Social Engineering** – deception to gain access or data.  
  Examples: phishing, vishing, CEO fraud, pretexting.  
  Search terms: ["social engineering", "phishing", "vishing", "fraud", "deception", "spoofing", "manipulation", "scam", "ceo fraud"]

- **CAT8: Physical Incident** – unauthorized physical access or impact.  
  Examples: equipment theft, data center break-in.  
  Search terms: ["physical access", "equipment theft", "burglary", "unauthorized entry", "broken door", "physical breach"]

- **CAT9: Unauthorized Modification** – improper changes to systems or data.  
  Examples: website defacement, alteration of records or logs.  
  Search terms: ["modification", "defacement", "unauthorized change", "erased", "altered record", "tampering"]

- **CAT10: Misuse of Resources** – using systems for non-authorized purposes.  
  Examples: cryptocurrency mining, spam campaigns, malware hosting.  
  Search terms: ["misuse", "resource abuse", "crypto mining", "compromised server", "malware hosting", "unauthorized use"]

- **CAT11: Third-Party Issues** – security incidents from suppliers or service providers.  
  Examples: SaaS breach, supply-chain compromise.  
  Search terms: ["third party", "supplier", "partner", "vendor", "supply chain", "external breach", "saas issue"]

- **CAT12: Intrusion Attempt** – unconfirmed or prevented attacks.  
  Examples: network scans, brute force attempts, blocked exploit attempts.  
  Search terms: ["intrusion attempt", "scan", "reconnaissance", "probing", "port scan", "blocked exploit", "failed attempt"]

---

### Input:
Incident Description:
{incident}

---

### Output format:
Category: [CAT number, e.g., CAT5]  
Explanation: [Concise justification linking the description to the chosen category]

If classification is not possible, return:
Category: Unknown  
Explanation: Unknown
"""
        
        return prompt.strip()
    
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
            
        except (ValueError, AttributeError, KeyError) as e:
            self.logger.warning("Erro no fallback extraction: %s", str(e))
            return {
                "Category": "Unknown", 
                "Explanation": f"Error processing response: {response[:100]}..."
            }

