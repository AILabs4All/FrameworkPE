#!/bin/bash

# Script de execução Docker para Security Incident Framework
# Versão adaptada do script.sh para uso em containers

set -e

# Configurações adaptadas para Docker
CONFIG_FILE="config/docker_config.json"
SCRIPT_DIR="scripts"
RUN_SCRIPT="$SCRIPT_DIR/run_ollama_classification.sh"
DATA_DIR="data/"
DATA_COLUMNS="target"
OUTPUT_FORMAT="xlsx"

# Técnicas de prompting disponíveis
TECHNIQUES=("progressive_hint" "progressive_rectification" "self_hint" "hypothesis_testing")

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Funções auxiliares
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

# Função para extrair nomes dos modelos SLM do arquivo de configuração
get_model_names() {
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "Arquivo de configuração não encontrado: $CONFIG_FILE"
        exit 1
    fi
    
    # Usar jq para extrair modelos que usam Ollama
    jq -r '.models | to_entries[] | select(.value.provider == "ollama") | .key' "$CONFIG_FILE" | sort
}

# Função para verificar pré-requisitos
check_prerequisites() {
    log_info "Verificando pré-requisitos..."
    
    # Verificar se jq está instalado
    if ! command -v jq &> /dev/null; then
        log_error "jq não está instalado. Instale com: apt-get install jq"
        exit 1
    fi
    
    # Verificar se o arquivo de configuração existe
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "Arquivo de configuração não encontrado: $CONFIG_FILE"
        exit 1
    fi
    
    # Verificar se o script de execução existe
    if [ ! -f "$RUN_SCRIPT" ]; then
        log_error "Script de execução não encontrado: $RUN_SCRIPT"
        exit 1
    fi
    
    # Verificar se o diretório de dados existe
    if [ ! -d "$DATA_DIR" ]; then
        log_error "Diretório de dados não encontrado: $DATA_DIR"
        exit 1
    fi
    
    # Verificar se Ollama está acessível
    if ! curl -sf "${OLLAMA_BASE_URL:-http://ollama:11434}/api/tags" > /dev/null 2>&1; then
        log_error "Ollama não está acessível. Verifique se o serviço está rodando."
        exit 1
    fi
    
    log_success "Todos os pré-requisitos verificados"
}

# Função para executar classificação com um modelo e técnica específicos
run_classification() {
    local model="$1"
    local technique="$2"
    local dry_run="$3"
    
    log_info "Executando: Modelo=$model, Técnica=$technique"
    
    # Comando para executar
    local cmd="$RUN_SCRIPT $DATA_DIR --columns \"$DATA_COLUMNS\" --model $model --technique $technique --output $OUTPUT_FORMAT --config $CONFIG_FILE"
    
    if [ "$dry_run" = "true" ]; then
        echo -e "${YELLOW}[DRY RUN]${NC} EXECUTARIA: $cmd"
        return 0
    fi
    
    # Executar o comando
    if eval "$cmd"; then
        log_success "Concluído: $model com $technique"
        return 0
    else
        log_error "Falha: $model com $technique"
        return 1
    fi
}

# Função principal
main() {
    local dry_run=false
    
    # Processar argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                dry_run=true
                shift
                ;;
            --help|-h)
                echo "Uso: $0 [--dry-run] [--help]"
                echo ""
                echo "Opções:"
                echo "  --dry-run    Mostra os comandos que seriam executados sem executar"
                echo "  --help, -h   Mostra esta mensagem de ajuda"
                exit 0
                ;;
            *)
                log_error "Opção desconhecida: $1"
                exit 1
                ;;
        esac
    done
    
    if [ "$dry_run" = "true" ]; then
        log_info "Modo DRY RUN ativado - nenhum comando será executado"
    fi
    
    # Header
    echo "==============================================="
    echo "Security Incident Framework - Batch Runner"
    if [ "$dry_run" = "true" ]; then
        echo "                  [DRY RUN MODE]"
    fi
    echo "==============================================="
    echo ""
    
    # Verificar pré-requisitos
    check_prerequisites
    
    # Obter lista de modelos
    local models
    models=$(get_model_names)
    local model_count=$(echo "$models" | wc -l)
    local technique_count=${#TECHNIQUES[@]}
    local total_executions=$((model_count * technique_count))
    
    log_info "Modelos SLM encontrados: $model_count"
    log_info "Técnicas configuradas: $technique_count"
    log_info "Total de execuções: $total_executions"
    echo ""
    
    # Listar modelos
    log_info "Modelos SLM que serão processados:"
    echo "$models" | while read -r model; do
        echo "  - $model"
    done
    echo ""
    
    # Listar técnicas
    log_info "Técnicas de prompting que serão utilizadas:"
    for technique in "${TECHNIQUES[@]}"; do
        echo "  - $technique"
    done
    echo ""
    
    # Confirmação antes de prosseguir (pular em dry-run)
    if [ "$dry_run" = "false" ]; then
        log_warning "Isso executará $total_executions classificações. Este processo pode levar várias horas."
        read -p "Deseja continuar? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Operação cancelada pelo usuário."
            exit 0
        fi
    fi
    
    # Executar todas as combinações
    local current_execution=0
    local success_count=0
    local start_time=$(date +%s)
    
    while read -r model; do
        for technique in "${TECHNIQUES[@]}"; do
            current_execution=$((current_execution + 1))
            
            log_info "[$current_execution/$total_executions] Processando: $model + $technique"
            
            if run_classification "$model" "$technique" "$dry_run"; then
                success_count=$((success_count + 1))
            fi
            
            # Mostrar progresso
            local progress=$((current_execution * 100 / total_executions))
            log_info "Progresso: $progress% ($success_count sucessos de $current_execution tentativas)"
            echo ""
        done
    done <<< "$models"
    
    # Resumo final
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo "==============================================="
    log_info "RESUMO DA EXECUÇÃO"
    echo "==============================================="
    log_success "Execuções bem-sucedidas: $success_count"
    log_info "Total de tentativas: $total_executions"
    log_info "Tempo total: ${duration}s"
    
    if [ "$dry_run" = "false" ]; then
        log_info "Resultados salvos em: results/"
        log_info "Logs disponíveis em: logs/"
    fi
    
    if [ $success_count -eq $total_executions ]; then
        log_success "Todas as execuções foram concluídas com sucesso!"
        exit 0
    else
        local failed_count=$((total_executions - success_count))
        log_warning "$failed_count execuções falharam"
        exit 1
    fi
}

# Executar função principal
main "$@"