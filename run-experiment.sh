#!/bin/bash

# Script para executar experimento automatizado via Docker Compose
# Security Incident Framework - Experimento Completo

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

show_usage() {
    echo "Uso: $0 [opções]"
    echo ""
    echo "Opções:"
    echo "  --dry-run        Executar apenas simulação (não executa classificações)"
    echo "  --setup-only     Apenas configurar modelos e parar"
    echo "  --simple         Usar configuração simplificada (máquinas limitadas)"
    echo "  --logs           Mostrar logs em tempo real"
    echo "  --status         Verificar status dos serviços"
    echo "  --stop           Parar todos os serviços"
    echo "  --clean          Limpar containers e volumes"
    echo "  --help, -h       Mostrar esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0                    # Executar experimento completo"
    echo "  $0 --simple           # Executar em máquina limitada"
    echo "  $0 --dry-run          # Simular execução"
    echo "  $0 --dry-run --simple # Simular em máquina limitada"
    echo "  $0 --setup-only       # Apenas configurar modelos"
    echo "  $0 --logs --simple    # Acompanhar logs (versão simples)"
}

# Função para verificar se arquivo de dados existe
check_data_file() {
    if [ ! -d "data" ] || [ -z "$(ls -A data/*.xlsx 2>/dev/null)" ]; then
        log_error "Diretório 'data' não encontrado ou sem arquivos Excel!"
        log_info "Certifique-se de que existe um arquivo .xlsx no diretório 'data/'"
        exit 1
    fi
    log_success "Arquivo de dados encontrado em data/"
}

# Função para verificar pré-requisitos
check_prerequisites() {
    log_info "Verificando pré-requisitos..."
    
    # Verificar Docker Compose
    if ! command -v docker &> /dev/null; then
        log_error "Docker não está instalado!"
        exit 1
    fi
    
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose não está disponível!"
        exit 1
    fi
    
    # Verificar arquivos necessários
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Arquivo $COMPOSE_FILE não encontrado!"
        exit 1
    fi
    
    if [ ! -f "script.sh" ]; then
        log_error "Arquivo script.sh não encontrado!"
        exit 1
    fi
    
    check_data_file
    log_success "Todos os pré-requisitos verificados!"
}

# Função para executar experimento completo
run_experiment() {
    log_info "🚀 Iniciando Experimento Completo do Security Incident Framework"
    echo "=================================================================="
    echo ""
    
    log_warning "Este experimento executará 108 classificações (27 modelos × 4 técnicas)"
    log_warning "Tempo estimado: 4-8 horas dependendo da máquina"
    echo ""
    
    read -p "Deseja continuar? (s/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        log_info "Experimento cancelado pelo usuário."
        exit 0
    fi
    
    log_info "Iniciando serviços..."
    docker compose -f "$COMPOSE_FILE" up -d ollama
    
    if [ "$SIMPLE_MODE" = true ]; then
        log_info "Aguardando Ollama inicializar (modo simplificado, aguardando mais tempo)..."
        sleep 120
    else
        log_info "Aguardando Ollama inicializar..."
    fi
    
    docker compose -f "$COMPOSE_FILE" up model-setup
    
    log_info "Iniciando experimento principal..."
    log_info "Use 'docker compose -f $COMPOSE_FILE logs -f experiment' para acompanhar"
    
    docker compose -f "$COMPOSE_FILE" up experiment
    
    log_success "Experimento concluído!"
    log_info "Resultados disponíveis em: ./results/"
    log_info "Logs disponíveis em: ./logs/"
}

# Função para executar dry-run
run_dry_run() {
    log_info "🧪 Executando Simulação do Experimento (Dry Run)"
    echo "================================================="
    echo ""
    
    log_info "Iniciando serviços..."
    docker compose -f "$COMPOSE_FILE" up -d ollama
    
    if [ "$SIMPLE_MODE" = true ]; then
        log_info "Aguardando Ollama inicializar (modo simplificado)..."
        sleep 120
    else
        log_info "Aguardando Ollama inicializar..."
        sleep 30
    fi
    
    log_info "Executando simulação..."
    docker compose -f "$COMPOSE_FILE" --profile dry-run up experiment-dry-run
    
    log_success "Simulação concluída!"
}

# Função para apenas configurar modelos
setup_only() {
    log_info "🔧 Configurando Apenas os Modelos SLM"
    echo "====================================="
    echo ""
    
    log_info "Iniciando Ollama..."
    docker compose -f "$COMPOSE_FILE" up -d ollama
    
    if [ "$SIMPLE_MODE" = true ]; then
        log_info "Aguardando inicialização (modo simplificado)..."
        sleep 120
    fi
    
    log_info "Configurando modelos (isso pode levar 1-2 horas)..."
    docker compose -f "$COMPOSE_FILE" up model-setup
    
    log_success "Modelos configurados!"
    log_info "Execute '$0' para executar o experimento completo"
}

# Função para mostrar logs
show_logs() {
    log_info "📋 Mostrando logs dos serviços..."
    docker compose -f "$COMPOSE_FILE" logs -f
}

# Função para mostrar status
show_status() {
    log_info "📊 Status dos serviços:"
    docker compose -f "$COMPOSE_FILE" ps
    echo ""
    
    # Verificar se Ollama está respondendo
    if docker compose -f "$COMPOSE_FILE" exec ollama curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
        log_success "Ollama está funcionando corretamente"
    else
        log_warning "Ollama pode não estar respondendo adequadamente"
    fi
}

# Função para parar serviços
stop_services() {
    log_info "⏹️  Parando todos os serviços..."
    docker compose -f "$COMPOSE_FILE" down
    log_success "Serviços parados!"
}

# Função para limpeza
clean_all() {
    log_warning "🧹 Isso removerá TODOS os containers, volumes e modelos baixados!"
    log_warning "Você precisará baixar os modelos novamente (~20GB+)"
    echo ""
    read -p "Tem certeza? (s/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        log_info "Removendo containers e volumes..."
        docker compose -f "$COMPOSE_FILE" down -v
        # Limpar ambas as versões se existirem
        docker compose -f docker-compose-experiment.yml down -v 2>/dev/null || true
        docker compose -f docker-compose-experiment-simple.yml down -v 2>/dev/null || true
        docker system prune -f
        log_success "Limpeza concluída!"
    else
        log_info "Limpeza cancelada."
    fi
}

# Detectar modo simplificado
COMPOSE_FILE="docker-compose-experiment.yml"
SIMPLE_MODE=false

# Processar argumentos para detectar --simple
for arg in "$@"; do
    if [[ "$arg" == "--simple" ]]; then
        COMPOSE_FILE="docker-compose-experiment-simple.yml"
        SIMPLE_MODE=true
        log_info "🔧 Modo simplificado ativado (para máquinas limitadas)"
        break
    fi
done

# Processamento dos argumentos
case "$1" in
    "--dry-run")
        check_prerequisites
        run_dry_run
        ;;
    
    "--setup-only")
        check_prerequisites
        setup_only
        ;;
    
    "--logs")
        show_logs
        ;;
    
    "--status")
        show_status
        ;;
    
    "--stop")
        stop_services
        ;;
    
    "--clean")
        clean_all
        ;;
    
    "--help"|"-h")
        show_usage
        ;;
    
    "")
        check_prerequisites
        run_experiment
        ;;
    
    *)
        log_error "Opção desconhecida: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac