#!/bin/bash

# Script auxiliar para facilitar o uso do Docker Compose
# Security Incident Framework

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
    echo "Uso: $0 <comando> [opções]"
    echo ""
    echo "Comandos disponíveis:"
    echo "  start          - Iniciar todos os serviços"
    echo "  stop           - Parar todos os serviços"
    echo "  restart        - Reiniciar todos os serviços"
    echo "  status         - Verificar status dos serviços"
    echo "  setup-models   - Configurar modelos Ollama"
    echo "  run-experiment - Executar experimento completo"
    echo "  dry-run        - Executar em modo dry-run (apenas visualizar)"
    echo "  logs           - Mostrar logs dos serviços"
    echo "  clean          - Limpar containers e volumes"
    echo "  shell          - Abrir shell no container da aplicação"
    echo ""
    echo "Exemplos:"
    echo "  $0 start"
    echo "  $0 setup-models"
    echo "  $0 run-experiment"
    echo "  $0 logs framework"
    echo "  $0 clean"
}

case "$1" in
    "start")
        log_info "Iniciando serviços..."
        docker compose up -d
        log_success "Serviços iniciados!"
        ;;
    
    "stop")
        log_info "Parando serviços..."
        docker compose down
        log_success "Serviços parados!"
        ;;
    
    "restart")
        log_info "Reiniciando serviços..."
        docker compose down
        docker compose up -d
        log_success "Serviços reiniciados!"
        ;;
    
    "status")
        log_info "Status dos serviços:"
        docker compose ps
        ;;
    
    "setup-models")
        log_info "Configurando modelos Ollama..."
        docker compose run --rm model-setup
        log_success "Modelos configurados!"
        ;;
    
    "run-experiment")
        log_info "Executando experimento completo..."
        log_warning "Isso pode levar várias horas. Use Ctrl+C para cancelar."
        docker compose run --rm framework ./docker-script.sh
        ;;
    
    "dry-run")
        log_info "Executando dry-run do experimento..."
        docker compose run --rm framework ./docker-script.sh --dry-run
        ;;
    
    "logs")
        service=${2:-""}
        if [ -n "$service" ]; then
            log_info "Mostrando logs do serviço: $service"
            docker compose logs -f "$service"
        else
            log_info "Mostrando logs de todos os serviços:"
            docker compose logs -f
        fi
        ;;
    
    "clean")
        log_warning "Isso removerá todos os containers e volumes. Deseja continuar? (y/N)"
        read -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Limpando containers e volumes..."
            docker compose down -v
            docker system prune -f
            log_success "Limpeza concluída!"
        else
            log_info "Operação cancelada."
        fi
        ;;
    
    "shell")
        log_info "Abrindo shell no container da aplicação..."
        docker compose run --rm framework bash
        ;;
    
    "help"|"--help"|"-h"|"")
        show_usage
        ;;
    
    *)
        log_error "Comando desconhecido: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac