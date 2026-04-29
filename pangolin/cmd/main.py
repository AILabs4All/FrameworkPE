from pathlib import Path
import argparse
import sys

# Adiciona o diretório raiz do projeto ao sys.path para poder importar módulos como 'core'
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cmd.init import cmd_init
from cmd.apply import cmd_apply
from cmd.run import cmd_run
from cmd.destroy import cmd_destroy
from cmd.list import cmd_list
from cmd.info import cmd_info

DESCRIPTION = """Pangolin
                - Gerenciador de projetos de teste e comparacao de prompts
                - Facilita a organizacao, execucao e analise de experimentos com LLMs
                - Geração de Playbooks para replicacao de experimentos
    """

EPILOG = """Exemplos:
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

PROMPT_ENGINEERING_TECHNIQUES = [
        "progressive_hint",
        "progressive_rectification",
        "self_hint",
        "hypothesis_testing",
        "free_prompt",
        "zeroshot"
]

OUTPUT_FORMATS = [
        "csv",
        "json",
        "xlsx"
]

def main():
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EPILOG
    )

    subparsers = parser.add_subparsers(dest='command',
                    help='Comandos disponiveis'
    )

    init_parser = subparsers.add_parser('init',
                    help='Criar novo projeto'
    )

    init_parser.add_argument('--name',
                    required=True,
                    help='Nome do projeto'
    )

    apply_parser = subparsers.add_parser('apply',
                    help='Aplicar configuracoes'
    )

    apply_parser.add_argument('--debug',
                    action='store_true',
                    help='Modo debug'
    )


    run_parser = subparsers.add_parser('run',
                                        help='Executar processamento de prompts'
    )
    run_parser.add_argument('--columns',
                            nargs='+',
                            help='Colunas dos dados para usar (sobrescreve config.yaml)'
    )

    run_parser.add_argument('--model',
                            help='Nome do modelo (sobrescreve config.yaml)'
    )

    run_parser.add_argument('--technique',
                           choices=PROMPT_ENGINEERING_TECHNIQUES,
                           help='Tecnica de prompt (sobrescreve config.yaml)'
    )

    run_parser.add_argument('--output',
                            choices=OUTPUT_FORMATS,
                            help='Formato de saida (sobrescreve config.yaml)'
    )

    run_parser.add_argument('--max-iterations',
                            type=int,
                            help='Maximo de iteracoes para tecnicas iterativas'
    )

    run_parser.add_argument('--temperature',
                            type=float,
                            help='Temperatura do modelo'
    )

    run_parser.add_argument('--max-tokens',
                        type=int,
                        help='Tamanho maximo da resposta do modelo'
    )

    run_parser.add_argument('--verbose',
                        '-v',
                        action='store_true',
                        help='Saida detalhada'
    )

    destroy_parser = subparsers.add_parser('destroy',
                                           help='Remover projeto'
    )
    
    destroy_parser.add_argument('--name',
                                required=True,
                                help='Nome do projeto'
    )
    destroy_parser.add_argument('--force',
                                '-f', action='store_true',
                                help='Remover sem confirmacao'
    )
    
    # list pg
    list_parser = subparsers.add_parser('list',
                                        help='Listar projetos'
    )
    
    # info pg
    info_parser = subparsers.add_parser('info',
                                        help='Informacoes do projeto atual'
)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
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
