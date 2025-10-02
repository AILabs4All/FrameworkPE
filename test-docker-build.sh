#!/bin/bash

# Script de teste para verificar se o Docker build funciona
set -e

echo "🧪 Testando build do Docker..."

# Testar apenas o build sem executar
docker compose build --no-cache framework

echo "✅ Build concluído com sucesso!"
echo ""
echo "Para executar o sistema completo:"
echo "  ./docker-helper.sh start"
echo "  ./docker-helper.sh setup-models"
echo "  ./docker-helper.sh run-experiment"