#!/bin/bash

# Script de teste para verificar se o container main.py funciona
set -e

echo "🧪 Testando container para experimentos main.py..."
echo ""

# Verificar se Ollama está rodando
echo "1. Verificando Ollama..."
if docker ps | grep -q "ollama/ollama"; then
    echo "✅ Container Ollama está rodando"
else
    echo "❌ Container Ollama não encontrado!"
    exit 1
fi

if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama está respondendo na porta 11434"
else
    echo "❌ Ollama não está respondendo!"
    exit 1
fi
echo ""

# Construir imagem
echo "2. Construindo imagem..."
docker build -f Dockerfile.main -t security-framework-main .
echo "✅ Imagem construída com sucesso"
echo ""

# Testar help do main.py
echo "3. Testando main.py --help..."
docker run --rm security-framework-main python main.py --help
echo "✅ main.py está funcionando"
echo ""

# Verificar estrutura de diretórios
echo "4. Verificando diretórios..."
if [ -d "data" ] && [ -n "$(ls -A data/*.xlsx 2>/dev/null)" ]; then
    echo "✅ Diretório data/ com arquivos Excel encontrado"
else
    echo "⚠️  Diretório data/ vazio ou sem arquivos Excel"
fi

if [ -d "config" ] && [ -f "config/default_config.json" ]; then
    echo "✅ Arquivo de configuração encontrado"
else
    echo "❌ Arquivo de configuração não encontrado!"
    exit 1
fi
echo ""

echo "✅ Teste concluído com sucesso!"
echo ""
echo "Agora você pode usar:"
echo "  ./run-main-experiment.sh --dry-run        # Ver comandos"
echo "  ./run-main-experiment.sh --list-models    # Ver modelos"
echo "  ./run-main-experiment.sh --single ollama_mistral_7b progressive_hint"
echo "  ./run-main-experiment.sh --full           # Experimento completo"