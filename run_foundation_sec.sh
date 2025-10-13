#!/bin/bash

# Comandos CLI para rodar o modelo foundation_sec com diferentes técnicas de prompt
# Baseado no padrão usado para ollama_smollm2_360m

echo "Iniciando experimentos com foundation_sec..."

# Progressive Hint
echo "Executando Progressive Hint..."
python3 main.py data/ --columns "target" --model foundation_sec --technique progressive_hint --output 'xlsx' &

# Self Hint
echo "Executando Self Hint..."
python3 main.py data/ --columns "target" --model foundation_sec --technique self_hint --output 'xlsx' &

# Progressive Rectification
echo "Executando Progressive Rectification..."
python3 main.py data/ --columns "target" --model foundation_sec --technique progressive_rectification --output 'xlsx' &

# Hypothesis Testing
echo "Executando Hypothesis Testing..."
python3 main.py data/ --columns "target" --model foundation_sec --technique hypothesis_testing --output 'xlsx' &

echo "Testando Free Prompt com foundation_sec..."
python3 main.py data/ --columns "target" --model foundation_sec --technique free_prompt --output 'xlsx'

# Aguardar todos os processos em background terminarem
wait

echo "Todos os experimentos com foundation_sec foram concluídos!"