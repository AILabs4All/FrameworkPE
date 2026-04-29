from core.pangolin_project import PangolinProject
from pathlib import Path


def cmd_apply(args):
    """Comando: apply pg"""
    try:
        # Verifica se está em um projeto
        project = PangolinProject.load_from_current_dir()
        
        if project is None:
            print("Erro: Voce nao esta em um diretorio de projeto Pangolin")
            print("   Este comando deve ser executado dentro do diretorio do projeto")
            print("   Procurando por config.yaml...")
            return 1
        
        print(f"Aplicando configuracoes do projeto '{project.project_name}'...")
        
        # Carrega e valida configuração
        config = project.load_config()
        is_valid, errors = project.validate_config(config)
        
        if not is_valid:
            print(f"\nConfiguracao invalida em config.yaml:")
            for error in errors:
                print(f"   - {error}")
            return 1
        
        print("Validacao da configuracao: OK")
        
        # Valida disponibilidade de modelos e prompts
        print("\nValidando disponibilidade de plugins...")
        
        from core.plugin_manager import PluginManager
        
        plugin_manager = PluginManager()
        
        # Mapeamento do provider em plugin para validação
        provider_to_plugin = {
            'ollama': 'LocalModel',
            'local': 'LocalModel',
            'huggingface': 'HuggingfaceModel',
            'hungifface': 'HuggingfaceModel',
            'openai': 'APIModel',
            'anthropic': 'APIModel',
            'gemini': 'APIModel',
            'google': 'APIModel',
            'cohere': 'APIModel',
            'azure': 'APIModel',
            'bedrock': 'APIModel',
            'vertex': 'APIModel',
            'palm': 'APIModel'
        }
        
        models = config.get('models', [])
        if models:
            for model_config in models:
                model_name = model_config.get('name')
                provider = model_config.get('provider', '').lower()
                plugin_name = provider_to_plugin.get(provider, 'APIModel')
                
                if plugin_manager.get_model_plugin(plugin_name):
                    print(f"   - Modelo '{model_name}': OK (plugin: {plugin_name})")
                else:
                    print(f"   - Modelo '{model_name}': Plugin '{plugin_name}' não encontrado")
        
        # Valida técnica de prompt
        technique = config.get('prompt', {}).get('technique')
        if technique:
            if isinstance(technique, list):
                technique = technique[0] if technique else None
                
            technique_to_plugin = {
                'progressive_hint': 'ProgressiveHintPlugin',
                'self_hint': 'SelfHintPlugin',
                'progressive_rectification': 'ProgressiveRectificationPlugin',
                'hypothesis_testing': 'HypothesisTestingPlugin',
                'free_prompt': 'FreePromptPlugin',
                'zeroshot': 'ZeroShotPlugin',
                'zeroshot_b': 'ZeroShotPlugin'
            }
                
            if technique:
                plugin_name = technique_to_plugin.get(technique)
                if plugin_name and plugin_manager.get_prompt_plugin(plugin_name):
                    print(f"   - Tecnica '{technique}': OK (plugin: {plugin_name})")
                elif plugin_name:
                    print(f"   - Tecnica '{technique}': Plugin '{plugin_name}' não encontrado")
                else:
                    print(f"   - Tecnica '{technique}': Técnica não conhecida pelo framework")
        
        # Aplica configurações
        result = project.apply()
        
        print(f"\nConfiguracoes aplicadas com sucesso!")
        
        # Mostra arquivos importados
        imported_files = result.get('imported_files', {})
        models_imported = imported_files.get('models', [])
        prompts_imported = imported_files.get('prompts', [])
        
        if models_imported or prompts_imported:
            print(f"\nArquivos importados:")
            if models_imported:
                print(f"   Modelos: {', '.join(models_imported)}")
            if prompts_imported:
                print(f"   Prompts: {', '.join(prompts_imported)}")
        
        print(f"\nResumo da configuracao:")
        
        models_display = [m.get('name', 'N/A') for m in config.get('models', [])]
        print(f"   Modelos: {', '.join(models_display)}")
        
        technique_display = config.get('prompt', {}).get('technique', 'N/A')
        if isinstance(technique_display, list):
            technique_display = ', '.join(technique_display)
        print(f"   Tecnica: {technique_display}")
        
        print(f"   Colunas: {', '.join(config.get('data', {}).get('input_columns', []))}")
        print(f"   Formato de saida: {config.get('output', {}).get('format', 'N/A')}")
        
        # Verifica se há dados
        data_files = list(project.data_dir.glob("*"))
        if data_files:
            print(f"\nArquivos em data/: {len(data_files)}")
        else:
            print(f"\nAtencao: Nenhum arquivo encontrado em data/")
            print(f"   Adicione seus arquivos de dados antes de executar o processamento")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Erro: {e}")
        return 1
    except Exception as e:
        print(f"Erro ao aplicar configuracoes: {e}")
        import traceback
        if hasattr(args, 'debug') and args.debug:
            traceback.print_exc()
        return 1
        
    except FileNotFoundError as e:
        print(f" Erro: {e}")
        return 1
    except Exception as e:
        print(f" Erro ao aplicar configurações: {e}")
        import traceback
        if args.debug:
            traceback.print_exc()
        return 1
