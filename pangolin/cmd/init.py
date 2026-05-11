"""Module for handling the init command to create new Pangolin projects."""

from core.project.pangolin_project import PangolinProject

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
        print(f"   ├── data/          # Base de dados (coloque seus arquivos CSV/JSON/XLSX aqui)")
        print(f"   ├── schema/        # Definições de técnicas de prompt em YAML")
        print(f"   ├── model/         # Diretorio do modelo")
        print(f"   ├── logs/          # Logs de execucao")
        print(f"   ├── output/        # Resultados das execucoes")
        print(f"   ├── config.yaml    # Configuracoes do projeto")
        print(f"   └── README.md      # Este arquivo")
        
        print(f"\nPróximos passos:")
        print(f"   1. cd {args.name}")
        print(f"   2. Coloque seus dados em data/")
        print(f"   3. Edite config.yaml conforme necessário")
        print(f"   4. Execute: apply pg")
        
        return 0
        
    except Exception as e:
        print(f"Erro ao criar projeto: {e}")
        return 1
