"""Script de teste para o ZeroShotPlugin."""

import sys
import pandas as pd
from core.plugin_manager import PluginManager

def test_zeroshot_plugin():
    """Testa o ZeroShotPlugin."""
    
    print("="*80)
    print("TESTE DO ZEROSHOTPLUGIN")
    print("="*80)
    
    # Criar plugin manager
    plugin_manager = PluginManager()
    
    # Listar plugins disponíveis
    print("\nPlugins de prompt disponíveis:")
    for plugin_name in plugin_manager.list_available_prompts():
        print(f"  - {plugin_name}")
    
    # Verificar se ZeroShotPlugin está registrado
    if "ZeroShotPlugin" in plugin_manager.list_available_prompts():
        print("\n✓ ZeroShotPlugin está registrado!")
    else:
        print("\n✗ ZeroShotPlugin NÃO está registrado!")
        return False
    
    # Tentar criar instância do modelo (usando mock ou local)
    print("\nCriando instância do modelo...")
    
    # Usar um modelo local simples para teste
    model_config = {
        "provider": "ollama",
        "model": "deepseek-r1:1.5b",
        "temperature": 0.9,
        "max_tokens": 2000,
        "base_url": "http://localhost:11434"
    }
    
    try:
        model_instance = plugin_manager.create_model_instance("LocalModel", model_config)
        if model_instance:
            print("✓ Instância do modelo criada com sucesso!")
        else:
            print("✗ Falha ao criar instância do modelo")
            return False
    except Exception as e:
        print(f"✗ Erro ao criar modelo: {e}")
        return False
    
    # Criar instância do ZeroShotPlugin
    print("\nCriando instância do ZeroShotPlugin...")
    try:
        zeroshot_instance = plugin_manager.create_prompt_instance("ZeroShotPlugin", model_instance)
        if zeroshot_instance:
            print("✓ Instância do ZeroShotPlugin criada com sucesso!")
        else:
            print("✗ Falha ao criar instância do ZeroShotPlugin")
            return False
    except Exception as e:
        print(f"✗ Erro ao criar ZeroShotPlugin: {e}")
        return False
    
    # Verificar nome do plugin
    print(f"\nNome do plugin: {zeroshot_instance.get_name()}")
    
    # Criar um incidente de teste
    print("\nTestando classificação de incidente...")
    test_data = pd.Series({
        'id': 'TEST-001',
        'target': 'Multiple failed SSH login attempts detected from external IP 192.168.1.100'
    })
    
    try:
        # Executar classificação
        result = zeroshot_instance.execute(
            prompt="",  # O ZeroShot ignora o prompt base
            data_row=test_data,
            columns=['target'],
            incident_id='TEST-001'
        )
        
        if result and len(result) > 0:
            print("\n✓ Classificação executada com sucesso!")
            print(f"\nResultado:")
            print(f"  - Category: {result[0].get('Category', 'N/A')}")
            print(f"  - Explanation: {result[0].get('Explanation', 'N/A')[:100]}...")
            return True
        else:
            print("\n✗ Nenhum resultado retornado")
            return False
            
    except Exception as e:
        print(f"\n✗ Erro na classificação: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_zeroshot_plugin()
    
    print("\n" + "="*80)
    if success:
        print("✓ TESTE CONCLUÍDO COM SUCESSO!")
        print("="*80)
        sys.exit(0)
    else:
        print("✗ TESTE FALHOU!")
        print("="*80)
        sys.exit(1)
