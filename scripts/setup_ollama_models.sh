#!/bin/bash

# Script para configurar automaticamente todos os modelos Ollama
# necessários para o Security Incident Framework

set -e

# Configurações
OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-"http://ollama:11434"}
CONFIG_FILE="/app/config/default_config.json"
MAX_RETRIES=5
RETRY_DELAY=10

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se Ollama está disponível
wait_for_ollama() {
    log_info "Aguardando Ollama ficar disponível..."
    
    local retries=0
    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -sf "$OLLAMA_BASE_URL/api/tags" > /dev/null 2>&1; then
            log_success "Ollama está disponível!"
            return 0
        fi
        
        retries=$((retries + 1))
        log_warning "Tentativa $retries/$MAX_RETRIES falhou. Aguardando ${RETRY_DELAY}s..."
        sleep $RETRY_DELAY
    done
    
    log_error "Ollama não está disponível após $MAX_RETRIES tentativas"
    exit 1
}

# Extrair modelos do arquivo de configuração
get_ollama_models() {
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "Arquivo de configuração não encontrado: $CONFIG_FILE"
        exit 1
    fi
    
    # Extrair apenas modelos que usam Ollama
    jq -r '.models | to_entries[] | select(.value.provider == "ollama") | .value.model' "$CONFIG_FILE" | sort -u
}

# Baixar um modelo específico
pull_model() {
    local model_name="$1"
    log_info "Baixando modelo: $model_name"
    
    # Fazer requisição para pull do modelo
    local response=$(curl -s -X POST "$OLLAMA_BASE_URL/api/pull" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"$model_name\"}" 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        log_success "Modelo $model_name baixado com sucesso"
        return 0
    else
        log_error "Falha ao baixar modelo $model_name"
        return 1
    fi
}

# Verificar se modelo existe
model_exists() {
    local model_name="$1"
    curl -sf "$OLLAMA_BASE_URL/api/tags" | jq -r '.models[].name' | grep -q "^$model_name"
}

# Função principal
main() {
    log_info "=== Configuração de Modelos Ollama para Security Framework ==="
    log_info "Base URL: $OLLAMA_BASE_URL"
    
    # Aguardar Ollama ficar disponível
    wait_for_ollama
    
    # Obter lista de modelos necessários
    log_info "Extraindo modelos necessários do arquivo de configuração..."
    local models
    models=$(get_ollama_models)
    
    if [ -z "$models" ]; then
        log_warning "Nenhum modelo Ollama encontrado na configuração"
        exit 0
    fi
    
    local model_count=$(echo "$models" | wc -l)
    log_info "Encontrados $model_count modelos para configurar"
    
    # Listar modelos
    log_info "Modelos que serão configurados:"
    echo "$models" | while read -r model; do
        echo "  - $model"
    done
    
    # Baixar cada modelo
    local success_count=0
    local total_count=0
    
    while read -r model; do
        total_count=$((total_count + 1))
        
        log_info "Processando modelo $total_count/$model_count: $model"
        
        # Verificar se modelo já existe
        if model_exists "$model"; then
            log_success "Modelo $model já existe, pulando download"
            success_count=$((success_count + 1))
            continue
        fi
        
        # Tentar baixar modelo
        if pull_model "$model"; then
            success_count=$((success_count + 1))
        else
            log_error "Falha ao configurar modelo $model"
        fi
        
        # Pequena pausa entre downloads
        sleep 2
        
    done <<< "$models"
    
    # Resumo final
    log_info "=== Resumo da Configuração ==="
    log_success "Modelos configurados com sucesso: $success_count/$total_count"
    
    if [ $success_count -eq $total_count ]; then
        log_success "Todos os modelos foram configurados com sucesso!"
        exit 0
    else
        log_error "Alguns modelos falharam na configuração"
        exit 1
    fi
}

# Executar função principal
main "$@"