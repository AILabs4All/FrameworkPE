from pangolin.core.project.pangolin_project import PangolinProject
from pathlib import Path

def cmd_destroy(args):
    """Comando: pg destroy --name <name>"""
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
        
        # Remove projeto (troca o cwd para o parent internamente, se necessário)
        projeto = project
        cwd_antes = Path.cwd()
        parent_antes = None
        if cwd_antes.resolve() == project.project_path.resolve():
            parent_antes = project.project_path.parent
        projeto.destroy()
        
        print(f"Projeto '{args.name}' removido com sucesso!")
        if parent_antes is not None:
            print(f"\nAgora você está em: {Path.cwd()}")
        
        return 0
        
    except Exception as e:
        print(f"Erro ao remover projeto: {e}")
        return 1
