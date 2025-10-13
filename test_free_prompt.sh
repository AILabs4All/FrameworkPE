#!/bin/bash

# Script para testar o novo plugin FreePrompt
echo "=== Teste do Free Prompt Plugin ==="

# Ativar ambiente virtual
source env/bin/activate

# Testar com foundation_sec
echo "Testando Free Prompt com foundation_sec..."
python3 main.py data/ --columns "target" --model foundation_sec --technique free_prompt

echo "Teste do Free Prompt concluído!"