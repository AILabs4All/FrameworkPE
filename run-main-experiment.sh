#!/bin/bash

# Script para executar experimentos usando main.py em container Docker
# Usa o container Ollama existente que já está rodando

set -e

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

# Verificar se Ollama está rodando
check_ollama() {
    if ! docker ps | grep -q "ollama/ollama"; then
        log_error "Container Ollama não está rodando!"
        log_info "Inicie o Ollama primeiro: docker run -d -p 11434:11434 --name ollama ollama/ollama"
        exit 1
    fi
    
    if ! curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
        log_error "Ollama não está respondendo na porta 11434!"
        exit 1
    fi
    
    log_success "Ollama está rodando e acessível"
}

# Construir imagem se necessário
build_image() {
    log_info "Construindo imagem do framework..."
    docker build -f Dockerfile.main -t security-framework-main .
    log_success "Imagem construída com sucesso"
}

# Executar um experimento específico
run_single_experiment() {
    local model="$1"
    local technique="$2"
    
    log_info "Executando: $model com $technique"
    
    docker run --rm \
        --network host \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/results:/app/results" \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/config:/app/config" \
        -e PYTHONPATH=/app \
        -e PYTHONUNBUFFERED=1 \
        -e OLLAMA_BASE_URL=http://localhost:11434 \
        security-framework-main \
        python main.py data/ --columns target --model "$model" --technique "$technique" --output xlsx
    
    if [ $? -eq 0 ]; then
        log_success "Experimento concluído: $model + $technique"
    else
        log_error "Falha no experimento: $model + $technique"
        return 1
    fi
}

# Executar experimento completo
run_full_experiment() {
    log_info "🚀 Iniciando Experimento Completo"
    echo "=================================="
    
    # Extrair modelos da configuração
    local models=$(docker run --rm \
        -v "$(pwd)/config:/app/config" \
        security-framework-main \
        jq -r '.models | to_entries[] | select(.value.provider == "ollama") | .key' /app/config/default_config.json | sort)
    
    local techniques=("progressive_hint" "progressive_rectification" "self_hint" "hypothesis_testing")
    
    local model_count=$(echo "$models" | wc -l)
    local technique_count=${#techniques[@]}
    local total_executions=$((model_count * technique_count))
    
    log_info "Modelos encontrados: $model_count"
    log_info "Técnicas: $technique_count"
    log_info "Total de execuções: $total_executions"
    echo ""
    
    log_warning "Isso executará $total_executions classificações e pode levar várias horas."
    read -p "Deseja continuar? (s/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        log_info "Experimento cancelado."
        exit 0
    fi
    
    local current=0
    local success=0
    local start_time=$(date +%s)
    
    # Executar todas as combinações
    while read -r model; do
        for technique in "${techniques[@]}"; do
            current=$((current + 1))
            log_info "[$current/$total_executions] Executando: $model + $technique"
            
            if run_single_experiment "$model" "$technique"; then
                success=$((success + 1))
            fi
            
            local progress=$((current * 100 / total_executions))
            log_info "Progresso: $progress% ($success sucessos de $current tentativas)"
            echo ""
        done
    done <<< "$models"
    
    # Resumo final
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo "=================================="
    log_info "RESUMO DO EXPERIMENTO"
    echo "=================================="
    log_success "Execuções bem-sucedidas: $success/$total_executions"
    log_info "Tempo total: ${duration}s"
    log_info "Resultados em: ./results/"
    log_info "Logs em: ./logs/"
}

# Executar dry-run
run_dry_run() {
    log_info "🧪 Simulação do Experimento (Dry Run)"
    echo "====================================="
    
    # Extrair modelos da configuração
    local models=$(docker run --rm \
        -v "$(pwd)/config:/app/config" \
        security-framework-main \
        jq -r '.models | to_entries[] | select(.value.provider == "ollama") | .key' /app/config/default_config.json | sort)
    
    local techniques=("progressive_hint" "progressive_rectification" "self_hint" "hypothesis_testing")
    
    local model_count=$(echo "$models" | wc -l)
    local technique_count=${#techniques[@]}
    local total_executions=$((model_count * technique_count))
    
    log_info "Comandos que seriam executados:"
    echo ""
    
    local current=0
    while read -r model; do
        for technique in "${techniques[@]}"; do
            current=$((current + 1))
            echo "[$current/$total_executions] python main.py data/ --columns target --model $model --technique $technique --output xlsx"
        done
    done <<< "$models"
    
    echo ""
    log_success "Simulação concluída! Total de $total_executions comandos seriam executados."
}

# Mostrar uso
show_usage() {
    echo "Uso: $0 [opções]"
    echo ""
    echo "Opções:"
    echo "  --full               Executar experimento completo (108 classificações)"
    echo "  --dry-run            Simular execução (mostrar comandos)"
    echo "  --single MODEL TECH  Executar experimento específico"
    echo "  --build              Apenas construir a imagem Docker"
    echo "  --list-models        Listar modelos disponíveis"
    echo "  --help, -h           Mostrar esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 --full"
    echo "  $0 --dry-run"
    echo "  $0 --single ollama_mistral_7b progressive_hint"
    echo "  $0 --list-models"
}

# Listar modelos disponíveis
list_models() {
    log_info "Modelos SLM disponíveis:"
    docker run --rm \
        -v "$(pwd)/config:/app/config" \
        security-framework-main \
        jq -r '.models | to_entries[] | select(.value.provider == "ollama") | "  - " + .key' /app/config/default_config.json
}

# Processamento dos argumentos
case "$1" in
    "--full")
        check_ollama
        build_image
        run_full_experiment
        ;;
    
    "--dry-run")
        build_image
        run_dry_run
        ;;
    
    "--single")
        if [ -z "$2" ] || [ -z "$3" ]; then
            log_error "Uso: $0 --single <modelo> <técnica>"
            exit 1
        fi
        check_ollama
        build_image
        run_single_experiment "$2" "$3"
        ;;
    
    "--build")
        build_image
        ;;
    
    "--list-models")
        build_image
        list_models
        ;;
    
    "--help"|"-h"|"")
        show_usage
        ;;
    
    *)
        log_error "Opção desconhecida: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac