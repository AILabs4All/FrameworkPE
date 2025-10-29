#!/bin/bash

# Script para baixar todos os modelos listados na imagem
echo "Iniciando download de todos os modelos..."

# Array com todos os modelos
models=(
    "mistral:7b"
    "falcon3:7b" 
    "falcon3:10b"
    "gpt-oss:20b"
    "phi4:14b"
    "deepseek-r1:7b"
    "deepseek-r1:8b"
    "deepseek-r1:14b"
    "gemma2:9b"
    "granite3.2:8b"
    "huihui_ai/foundation-sec-abliterated:8b"
    "llama3.1:8b"
    "deepseek-r1:32b"
    "deepseek-r1:70b"
    "cogito:32b"
    "cogito:70b"
    "llama3.3:70b"
    "qwen3:32b"
)

# Contadores para estatísticas
total=${#models[@]}
current=0
success=0
fail=0

echo "Total de modelos para baixar: $total"
echo "======================================"

# Função para baixar cada modelo
download_model() {
    local model=$1
    local count=$2
    local total=$3
    
    echo "[$count/$total] Baixando $model..."
    
    if docker exec ollama ollama pull "$model"; then
        echo "✅ $model baixado com sucesso!"
        ((success++))
    else
        echo "❌ Falha ao baixar $model"
        ((fail++))
    fi
    
    echo "--------------------------------------"
}

# Baixar cada modelo
for model in "${models[@]}"; do
    ((current++))
    download_model "$model" "$current" "$total"
    
    # Pequena pausa entre downloads para evitar sobrecarga
    sleep 2
done

# Relatório final
echo "======================================"
echo "DOWNLOAD FINALIZADO!"
echo "Modelos baixados com sucesso: $success"
echo "Modelos com falha: $fail"
echo "Total processado: $total"

if [ $fail -eq 0 ]; then
    echo "🎉 Todos os modelos foram baixados com sucesso!"
else
    echo "⚠️  Alguns modelos falharam. Verifique as mensagens acima."
fi