import re
import json
from typing import Dict


def extract_response(texto: str) -> Dict[str, str]:
    """
    Extrai 'Category' e 'Explanation' da resposta do modelo.
    Tenta JSON primeiro; fallback para regex.
    """
    if _is_valid_json(texto):
        dados = json.loads(texto)
        if "Category" in dados and "Explanation" in dados:
            return {
                "Category": dados["Category"].strip(),
                "Explanation": dados["Explanation"].strip(),
            }

    padrao = (
        r"(?:\*\*Category:\*\*|Category:)\s*(.*?)\s*"
        r"(?:\*\*Explanation:\*\*|Explanation:)\s*(.*?)(?=\n|$)"
    )
    matches = re.findall(padrao, texto, re.DOTALL)
    if matches:
        ultima = matches[-1]
        return {
            "Category": ultima[0].replace("*", "").replace("\n", "").strip(),
            "Explanation": ultima[1].replace("*", "").replace("\n", "").strip(),
        }

    return {"Category": "unknown", "Explanation": "unknown"}


def _is_valid_json(texto: str) -> bool:
    try:
        json.loads(texto)
        return True
    except json.JSONDecodeError:
        return False
