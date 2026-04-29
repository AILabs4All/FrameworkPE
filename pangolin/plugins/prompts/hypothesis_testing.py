from .base_prompt import BasePromptPlugin
from typing import Dict, Any, List
import pandas as pd

class HypothesisTestingPlugin(BasePromptPlugin):
    """Plugin para Hypothesis Testing Prompting."""
    
    def execute(self, prompt: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Implementa Hypothesis Testing Prompting.
        Para cada categoria CATx, testa a hipótese usando as keywords correspondentes.
        """
        max_iter = kwargs.get("max_iter", 12)
        limite_qualidade = kwargs.get("limite_qualidade", 0.9)
        
        results = []
        incident = self.build_incident_info(data_row, columns)
        categories = [f"CAT{i}" for i in range(1, 13)]
        
        i = 0
        while i < len(categories) and i < max_iter:
            category = categories[i]
            keywords = self._get_subcategories(category)
            keywords_str = ', '.join(keywords)
            
            prompt_llm = f"""
            Security Incident Analysis System - HTP

            Incident Description:
            "{prompt}"

            Instructions:
            For NIST category Considered tha Category: {category} and keyword: {keywords_str} perform the following steps:

            1. True Hypothesis:
               - Assume the incident belongs to this category. Justify based on the description and keywords.
               - Indicate whether the hypothesis is SUPPORTED or NOT SUPPORTED.

            2. False Hypothesis:
               - Assume the incident does NOT belong to this category. Justify based on the lack of evidence.
               - Indicate whether the hypothesis is SUPPORTED or NOT SUPPORTED.
            
            Return the hypotheses in the following format:
                True Hypothesis:[SUPPORTED/NOT SUPPORTED] 
                False Hypothesis:[SUPPORTED/NOT SUPPORTED]
            
            Final Classification Decision:
              - If the True Hypothesis is SUPPORTED and the False Hypothesis is NOT SUPPORTED, return:
                Category: same {category}
                Explanation: [Justification for the chosen same considered {category}]
              - Otherwise, return "UNKNOWN" as the final classification.
                Category: UNKNOWN
                Explanation: UNKNOWN    
            """
            
            incident_id = kwargs.get('incident_id')
            hipoteses = self.model_plugin.send_prompt(prompt_llm, mode="htp", incident_id=incident_id)
            incident_info = self.extract_security_incidents(hipoteses)
            result_cat = incident_info['Category']
            
            # Verifica se a hipótese foi confirmada com alta qualidade
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
        
        # Se nenhuma categoria foi confirmada, retorna resultado desconhecido
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
        return "hypothesis_testing"
    
    def get_description(self) -> str:
        """Retorna descrição da técnica."""
        return "Hypothesis Testing Prompting - Testa hipóteses para cada categoria NIST sistematicamente"