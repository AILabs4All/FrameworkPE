#!/bin/bash

# Exemplos de uso do ZeroShotPlugin

echo "=========================================="
echo "EXEMPLOS DE USO DO ZEROSHOTPLUGIN"
echo "=========================================="

# Exemplo 1: Classificar 10 incidentes com deepseek-r1:1.5b
echo -e "\n1. Classificar 10 incidentes com deepseek-r1:1.5b"
echo "   Comando:"
echo "   python main.py data/10_incidentes.xlsx --columns target --model ollama_deepseek_15b --technique zeroshot --output xlsx"

# Exemplo 2: Classificar com qwen3:8b
echo -e "\n2. Classificar com qwen3:8b"
echo "   Comando:"
echo "   python main.py data/10_incidentes.xlsx --columns target --model ollama_qwen3_8b --technique zeroshot --output xlsx"

# Exemplo 3: Classificar com temperatura diferente
echo -e "\n3. Classificar com temperatura 0.7"
echo "   Comando:"
echo "   python main.py data/10_incidentes.xlsx --columns target --model ollama_deepseek_15b --technique zeroshot --temperature 0.7 --output xlsx"

# Exemplo 4: Classificar e salvar em CSV
echo -e "\n4. Salvar resultado em CSV"
echo "   Comando:"
echo "   python main.py data/10_incidentes.xlsx --columns target --model ollama_deepseek_15b --technique zeroshot --output csv"

# Exemplo 5: Comparar ZeroShot com outras técnicas
echo -e "\n5. Comparar ZeroShot com Free Prompt"
echo "   Comando para ZeroShot:"
echo "   python main.py data/10_incidentes.xlsx --columns target --model ollama_deepseek_15b --technique zeroshot --output xlsx"
echo "   Comando para Free Prompt:"
echo "   python main.py data/10_incidentes.xlsx --columns target --model ollama_deepseek_15b --technique free_prompt --output xlsx"

# Exemplo 6: Rodar todos os modelos com ZeroShot
echo -e "\n6. Rodar múltiplos modelos com ZeroShot"
echo "   Script:"
cat << 'EOF'
#!/bin/bash
MODELS=(
    "ollama_deepseek_15b"
    "ollama_qwen3_8b"
    "ollama_llama3_1_8b"
    "ollama_smollm2_360m"
)

for MODEL in "${MODELS[@]}"; do
    echo "Processando modelo: $MODEL"
    python main.py data/10_incidentes.xlsx \
        --columns target \
        --model $MODEL \
        --technique zeroshot \
        --output xlsx
done
EOF

echo -e "\n=========================================="
echo "Para executar os exemplos, copie e cole os comandos acima"
echo "=========================================="
