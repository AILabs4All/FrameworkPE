#!/bin/bash

# Script de automação para execução de classificações com todos os modelos SLM
# Autor: Security Incident Framework Team
# Data: $(date +%Y-%m-%d)
#
# Uso: ./script.sh [--dry-run]
#   --dry-run: Mostra o que seria executado sem executar

set -e  # Parar execução em caso de erro

# Configurações
CONFIG_FILE="config/default_config.json"
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
NC='\033[0m' # No Color

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

# Verificar se arquivos necessários existem
check_prerequisites() {
    log_info "Verificando pré-requisitos..."
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log_error "Arquivo de configuração não encontrado: $CONFIG_FILE"
        exit 1
    fi
    
    if [[ ! -f "$RUN_SCRIPT" ]]; then
        log_error "Script de execução não encontrado: $RUN_SCRIPT"
        exit 1
    fi
    
    if [[ ! -d "$DATA_DIR" ]]; then
        log_error "Diretório de dados não encontrado: $DATA_DIR"
        exit 1
    fi
    
    # Verificar se jq está instalado para parsear JSON
    if ! command -v jq &> /dev/null; then
        log_error "jq não está instalado. Instale com: sudo apt-get install jq"
        exit 1
    fi
    
    # Tornar o script de execução executável
    chmod +x "$RUN_SCRIPT"
    
    log_success "Todos os pré-requisitos verificados"
}

# Extrair nomes dos modelos SLM (Small Language Models) do arquivo JSON
get_model_names() {
    log_info "Extraindo nomes dos modelos SLM de $CONFIG_FILE..." >&2
    
    # Extrair apenas modelos SLM (que começam com "ollama_") usando jq
    local models=$(jq -r '.models | keys[] | select(startswith("ollama_"))' "$CONFIG_FILE" 2>/dev/null)
    
    if [[ -z "$models" ]]; then
        log_error "Não foi possível extrair modelos SLM do arquivo JSON" >&2
        exit 1
    fi
    
    echo "$models"
}

# Executar classificação para um modelo e técnica específicos
run_classification() {
    local model="$1"
    local technique="$2"
    local dry_run="$3"
    
    log_info "Executando: Modelo=${model}, Técnica=${technique}"
    
    # Comando para executar
    local cmd="$RUN_SCRIPT $DATA_DIR --columns \"$DATA_COLUMNS\" --model $model --technique $technique --output $OUTPUT_FORMAT"
    
    echo "Comando: $cmd"
    
    # Se for dry run, apenas simular
    if [[ "$dry_run" == "true" ]]; then
        log_info "[DRY RUN] Simulando execução..."
        sleep 1
        log_success "[DRY RUN] Simulado: $model com $technique"
        return 0
    fi
    
    # Executar o comando
    if eval "$cmd"; then
        log_success "Concluído: $model com $technique"
        return 0
    else
        log_error "Falhou: $model com $technique"
        return 1
    fi
}

# Função principal
main() {
    # Verificar argumentos
    local dry_run=false
    if [[ "$1" == "--dry-run" ]]; then
        dry_run=true
        log_info "Modo DRY RUN ativado - nenhum comando será executado"
    fi
    
    echo "==============================================="
    echo "Security Incident Framework - Batch Runner"
    if [[ "$dry_run" == "true" ]]; then
        echo "                  [DRY RUN MODE]"
    fi
    echo "==============================================="
    echo ""
    
    # Verificar pré-requisitos
    check_prerequisites
    
    # Obter lista de modelos (capturar stderr para evitar poluição da saída)
    local models=$(get_model_names 2>/dev/null)
    local model_count=$(echo "$models" | wc -l)
    local technique_count=${#TECHNIQUES[@]}
    local total_executions=$((model_count * technique_count))
    
    log_info "Modelos SLM encontrados: $model_count"
    log_info "Técnicas configuradas: $technique_count"
    log_info "Total de execuções: $total_executions"
    
    # Estimativa de tempo (assumindo ~2-3 minutos por execução)
    local estimated_minutes=$((total_executions * 2))
    local estimated_hours=$((estimated_minutes / 60))
    local remaining_minutes=$((estimated_minutes % 60))
    
    if [[ "$dry_run" == "false" ]]; then
        log_info "Tempo estimado: ~${estimated_hours}h ${remaining_minutes}min (pode variar conforme modelo)"
    fi
    echo ""
    
    # Mostrar lista de modelos
    log_info "Modelos SLM que serão processados:"
    echo "$models" | sed 's/^/  - /'
    echo ""
    
    # Mostrar lista de técnicas
    log_info "Técnicas que serão executadas:"
    for technique in "${TECHNIQUES[@]}"; do
        echo "  - $technique"
    done
    echo ""
    
    # Confirmar execução
    read -p "Deseja continuar? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "Execução cancelada pelo usuário"
        exit 0
    fi
    
    # Contadores para estatísticas
    local success_count=0
    local error_count=0
    local current_execution=0
    
    echo ""
    log_info "Iniciando execuções em lote..."
    echo "================================================"
    
    # Loop através de todos os modelos
    while IFS= read -r model; do
        log_info "Processando modelo: $model"
        
        # Loop através de todas as técnicas
        for technique in "${TECHNIQUES[@]}"; do
            current_execution=$((current_execution + 1))
            
            echo ""
            echo "[$current_execution/$total_executions] $model + $technique"
            echo "------------------------------------------------"
            
            # Executar classificação
            if run_classification "$model" "$technique" "$dry_run"; then
                success_count=$((success_count + 1))
            else
                error_count=$((error_count + 1))
                log_warning "Continuando com próxima execução..."
            fi
            
            echo ""
            # Pequena pausa entre execuções
            sleep 2
        done
        
        echo "Modelo $model concluído"
        echo "================================================"
        
    done <<< "$models"
    
    # Relatório final
    echo ""
    echo "==============================================="
    echo "RELATÓRIO FINAL"
    echo "==============================================="
    log_info "Total de execuções: $total_executions"
    log_success "Sucessos: $success_count"
    if [[ $error_count -gt 0 ]]; then
        log_error "Erros: $error_count"
    else
        log_info "Erros: $error_count"
    fi
    echo ""
    
    if [[ $error_count -eq 0 ]]; then
        log_success "Todas as execuções foram concluídas com sucesso!"
    else
        log_warning "Algumas execuções falharam. Verifique os logs acima."
    fi
    
    echo ""
    log_info "Execução do lote finalizada"
}

# Tratar interrupções (Ctrl+C)
trap 'echo ""; log_warning "Execução interrompida pelo usuário"; exit 130' INT

# Executar função principal
main "$@"