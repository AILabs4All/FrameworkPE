#!/usr/bin/env python3
"""
Automação de Execução do Framework de Classificação de Incidentes
Executa todos os modelos e técnicas de prompt de forma automatizada
"""

import subprocess
import sys
import json
import time
from pathlib import Path

# Lista de modelos e seus respectivos nomes no Ollama
MODELS = {
    "ollama_qwen3_1_7b": "qwen3:1.7b",
    "ollama_qwen3_4b": "qwen3:4b", 
    "ollama_qwen3_8b": "qwen3:8b",
    "ollama_llama3_1_8b": "llama3.1:8b",
    "ollama_llama3_2_1b": "llama3.2:1b",
    "ollama_llama3_2_3b": "llama3.2:3b",
    "ollama_deepseek_r1_7b": "deepseek-r1:7b",
    "ollama_deepseek_r1_8b": "deepseek-r1:8b",
    "ollama_deepseek_r1_14b": "deepseek-r1:14b",
    "ollama_phi3_3_8b": "phi3:3.8b",
    "ollama_phi3_14b": "phi3:14b",
    "ollama_smollm2_135m": "smollm2:135m",
    "ollama_smollm2_360m": "smollm2:360m",
    "ollama_smollm2_1_7b": "smollm2:1.7b",
    "ollama_falcon3_1b": "falcon3:1b",
    "ollama_falcon3_3b": "falcon3:3b",
    "ollama_falcon3_7b": "falcon3:7b",
    "ollama_falcon3_10b": "falcon3:10b",
}

# Lista de técnicas de prompt
TECHNIQUES = [
    "progressive_hint",
    "progressive_rectification", 
    "self_hint",
    "hypothesis_testing"
]

def check_model_available(model_name: str) -> bool:
    """
    Verifica se o modelo está disponível no Ollama
    """
    try:
        result = subprocess.run(
            ["docker", "exec", "ollama", "ollama", "list"],
            capture_output=True, 
            text=True,
            check=True
        )
        return model_name in result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Erro ao verificar modelos: {e}")
        return False

def pull_model(model_name: str) -> bool:
    """
    Faz o download do modelo se não estiver disponível
    """
    print(f"🔄 Baixando modelo {model_name}...")
    try:
        result = subprocess.run(
            ["docker", "exec", "ollama", "ollama", "pull", model_name],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Modelo {model_name} baixado com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao baixar modelo {model_name}: {e}")
        return False

def run_experiment(framework_model: str, ollama_model: str, technique: str, data_dir: str = "data") -> bool:
    """
    Executa uma combinação específica de modelo e técnica
    """
    print(f"\n{'='*80}")
    print(f"🚀 EXECUTANDO: Modelo {framework_model} | Técnica {technique}")
    print(f"{'='*80}")
    
    # Verifica se o modelo está disponível
    if not check_model_available(ollama_model):
        print(f"📥 Modelo {ollama_model} não encontrado. Iniciando download...")
        if not pull_model(ollama_model):
            print(f"⏭️  Pulando modelo {framework_model} devido a erro no download")
            return False
    
    # Constrói o comando
    cmd = [
        "python3", "main.py",
        data_dir,
        "--columns", "target",
        "--model", framework_model,
        "--technique", technique,
        "--output", "xlsx",
        "--verbose"
    ]
    
    print(f"📋 Comando: {' '.join(cmd)}")
    
    try:
        # Executa o comando
        start_time = time.time()
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        execution_time = time.time() - start_time
        
        print(f"✅ SUCESSO: {framework_model} + {technique}")
        print(f"⏱️  Tempo de execução: {execution_time:.2f} segundos")
        
        # Exibe parte da saída
        if result.stdout:
            lines = result.stdout.split('\n')
            for line in lines[-10:]:  # Últimas 10 linhas
                if line.strip():
                    print(f"   {line}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ ERRO na execução: {framework_model} + {technique}")
        print(f"   Código de saída: {e.returncode}")
        if e.stderr:
            error_lines = e.stderr.split('\n')
            for line in error_lines[:5]:  # Primeiras 5 linhas de erro
                if line.strip():
                    print(f"   ERRO: {line}")
        return False

def generate_summary_report(results: dict):
    """
    Gera um relatório resumido dos resultados
    """
    print(f"\n{'#'*80}")
    print("# 📊 RELATÓRIO FINAL DE EXECUÇÃO")
    print(f"{'#'*80}")
    
    total_tests = len(MODELS) * len(TECHNIQUES)
    successful_tests = sum(sum(tech_results.values()) for tech_results in results.values())
    
    print(f"Total de combinações testadas: {total_tests}")
    print(f"Combinações bem-sucedidas: {successful_tests}")
    print(f"Combinações com erro: {total_tests - successful_tests}")
    
    print(f"\n📈 Detalhes por modelo:")
    for model_framework, model_ollama in MODELS.items():
        success_count = sum(results[model_framework].values())
        total_for_model = len(TECHNIQUES)
        print(f"   {model_framework}: {success_count}/{total_for_model} técnicas")
    
    print(f"\n📈 Detalhes por técnica:")
    for technique in TECHNIQUES:
        success_count = sum(results[model][technique] for model in MODELS.keys())
        total_for_technique = len(MODELS)
        print(f"   {technique}: {success_count}/{total_for_technique} modelos")

def main():
    """
    Função principal que orquestra todas as execuções
    """
    print("🤖 INICIANDO AUTOMAÇÃO DE TESTES DO FRAMEWORK")
    print(f"📁 Diretório de dados: data/")
    print(f"🔢 Total de modelos: {len(MODELS)}")
    print(f"🎯 Total de técnicas: {len(TECHNIQUES)}")
    print(f"🧪 Total de combinações: {len(MODELS) * len(TECHNIQUES)}")
    
    # Verifica se o main.py existe
    if not Path("main.py").exists():
        print("❌ ERRO: Arquivo main.py não encontrado!")
        sys.exit(1)
    
    # Verifica se o diretório de dados existe
    if not Path("data").exists():
        print("❌ ERRO: Diretório 'data' não encontrado!")
        sys.exit(1)
    
    # Dicionário para armazenar resultados
    results = {model: {tech: False for tech in TECHNIQUES} for model in MODELS.keys()}
    
    # Contadores
    total_combinations = len(MODELS) * len(TECHNIQUES)
    current_combination = 0
    
    # Executa todas as combinações
    for model_framework, model_ollama in MODELS.items():
        for technique in TECHNIQUES:
            current_combination += 1
            print(f"\n📊 Progresso: {current_combination}/{total_combinations}")
            
            # Executa o experimento
            success = run_experiment(model_framework, model_ollama, technique)
            results[model_framework][technique] = success
            
            # Pequena pausa entre execuções para não sobrecarregar
            time.sleep(2)
    
    # Gera relatório final
    generate_summary_report(results)
    
    # Salva resultados em arquivo JSON
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"execution_results_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados detalhados salvos em: {results_file}")
    print("🎉 Automação concluída!")

if __name__ == "__main__":
    main()