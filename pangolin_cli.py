#!/usr/bin/env python3
"""
Pangolin CLI - Gerenciador de projetos de teste e comparacao de prompts.

Comandos:
  pg init --name <name>     Cria um novo projeto
  pg apply                  Aplica configuracoes do config.yaml
  pg run                    Executa processamento de prompts
  pg destroy --name <name>  Remove um projeto
  pg list                   Lista todos os projetos
  pg info                   Mostra informacoes do projeto atual
"""

import argparse
import sys
from pathlib import Path
from core.pangolin_project import PangolinProject


def cmd_init(args):
    """Comando: init pg --name <name>"""
    if not args.name:
        print("Erro: name do projeto é obrigatório")
        print("   Use: init pg --name <name_do_projeto>")
        return 1
    
    try:
        print(f"Criando projeto '{args.name}'...")
        
        # Cria projeto
        project = PangolinProject(args.name, base_dir=".")
        project.create()
        
        print(f"\nProjeto '{args.name}' criado com sucesso!")
        print(f"\nEstrutura criada:")
        print(f"   {args.name}/")
        print(f"   ├── data/          # Coloque seus dados aqui")
        print(f"   ├── prompts/       # Prompts customizados")
        print(f"   ├── model/         # Modelos")
        print(f"   ├── config.yaml    # Configurações")
        print(f"   └── README.md      # Documentação")
        
        print(f"\nPróximos passos:")
        print(f"   1. cd {args.name}")
        print(f"   2. Coloque seus dados em data/")
        print(f"   3. Edite config.yaml conforme necessário")
        print(f"   4. Execute: apply pg")
        
        return 0
        
    except Exception as e:
        print(f"Erro ao criar projeto: {e}")
        return 1


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
        
        # Importa para validação
        from core.config_loader import ConfigLoader
        from core.plugin_manager import PluginManager
        
        # Carrega config do framework
        framework_config_path = Path(__file__).parent / "config" / "default_config.json"
        if framework_config_path.exists():
            framework_config = ConfigLoader.load(str(framework_config_path))
            plugin_manager = PluginManager()
            
            # Valida modelo
            model_name = config.get('model', {}).get('name')
            if model_name:
                model_config = framework_config.get("models", {}).get(model_name)
                if not model_config:
                    print(f"\n   Aviso: Modelo '{model_name}' nao encontrado no config do framework")
                    print(f"   Modelos disponiveis: {', '.join(list(framework_config.get('models', {}).keys())[:5])}...")
                else:
                    plugin_name = model_config.get("plugin")
                    if plugin_manager.get_model_plugin(plugin_name):
                        print(f"   - Modelo '{model_name}': OK (plugin: {plugin_name})")
                    else:
                        print(f"   - Modelo '{model_name}': Plugin '{plugin_name}' nao encontrado")
            
            # Valida técnica de prompt
            technique = config.get('prompt', {}).get('technique')
            if technique:
                if isinstance(technique, list):
                    technique = technique[0] if technique else None
                    
                if technique:
                    prompt_config = framework_config.get("prompt_techniques", {}).get(technique)
                    if not prompt_config:
                        print(f"\n   Aviso: Tecnica '{technique}' nao encontrada no config do framework")
                        print(f"   Tecnicas disponiveis: {', '.join(list(framework_config.get('prompt_techniques', {}).keys()))}")
                    else:
                        plugin_name = prompt_config.get("plugin")
                        if plugin_manager.get_prompt_plugin(plugin_name):
                            print(f"   - Tecnica '{technique}': OK (plugin: {plugin_name})")
                        else:
                            print(f"   - Tecnica '{technique}': Plugin '{plugin_name}' nao encontrado")
        
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
        print(f"   Modelo: {config.get('model', {}).get('name', 'N/A')}")
        
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


def cmd_destroy(args):
    """Comando: destroy pg --name <name>"""
    if not args.name:
        print("Erro: Nome do projeto e obrigatorio")
        print("   Use: pg destroy --name <name_do_projeto>")
        return 1
    
    try:
        # Verifica se está no diretório do projeto
        project = PangolinProject.load_from_current_dir()
        
        if project is None or project.project_name != args.name:
            print(f"Erro: Voce deve estar dentro do diretorio do projeto '{args.name}'")
            print(f"   cd {args.name} && pg destroy --name {args.name}")
            return 1
        
        # Confirmação
        if not args.force:
            print(f"ATENCAO: Esta acao ira remover permanentemente o projeto '{args.name}'")
            print(f"   Caminho: {project.project_path}")
            response = input(f"\n   Digite 'sim' para confirmar: ")
            
            if response.lower() != 'sim':
                print("Operacao cancelada")
                return 0
        
        print(f"\nRemovendo projeto '{args.name}'...")
        
        # Remove projeto
        project.destroy()
        
        print(f"Projeto '{args.name}' removido com sucesso!")
        print(f"\nDica: Voce ainda esta no diretorio que foi removido")
        print(f"   Execute: cd ..")
        
        return 0
        
    except Exception as e:
        print(f"Erro ao remover projeto: {e}")
        return 1


