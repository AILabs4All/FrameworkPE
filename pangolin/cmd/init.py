"""Module for handling the init command to create new Pangolin projects."""

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
