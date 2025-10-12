#!/usr/bin/env python3
"""Script de exemplo para testar o HuggingfaceModel."""

import sys
import os
import json

# Adicionar o diretório do framework ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugins.models.hungguiface_model import HuggingfaceModel


def test_huggingface_model():
    """Testa a classe HuggingfaceModel com o exemplo do Foundation-Sec-8B."""
    
    # Configuração do modelo
    config = {
        "provider": "huggingface",
        "model": "fdtn-ai/Foundation-Sec-8B",
        "model_path": "fdtn-ai/Foundation-Sec-8B",
        "temperature": 0.1,
        "max_tokens": 3,
        "device": "auto",
        "load_config": {
            "model": {
                "trust_remote_code": False,
                "low_cpu_mem_usage": True
            },
            "tokenizer": {
                "trust_remote_code": False
            }
        }
    }
    
    # Prompt de exemplo
    prompt = """CVE-2021-44228 is a remote code execution flaw in Apache Log4j2 via unsafe JNDI lookups ("Log4Shell"). The CWE is CWE-502.

CVE-2017-0144 is a remote code execution vulnerability in Microsoft's SMBv1 server ("EternalBlue") due to a buffer overflow. The CWE is CWE-119.

CVE-2014-0160 is an information-disclosure bug in OpenSSL's heartbeat extension ("Heartbleed") causing out-of-bounds reads. The CWE is CWE-125.

CVE-2017-5638 is a remote code execution issue in Apache Struts 2's Jakarta Multipart parser stemming from improper input validation of the Content-Type header. The CWE is CWE-20.

CVE-2019-0708 is a remote code execution vulnerability in Microsoft's Remote Desktop Services ("BlueKeep") triggered by a use-after-free. The CWE is CWE-416.

CVE-2015-10011 is a vulnerability about OpenDNS OpenResolve improper log output neutralization. The CWE is"""
    
    try:
        print("Inicializando modelo HuggingFace...")
        model = HuggingfaceModel(config)
        
        print("Informações do modelo:")
        info = model.get_model_info()
        print(json.dumps(info, indent=2))
        
        print("\nEnviando prompt...")
        print(f"Prompt: {prompt[-100:]}...")  # Mostrar apenas o final do prompt
        
        response = model.send_prompt(
            prompt,
            max_new_tokens=3,
            do_sample=True,
            temperature=0.1,
            top_p=0.9
        )
        
        print(f"\nResposta: {response}")
        
    except Exception as e:
        print(f"Erro durante o teste: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("=== Teste do HuggingfaceModel ===")
    success = test_huggingface_model()
    print(f"\nTeste {'PASSOU' if success else 'FALHOU'}")