def cmd_list(args):
    """Comando: list pg"""
    try:
        print("Listando projetos Pangolin...")
        
        projects = PangolinProject.list_projects(".")
        
        if not projects:
            print("\n   Nenhum projeto encontrado no diretorio atual")
            print("\nCrie um novo projeto com: pg init --name <name>")
            return 0
        
        print(f"\n   Encontrados {len(projects)} projeto(s):\n")
        
        for idx, proj in enumerate(projects, 1):
            print(f"   {idx}. {proj['name']}")
            if proj['description']:
                print(f"      Descricao: {proj['description']}")
            if proj['created_at']:
                print(f"      Criado em: {proj['created_at']}")
            print(f"      Caminho: {proj['path']}")
            print()
        
        return 0
        
    except Exception as e:
        print(f"Erro ao listar projetos: {e}")
        return 1


def cmd_info(args):
    """Comando: info pg"""
    try:
        # Verifica se está em um projeto
        project = PangolinProject.load_from_current_dir()
        
        if project is None:
            print("Erro: Voce nao esta em um diretorio de projeto Pangolin")
            return 1
        
        print(f"Informacoes do projeto '{project.project_name}':")
        
        info = project.get_info()
        
        print(f"\nDiretorios:")
        print(f"   Projeto: {info['path']}")
        print(f"   Data: {info['directories']['data']} ({info['file_counts']['data']} arquivos)")
        print(f"   Prompts: {info['directories']['prompts']} ({info['file_counts']['prompts']} arquivos)")
        print(f"   Model: {info['directories']['model']} ({info['file_counts']['model']} arquivos)")
        print(f"   Logs: {info['directories']['logs']} ({info['file_counts']['logs']} arquivos)")
        print(f"   Output: {info['directories']['output']} ({info['file_counts']['output']} arquivos)")
        
        config = info['config']
        print(f"\nConfiguracao:")
        print(f"   Descricao: {config.get('project', {}).get('description', 'N/A')}")
        print(f"   Versao: {config.get('project', {}).get('version', 'N/A')}")
        print(f"   Modelo: {config.get('model', {}).get('name', 'N/A')}")
        print(f"   Tecnica: {config.get('prompt', {}).get('technique', 'N/A')}")
        
        return 0
        
    except Exception as e:
        print(f"Erro ao obter informacoes: {e}")
        return 1


