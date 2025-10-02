from .base_prompt import BasePromptPlugin
from typing import Dict, Any, List, Optional
import pandas as pd

class ProgressiveRectificationPlugin(BasePromptPlugin):
    """Plugin para Progressive Rectification Prompting."""
    
    def execute(self, prompt: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Implementa Progressive Rectification Prompting.
        Valida respostas mascarando palavras-chave e retificando quando necessário.
        """
        max_iter = kwargs.get("max_iter", 4)
        limite_qualidade = kwargs.get("limite_qualidade", 0.9)
        
        output_format = """
        If classification is not possible, return:
        Category: Unknown
        Explanation: Unknown
        
        OUTPUT:
        Category: [NIST code]
        Explanation: [Justification for the chosen category]
        """
        
        informacoes_das_colunas = self.build_incident_info(data_row, columns)
        
        # Captura ID do incidente
        incident_id = kwargs.get('incident_id')
        
        # Resposta inicial
        r_0 = self.model_plugin.send_prompt(f"{prompt} {output_format}", mode="prp", incident_id=incident_id)
        a_0 = self.extract_security_incidents(r_0)
        categoria_atual = a_0["Category"]
        categoria_rejectada = ''
        
        attempt = 0
        resultados = []
        
        while attempt < max_iter:
            subcategory = self._get_subcategories(categoria_atual)
            
            for subcat in subcategory:
                categoria_anterior = categoria_atual
                
                # Mascara o incidente
                incidente_mascarado = self._mask_prompt(prompt, subcat, incident_id)
                
                # Valida resposta
                categoria_atual = self._validate_response(incidente_mascarado, categoria_atual, subcat, incident_id)
                
                # Calcula qualidade
                qualidade = self.calculate_rouge_score(str(categoria_anterior), str(categoria_atual))
                
                if qualidade >= limite_qualidade:
                    resultados.append({
                        "id": incident_id,
                        "informacoes_das_colunas": informacoes_das_colunas,
                        "categoria": categoria_atual,
                        "explicacao": a_0["Explanation"],
                        "qualidade": qualidade,
                        "iteracao": attempt + 1
                    })
                    return resultados
                else:
                    # Retifica
                    categoria_rejectada = ',' + categoria_atual
                    rectification_prompt = self._build_rectification_prompt(prompt, categoria_rejectada)
                    response = self.model_plugin.send_prompt(rectification_prompt, mode="prp", incident_id=incident_id)
                    incident = self.extract_security_incidents(response)
                    categoria_atual = incident["Category"]
            
            attempt += 1
        
        # Retorna resultado final se não convergiu
        resultados.append({
            "id": incident_id,
            "informacoes_das_colunas": informacoes_das_colunas,
            "categoria": categoria_atual,
            "explicacao": a_0["Explanation"],
            "qualidade": 0.0,
            "iteracao": max_iter
        })
        return resultados
    
    def _build_rectification_prompt(self, prompt: str, categoria_rejectada: str = "") -> str:
        """Constrói prompt de retificação."""
        return f"""
        Incident: {prompt}
        The answer is probably not: {categoria_rejectada}
        Let's think step by step to reclassify.
        
        OUTPUT:
        Category: [NIST code]
        Explanation: [Justification for the chosen category]
        """
    
    def _validate_response(self, prompt: str, category: str, subcategory: str, incident_id: Optional[str] = None) -> str:
        """Valida resposta usando prompt mascarado."""
        prompt_verification = f"""{prompt}
        Incident (masked): {subcategory}
        Hypothesis: {category}
        Question: What is the value of X in the Incident? (If not applicable, respond 'Unknown')
        
        OUTPUT:
        Category: [NIST code]
        Explanation: [Justification for the chosen category]
        """
        response = self.model_plugin.send_prompt(prompt_verification, mode="prp", incident_id=incident_id)
        return self.extract_security_incidents(response)['Category']
    
    def _mask_prompt(self, prompt: str, subcat: str, incident_id: Optional[str] = None) -> str:
        """Mascara ocorrências de subcategoria no prompt."""
        mascarar = f"""
        {prompt}
        Replace all occurrences of the word '{subcat}' with 'X' in a given text. 
        Ensure that the substitution preserves the original context and sentence structure.
        """
        return self.model_plugin.send_prompt(mascarar, mode="prp", incident_id=incident_id)
    
    def _get_subcategories(self, categoria: str) -> List[str]:
        """Retorna subcategorias para uma categoria NIST."""
        palavras_chave = {
            "CAT1": ["phishing", "brute force", "unauthorized access", "compromised password", "credential theft", "account compromise", "token", "oauth", "ssh", "suspicious login"],
            "CAT2": ["malware", "ransomware", "trojan", "virus", "spyware", "rootkit", "infection", "malicious code"],
            "CAT3": ["ddos", "dos", "denial of service", "flood", "syn flood", "udp flood", "botnet", "api outage", "site down"],
            "CAT4": ["data leak", "exposed data", "leaked credentials", "sensitive information", "data exfiltration", "unauthorized disclosure"],
            "CAT5": ["exploit", "vulnerability", "cve", "remote execution", "sql injection", "injection", "rce", "security flaw"],
            "CAT6": ["insider", "internal abuse", "employee", "internal leak", "sabotage", "intentional action", "staff"],
            "CAT7": ["social engineering", "phishing", "vishing", "fraud", "deception", "spoofing", "manipulation", "scam", "ceo fraud"],
            "CAT8": ["physical access", "equipment theft", "burglary", "unauthorized entry", "broken door", "physical breach"],
            "CAT9": ["modification", "defacement", "unauthorized change", "erased", "altered record", "tampering"],
            "CAT10": ["misuse", "resource abuse", "crypto mining", "compromised server", "malware hosting", "unauthorized use"],
            "CAT11": ["third party", "supplier", "partner", "vendor", "supply chain", "external breach", "saas issue"],
            "CAT12": ["intrusion attempt", "scan", "reconnaissance", "probing", "port scan", "blocked exploit", "failed attempt"],
            "UNKNOWN": ["unknown", "unspecified", "not categorized", "no category", "undefined", "other"]
        }
        return palavras_chave.get(categoria.strip().upper(), [])
    
    def get_name(self) -> str:
        """Retorna o nome da técnica."""
        return "progressive_rectification"
    
    def get_description(self) -> str:
        """Retorna descrição da técnica."""
        return "Progressive Rectification Prompting - Valida e retifica respostas usando mascaramento"