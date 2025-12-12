#!/usr/bin/env python3
"""
SICF - Security Incident Classification Framework CLI
Simple command-line interface for incident classification.
"""

import argparse
import sys
from pathlib import Path
from core.framework import SecurityIncidentFramework
from core.config_loader import ConfigLoader


def main():
    parser = argparse.ArgumentParser(
        description='Security Incident Classification Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Classify incidents
  ./sicf.py classify --config config.yaml --input data/ --columns description --model ollama_gemma2:9b --technique progressive_hint
  
  # List available models
  ./sicf.py list-models --config config.yaml
  
  # List available techniques
  ./sicf.py list-techniques --config config.yaml
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Classify command
    classify = subparsers.add_parser('classify', help='Classify security incidents')
    classify.add_argument('--config', '-c', required=True, help='Path to YAML/JSON config file')
    classify.add_argument('--input', '-i', required=True, help='Input data file or directory')
    classify.add_argument('--columns', '-col', nargs='+', required=True, help='Columns to use for classification')
    classify.add_argument('--model', '-m', required=True, help='Model name from config')
    classify.add_argument('--technique', '-t', required=True, help='Prompt technique name')
    classify.add_argument('--output', '-o', help='Output file path (optional)')
    classify.add_argument('--format', '-f', choices=['csv', 'json', 'xlsx'], default='json', help='Output format')
    
    # List models
    list_models = subparsers.add_parser('list-models', help='List available models')
    list_models.add_argument('--config', '-c', required=True, help='Path to YAML/JSON config file')
    
    # List techniques
    list_techniques = subparsers.add_parser('list-techniques', help='List available techniques')
    list_techniques.add_argument('--config', '-c', required=True, help='Path to YAML/JSON config file')
    
    # Info command
    info = subparsers.add_parser('info', help='Show framework information')
    info.add_argument('--config', '-c', required=True, help='Path to YAML/JSON config file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Load configuration
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"❌ Error: Config file not found: {config_path}")
            sys.exit(1)
        
        config = ConfigLoader.load(str(config_path))
        
        # Execute command
        if args.command == 'classify':
            print(f"🔍 Classifying incidents from: {args.input}")
            print(f"📊 Model: {args.model}")
            print(f"🎯 Technique: {args.technique}")
            print()
            
            framework = SecurityIncidentFramework(str(config_path))
            
            results = framework.process_incidents(
                input_dir=args.input,
                columns=args.columns,
                model_name=args.model,
                prompt_technique=args.technique,
                output_format=args.format
            )
            
            print()
            print("✅ Classification complete!")
            print(f"   Total incidents: {results.get('total_incidents', 0)}")
            print(f"   Output file: {results.get('output_file', 'N/A')}")
            
            if args.output:
                from utils.file_handlers import save_results
                save_results(results.get('results', []), args.output, args.format)
                print(f"   Saved to: {args.output}")
        
        elif args.command == 'list-models':
            config_loader = ConfigLoader()
            models = config_loader.list_available_models(config)
            
            print("\n📋 Available models:\n")
            for model in models:
                model_info = config.get('models', {}).get(model, {})
                provider = model_info.get('provider', 'unknown')
                model_name = model_info.get('model', 'unknown')
                print(f"  • {model}")
                print(f"    Provider: {provider}")
                print(f"    Model: {model_name}")
                print()
        
        elif args.command == 'list-techniques':
            config_loader = ConfigLoader()
            techniques = config_loader.list_available_prompts(config)
            
            print("\n🎯 Available techniques:\n")
            for tech in techniques:
                tech_info = config.get('prompt_techniques', {}).get(tech, {})
                plugin = tech_info.get('plugin', 'unknown')
                print(f"  • {tech}")
                print(f"    Plugin: {plugin}")
                print()
        
        elif args.command == 'info':
            framework_info = config.get('framework', {})
            models = config.get('models', {})
            techniques = config.get('prompt_techniques', {})
            
            print("\n" + "="*60)
            print(f"  {framework_info.get('name', 'Framework')}")
            print(f"  Version: {framework_info.get('version', 'N/A')}")
            print("="*60)
            print(f"\n📊 Statistics:")
            print(f"   Models configured: {len(models)}")
            print(f"   Techniques configured: {len(techniques)}")
            print(f"   NIST categories: {'Enabled' if config.get('nist_categories', {}).get('enabled') else 'Disabled'}")
            print()
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        if '--debug' in sys.argv:
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