def cmd_run(args):
    """Comando: run pg"""
    try:
        # Verifica se está em um projeto
        project = PangolinProject.load_from_current_dir()
        
        if project is None:
            print("Erro: Voce nao esta em um diretorio de projeto Pangolin")
            print("   Este comando deve ser executado dentro do diretorio do projeto")
            return 1
        
        print(f"Executando processamento no projeto '{project.project_name}'...")
        
        # Carrega configuracao
        config = project.load_config()
        
        # Importa framework apenas quando necessario
        from core.framework import SecurityIncidentFramework
        from core.config_loader import ConfigLoader
        from utils.logger import setup_logger
        
        # Configura logger do projeto
        logger = setup_logger("pg-run", log_dir=str(project.logs_dir))
        
        # Valida dados
        data_files = list(project.data_dir.glob("*"))
        if not data_files:
            print("\nErro: Nenhum arquivo encontrado em data/")
            print("   Adicione seus arquivos de dados antes de executar")
            return 1
        
        # Usa parametros da linha de comando ou do config.yaml
        columns = args.columns if args.columns else config.get('data', {}).get('input_columns', [])
        model_name = args.model if args.model else config.get('model', {}).get('name')
        technique = args.technique if args.technique else config.get('prompt', {}).get('technique')
        output_format = args.output if args.output else config.get('output', {}).get('format', 'csv')
        
        # Valida parametros obrigatorios
        if not columns:
            print("\nErro: Colunas nao especificadas")
            print("   Use --columns ou configure 'data.input_columns' em config.yaml")
            return 1
        
        if not model_name:
            print("\nErro: Modelo nao especificado")
            print("   Use --model ou configure 'model.name' em config.yaml")
            return 1
        
        if not technique:
            print("\nErro: Tecnica nao especificada")
            print("   Use --technique ou configure 'prompt.technique' em config.yaml")
            return 1
        
        # Carrega config do framework (usa config global se disponivel)
        framework_config_path = Path(__file__).parent / "config" / "default_config.json"
        if not framework_config_path.exists():
            # Tenta caminho relativo ao exemplo
            framework_config_path = Path(__file__).parent.parent / "exemplo" / "config" / "default_config.json"
        
        if not framework_config_path.exists():
            print(f"\nErro: Arquivo de configuracao do framework nao encontrado")
            print(f"   Procurado em: {framework_config_path}")
            return 1
        
        # Inicializa framework com projeto
        logger.info(f"Inicializando framework com config: {framework_config_path}")
        framework = SecurityIncidentFramework(str(framework_config_path), project=project)
        
        # Prepara parametros da tecnica
        technique_params = {}
        if args.max_iterations:
            technique_params['max_iterations'] = args.max_iterations
        if args.temperature:
            technique_params['temperature'] = args.temperature
        if args.max_tokens:
            technique_params['max_tokens'] = args.max_tokens
        
        # Processa dados
        print(f"\nProcessando com:")
        print(f"   Modelo: {model_name}")
        print(f"   Tecnica: {technique}")
        print(f"   Colunas: {', '.join(columns)}")
        print(f"   Formato de saida: {output_format}")
        print(f"   Diretorio de dados: {project.data_dir}")
        print(f"   Diretorio de saida: {project.output_dir}")
        print()
        
        results = framework.process_incidents(
            input_dir=str(project.data_dir),
            columns=columns,
            model_name=model_name,
            prompt_technique=technique,
            output_format=output_format,
            **technique_params
        )
        
        # Mostra resumo
        print("\n" + "="*60)
        print("RESUMO DO PROCESSAMENTO")
        print("="*60)
        print(f"Total processado: {results['total_incidents']}")
        print(f"Modelo usado: {results['model_used']}")
        print(f"Tecnica usada: {results['prompt_technique']}")
        print(f"Arquivo de saida: {results['output_file']}")
        
        if 'performance' in results:
            perf = results['performance']
            print(f"Tokens usados: {perf.get('total_tokens', 'N/A')}")
            print(f"Custo estimado: ${perf.get('total_cost', 0):.4f}")
        
        print("\nResultados salvos em:")
        print(f"   {project.output_dir}/")
        print(f"Logs salvos em:")
        print(f"   {project.logs_dir}/")
        
        logger.info("Processamento concluido com sucesso")
        return 0
        
    except FileNotFoundError as e:
        print(f"\nErro: Arquivo nao encontrado: {e}")
        return 1
    except ValueError as e:
        print(f"\nErro de configuracao: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\nProcessamento interrompido pelo usuario")
        return 130
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='Pangolin - Gerenciador de projetos de teste e comparacao de prompts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Criar novo projeto
  pg init --name meu_projeto
  
  # Aplicar configuracoes (dentro do diretorio do projeto)
  cd meu_projeto
  pg apply
  
  # Executar processamento
  pg run --columns descricao --model ollama_gemma2:9b --technique progressive_hint
  
  # Ver informacoes do projeto atual
  pg info
  
  # Listar todos os projetos
  pg list
  
  # Remover projeto (dentro do diretorio do projeto)
  cd meu_projeto
  pg destroy --name meu_projeto
        """
    )
    
    # Comandos principais
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponiveis')
    
    # init pg
    init_parser = subparsers.add_parser('init', help='Criar novo projeto')
    init_parser.add_argument('--name', required=True, help='Nome do projeto')
    
    # apply pg
    apply_parser = subparsers.add_parser('apply', help='Aplicar configuracoes')
    apply_parser.add_argument('--debug', action='store_true', help='Modo debug')
    
    # run pg
    run_parser = subparsers.add_parser('run', help='Executar processamento de prompts')
    run_parser.add_argument('--columns', nargs='+', help='Colunas dos dados para usar (sobrescreve config.yaml)')
    run_parser.add_argument('--model', help='Nome do modelo (sobrescreve config.yaml)')
    run_parser.add_argument('--technique', 
                           choices=['progressive_hint', 'progressive_rectification',
                                   'self_hint', 'hypothesis_testing', 'free_prompt', 'zeroshot'],
                           help='Tecnica de prompt (sobrescreve config.yaml)')
    run_parser.add_argument('--output', choices=['csv', 'json', 'xlsx'], 
                           help='Formato de saida (sobrescreve config.yaml)')
    run_parser.add_argument('--max-iterations', type=int, 
                           help='Maximo de iteracoes para tecnicas iterativas')
    run_parser.add_argument('--temperature', type=float, 
                           help='Temperatura do modelo')
    run_parser.add_argument('--max-tokens', type=int, 
                           help='Maximo de tokens de resposta')
    run_parser.add_argument('--verbose', '-v', action='store_true',
                           help='Saida detalhada')
    
    # destroy pg
    destroy_parser = subparsers.add_parser('destroy', help='Remover projeto')
    destroy_parser.add_argument('--name', required=True, help='Nome do projeto')
    destroy_parser.add_argument('--force', '-f', action='store_true', help='Remover sem confirmacao')
    
    # list pg
    list_parser = subparsers.add_parser('list', help='Listar projetos')
    
    # info pg
    info_parser = subparsers.add_parser('info', help='Informacoes do projeto atual')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Executa comando
    if args.command == 'init':
        return cmd_init(args)
    elif args.command == 'apply':
        return cmd_apply(args)
    elif args.command == 'run':
        return cmd_run(args)
    elif args.command == 'destroy':
        return cmd_destroy(args)
    elif args.command == 'list':
        return cmd_list(args)
    elif args.command == 'info':
        return cmd_info(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
