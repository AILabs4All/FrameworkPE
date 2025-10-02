import re
import json
from typing import Dict, Any

def extract_security_incidents(texto: str) -> Dict[str, str]:
    """
    Extrai 'Category' e 'Explanation' do texto fornecido.
    Verifica se o texto é um JSON válido. Caso seja, extrai as informações diretamente do JSON.
    Caso contrário, utiliza regex para extrair as informações.

    Args:
        texto (str): O texto contendo as informações de 'Category' e 'Explanation'.

    Returns:
        dict: Um dicionário contendo os valores de 'Category' e 'Explanation'.
    """
    # Verifica se o texto é um JSON válido
    if is_valid_json(texto):
        dados = json.loads(texto)
        # Verifica se o JSON contém as chaves 'Category' e 'Explanation'
        if "Category" in dados and "Explanation" in dados:
            return {
                "Category": dados["Category"].strip(),
                "Explanation": dados["Explanation"].strip()
            }

    # Caso o texto não seja um JSON válido, continua com regex
    padrao = r"(?:\*\*Category:\*\*|Category:)\s*(.*?)\s*(?:\*\*Explanation:\*\*|Explanation:|Explanation:)\s*(.*?)(?=\n|$)"
    matches = re.findall(padrao, texto, re.DOTALL)

    # Retorna apenas a última ocorrência válida, se existir
    if matches:
        ultima_ocorrencia = matches[-1]
        return {
            "Category": extract_cat(ultima_ocorrencia[0].replace("*", "").replace("\n", "").strip()),
            "Explanation": ultima_ocorrencia[1].replace("*", "").replace("\n", "").strip()
        }
    else:
        return {"Category": "unknown", "Explanation": "unknown"}

def is_valid_json(texto: str) -> bool:
    """
    Verifica se o texto fornecido é um JSON válido.
    
    Args:
        texto (str): O texto a ser verificado.
    
    Returns:
        bool: True se for um JSON válido, False caso contrário.
    """
    try:
        json.loads(texto)
        return True
    except json.JSONDecodeError:
        return False

def extract_cat(texto: str) -> str:
    """
    Procura e retorna o primeiro código CAT (CAT1 a CAT12) encontrado no texto.
    Se não encontrar, retorna o texto original.
    
    Args:
        texto (str): Texto para buscar código CAT
        
    Returns:
        str: Código CAT encontrado ou texto original
    """
    match = re.search(r'\bCAT([1-9]|1[0-2])\b', texto.upper())
    if match:
        return f"CAT{match.group(1)}"
    return texto

def get_nist_categories() -> Dict[str, Dict[str, Any]]:
    """
    Retorna dicionário com todas as categorias NIST e suas subcategorias/keywords.
    
    Returns:
        Dict com categorias NIST completas
    """
    return {
        "CAT1": {
            "name": "Account Compromise",
            "description": "unauthorized access to user or administrator accounts",
            "keywords": ["phishing", "brute force", "unauthorized access", "compromised password", 
                        "credential theft", "account compromise", "token", "oauth", "ssh", "suspicious login"],
            "examples": ["credential phishing", "SSH brute force", "OAuth token theft"]
        },
        "CAT2": {
            "name": "Malware",
            "description": "infection by malicious code",
            "keywords": ["malware", "ransomware", "trojan", "virus", "spyware", "rootkit", "infection", "malicious code"],
            "examples": ["ransomware", "Trojan horse", "macro virus"]
        },
        "CAT3": {
            "name": "Denial of Service Attack",
            "description": "making systems unavailable",
            "keywords": ["ddos", "dos", "denial of service", "flood", "syn flood", "udp flood", "botnet", "api outage", "site down"],
            "examples": ["volumetric DoS or DDoS", "attack on publicly available APIs", "botnet Mirai attacking server"]
        },
        "CAT4": {
            "name": "Data Leak",
            "description": "unauthorized disclosure of sensitive data",
            "keywords": ["data leak", "exposed data", "leaked credentials", "sensitive information", "data exfiltration", "unauthorized disclosure"],
            "examples": ["database theft", "leaked credentials"]
        },
        "CAT5": {
            "name": "Vulnerability Exploitation",
            "description": "using technical flaws for attacks",
            "keywords": ["exploit", "vulnerability", "cve", "remote execution", "sql injection", "injection", "rce", "security flaw"],
            "examples": ["exploitation of critical CVE", "remote code execution (RCE)", "SQL injection in web applications"]
        },
        "CAT6": {
            "name": "Insider Abuse",
            "description": "malicious actions by internal users",
            "keywords": ["insider", "internal abuse", "employee", "internal leak", "sabotage", "intentional action", "staff"],
            "examples": ["copying confidential data", "sabotage"]
        },
        "CAT7": {
            "name": "Social Engineering",
            "description": "deception to gain access or data",
            "keywords": ["social engineering", "phishing", "vishing", "fraud", "deception", "spoofing", "manipulation", "scam", "ceo fraud"],
            "examples": ["phishing", "vishing", "CEO fraud"]
        },
        "CAT8": {
            "name": "Physical Incident",
            "description": "impact due to unauthorized physical access",
            "keywords": ["physical access", "equipment theft", "burglary", "unauthorized entry", "broken door", "physical breach"],
            "examples": ["laptop theft", "data center break-in"]
        },
        "CAT9": {
            "name": "Unauthorized Modification",
            "description": "improper changes to systems or data",  
            "keywords": ["modification", "defacement", "unauthorized change", "erased", "altered record", "tampering"],
            "examples": ["defacement", "record manipulation"]
        },
        "CAT10": {
            "name": "Misuse of Resources",
            "description": "unauthorized use for other purposes",
            "keywords": ["misuse", "resource abuse", "crypto mining", "compromised server", "malware hosting", "unauthorized use"],
            "examples": ["cryptocurrency mining", "malware distribution"]
        },
        "CAT11": {
            "name": "Third-Party Issues",
            "description": "security failures by suppliers",
            "keywords": ["third party", "supplier", "partner", "vendor", "supply chain", "external breach", "saas issue"],
            "examples": ["SaaS breach", "supply chain attack"]
        },
        "CAT12": {
            "name": "Intrusion Attempt",
            "description": "unconfirmed attacks",
            "keywords": ["intrusion attempt", "scan", "reconnaissance", "probing", "port scan", "blocked exploit", "failed attempt"],
            "examples": ["network scans", "brute force", "blocked exploits"]
        },
        "UNKNOWN": {
            "name": "Unknown/Unclassified",
            "description": "incidents that cannot be classified",
            "keywords": ["unknown", "unspecified", "not categorized", "no category", "undefined", "other"],
            "examples": ["unspecified security event", "unclear incident type"]
        }
    }

def get_subcategories(categoria: str) -> list:
    """
    Dado o valor da chave (ex: 'CAT1'), retorna a lista de palavras-chave correspondente.
    Se não encontrar, retorna uma lista vazia.
    
    Args:
        categoria (str): Código da categoria (ex: 'CAT1')
        
    Returns:
        list: Lista de palavras-chave para a categoria
    """
    nist_cats = get_nist_categories()
    return nist_cats.get(categoria.strip().upper(), {}).get("keywords", [])