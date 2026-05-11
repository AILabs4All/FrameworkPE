from core.project.pangolin_project import PangolinProject

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
        print(f"Projeto: {info['path']}")
        print(f"Data: {info['directories']['data']} ({info['file_counts']['data']} arquivos)")
        print(f"Schema: {info['directories']['schema']}")
        print(f"Model: {info['directories']['model']} ({info['file_counts']['model']} arquivos)")
        print(f"Logs: {info['directories']['logs']} ({info['file_counts']['logs']} arquivos)")
        print(f"Output: {info['directories']['output']} ({info['file_counts']['output']} arquivos)")
        
        config = info['config']
        print(f"\nConfiguracao:")
        print(f"Descricao: {config.get('project', {}).get('description', 'N/A')}")
        print(f"Versao: {config.get('project', {}).get('version', 'N/A')}")
        models = config.get('models', [])
        model_names = ', '.join(m.get('name', 'N/A') for m in models) if models else 'N/A'
        print(f"Modelos: {model_names}")
        print(f"Tecnica: {config.get('prompt', {}).get('technique', 'N/A')}")
        
        return 0
        
    except Exception as e:
        print(f"Erro ao obter informacoes: {e}")
        return 1
