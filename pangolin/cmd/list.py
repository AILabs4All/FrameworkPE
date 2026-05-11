from core.project.pangolin_project import PangolinProject

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
