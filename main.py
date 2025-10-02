#!/usr/bin/env python3
"""
Framework de Classificação de Incidentes de Segurança
Sistema plugável para classificação usando diferentes LLMs/SLMs e técnicas de prompt
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Dict, Any

from core.framework import SecurityIncidentFramework
from utils.logger import setup_logger

# Mapeamento de modos legados para nomes de técnicas
MODE_MAPPING = {
    'php': 'progressive_hint',
    'prp': 'progressive_rectification', 
    'shp': 'self_hint',
    'htp': 'hypothesis_testing'
}

def setup_argument_parser() -> argparse.ArgumentParser:
    """Configura o parser de argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Framework de Classificação de Incidentes de Segurança",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s data/ --columns "descricao" "tipo" --model openai_gpt4 --technique progressive_hint
  %(prog)s data/ --columns "descricao" --model ollama_llama3 --technique self_hint --output json
  %(prog)s data/ --columns "descricao" "severidade" --model hf_bert --technique hypothesis_testing --config custom_config.json
  
Técnicas disponíveis:
  - progressive_hint: Progressive Hint Prompting
  - progressive_rectification: Progressive Rectification  
  - self_hint: Self Hint Prompting
  - hypothesis_testing: Hypothesis Testing
  
Compatibilidade com versões anteriores:
  --mode php é equivalente a --technique progressive_hint
        """
    )
    
    # Argumentos obrigatórios
    parser.add_argument('input_dir', 
                       help="Diretório contendo arquivos de incidentes (CSV, JSON, XLSX)")
    
    parser.add_argument('--columns', nargs='+', required=True,
                       help="Colunas dos dados para usar na classificação")
    
    # Seleção do modelo
    model_group = parser.add_mutually_exclusive_group(required=True)
    model_group.add_argument('--model', 
                            help="Nome do modelo configurado (ex: openai_gpt4, ollama_llama3)")
    model_group.add_argument('--provider', dest='model',  # Para compatibilidade
                            help="(Depreciado) Use --model")
    
    # Seleção da técnica
    technique_group = parser.add_mutually_exclusive_group()
    technique_group.add_argument('--technique',
                                choices=['progressive_hint', 'progressive_rectification',
                                        'self_hint', 'hypothesis_testing'],
                                default='progressive_hint',
                                help="Técnica de prompt a usar")
    technique_group.add_argument('--mode',  # Para compatibilidade
                                choices=['php', 'prp', 'shp', 'htp'],
                                help="(Depreciado) Use --technique")
    
    # Configurações opcionais
    parser.add_argument('--config', default="config/default_config.json",
                       help="Arquivo de configuração (default: config/default_config.json)")
    
    parser.add_argument('--output', choices=['csv', 'json', 'xlsx'], default='csv',
                       help="Formato de saída (default: csv)")
    
    parser.add_argument('--output-dir', default="output",
                       help="Diretório para salvar resultados (default: output)")
    
    # Parâmetros específicos das técnicas
    parser.add_argument('--max-iterations', type=int, default=3,
                       help="Máximo de iterações para técnicas iterativas")
    
    parser.add_argument('--rouge-threshold', type=float, default=0.7,
                       help="Threshold ROUGE para Progressive Hint")
    
    parser.add_argument('--temperature', type=float,
                       help="Temperatura do modelo (se suportado)")
    
    parser.add_argument('--max-tokens', type=int,
                       help="Máximo de tokens de resposta")
    
    # Utilidades
    parser.add_argument('--list-models', action='store_true',
                       help="Lista modelos disponíveis e sai")
    
    parser.add_argument('--list-techniques', action='store_true',
                       help="Lista técnicas disponíveis e sai")
    
    parser.add_argument('--info', action='store_true',
                       help="Mostra informações do framework e sai")
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help="Saída detalhada")
    
    return parser

def validate_arguments(args: argparse.Namespace) -> str:
    """Valida e normaliza argumentos."""
    # Compatibilidade com --mode
    if args.mode:
        if args.mode in MODE_MAPPING:
            technique = MODE_MAPPING[args.mode]
            print(f"Aviso: --mode está depreciado. Use --technique {technique}")
            return technique
        else:
            raise ValueError(f"Modo inválido: {args.mode}")
    
    return args.technique

def handle_info_commands(framework: SecurityIncidentFramework, args: argparse.Namespace) -> bool:
    """Processa comandos informativos. Retorna True se deve sair."""
    if args.list_models:
        models = framework.list_available_models()
        print("Modelos Disponíveis:")
        for model in models:
            print(f"  - {model}")
        return True
    
    if args.list_techniques:
        techniques = framework.list_available_prompts()
        print("Técnicas de Prompt Disponíveis:")
        for technique in techniques:
            print(f"  - {technique}")
        return True
    
    if args.info:
        info = framework.get_framework_info()
        print("Informações do Framework:")
        print(json.dumps(info, indent=2, ensure_ascii=False))
        return True
    
    return False

def main():
    """Função principal."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Configura logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logger("main", log_level=log_level)
    
    try:
        # Inicializa framework
        logger.info("Inicializando Framework de Classificação de Incidentes")
        framework = SecurityIncidentFramework(args.config)
        
        # Processa comandos informativos
        if handle_info_commands(framework, args):
            return 0
        
        # Valida argumentos
        technique = validate_arguments(args)
        
        # Valida entrada
        input_path = Path(args.input_dir)
        if not input_path.exists():
            logger.error(f"Diretório não encontrado: {args.input_dir}")
            return 1
        
        # Prepara parâmetros da técnica
        technique_params = {}
        if args.max_iterations:
            technique_params['max_iterations'] = args.max_iterations
        if args.rouge_threshold:
            technique_params['rouge_threshold'] = args.rouge_threshold
        if args.temperature:
            technique_params['temperature'] = args.temperature
        if args.max_tokens:
            technique_params['max_tokens'] = args.max_tokens
        
        # Processa incidentes
        logger.info(f"Processando incidentes com modelo '{args.model}' e técnica '{technique}'")
        
        results = framework.process_incidents(
            input_dir=str(input_path),
            columns=args.columns,
            model_name=args.model,
            prompt_technique=technique,
            output_format=args.output,
            **technique_params
        )
        
        # Mostra resumo
        print("\n" + "="*60)
        print("RESUMO DO PROCESSAMENTO")
        print("="*60)
        print(f"Total de incidentes processados: {results['total_incidents']}")
        print(f"Modelo usado: {results['model_used']}")
        print(f"Técnica usada: {results['prompt_technique']}")
        print(f"Arquivo de saída: {results['output_file']}")
        
        if 'performance' in results:
            perf = results['performance']
            print(f"Tokens usados: {perf.get('total_tokens', 'N/A')}")
            print(f"Custo estimado: ${perf.get('total_cost', 0):.4f}")
        
        logger.info("Processamento concluído com sucesso")
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"Arquivo não encontrado: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Erro de configuração: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("Processamento interrompido pelo usuário")
        return 130
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())