# 🧪 Experimento Automatizado - Docker Compose

Este é um Docker Compose específico para executar o **experimento completo do script.sh** de forma totalmente automatizada.

## 🎯 O que faz

Executa automaticamente:
- ✅ Inicializa o Ollama
- ✅ Baixa todos os 27 modelos SLM
- ✅ Executa o script.sh completo
- ✅ Gera resultados em ./results/
- ✅ Salva logs em ./logs/

## 🚀 Uso Rápido

### Opção 1: Script Automático (RECOMENDADO)

```bash
# Experimento completo
./run-experiment.sh

# Para máquinas limitadas
./run-experiment.sh --simple

# Apenas simulação
./run-experiment.sh --dry-run

# Apenas configurar modelos
./run-experiment.sh --setup-only
```

### Opção 2: Docker Compose Manual

```bash
# Versão padrão
docker compose -f docker-compose-experiment.yml up

# Versão simplificada (máquinas limitadas)
docker compose -f docker-compose-experiment-simple.yml up

# Apenas dry-run
docker compose -f docker-compose-experiment.yml --profile dry-run up
```

## 📋 Arquivos do Experimento

### Principais
- **`docker-compose-experiment.yml`** - Versão padrão (máquinas potentes)
- **`docker-compose-experiment-simple.yml`** - Versão simplificada (máquinas limitadas)
- **`run-experiment.sh`** - Script automático para controle total ⭐

### Fluxo de Execução
```
1. ollama          (inicializa servidor de modelos)
2. model-setup     (baixa todos os 27 modelos SLM)
3. experiment      (executa script.sh completo)
```

## 🔧 Comandos Disponíveis

```bash
# Iniciar experimento completo
./run-experiment.sh

# Modo simplificado (máquinas limitadas)
./run-experiment.sh --simple

# Apenas simular (dry-run)
./run-experiment.sh --dry-run
./run-experiment.sh --dry-run --simple

# Apenas configurar modelos
./run-experiment.sh --setup-only

# Ver logs em tempo real
./run-experiment.sh --logs
./run-experiment.sh --logs --simple

# Ver status
./run-experiment.sh --status

# Parar tudo
./run-experiment.sh --stop

# Limpar tudo (CUIDADO: remove modelos)
./run-experiment.sh --clean
```

## 📊 O que Acontece

### Passo 1: Inicialização (5-10 minutos)
- Baixa imagem Ollama
- Constrói container da aplicação
- Inicia servidor Ollama

### Passo 2: Configuração de Modelos (1-3 horas)
- Baixa automaticamente os 27 modelos SLM
- ~20GB+ de download
- Tempo varia com conexão de internet

### Passo 3: Experimento (4-8 horas)
- Executa script.sh automaticamente
- 108 classificações (27 modelos × 4 técnicas)
- Salva resultados automaticamente

## 📁 Estrutura de Resultados

```
results/
├── classification_results_YYYYMMDD_HHMMSS.xlsx
├── progressive_hint/
│   ├── ollama_mistral_7b_results.xlsx
│   └── ...
├── progressive_rectification/
├── self_hint/
└── hypothesis_testing/

logs/
├── framework_YYYYMMDD.log
├── experiment_execution.log
└── ollama_interactions.log
```

## 🔍 Monitoramento

### Ver Progresso em Tempo Real
```bash
# Logs gerais
./run-experiment.sh --logs

# Logs específicos
docker compose -f docker-compose-experiment.yml logs -f experiment
docker compose -f docker-compose-experiment.yml logs -f ollama
```

### Verificar Status
```bash
# Status dos containers
./run-experiment.sh --status

# Verificar se Ollama responde
curl http://localhost:11434/api/tags

# Verificar recursos
docker stats
```

## 🚨 Para Máquinas Limitadas

Se encontrar problemas de "unhealthy" ou timeout:

```bash
# Use SEMPRE a versão simplificada
./run-experiment.sh --simple

# Ou manualmente
docker compose -f docker-compose-experiment-simple.yml up
```

**Diferenças da versão simplificada:**
- Health checks mais tolerantes
- Timeouts maiores (10min start period)
- Aguarda mais tempo entre etapas
- Sem limitações de recursos

## ⚡ Dicas Importantes

1. **Primeira Execução**: Reserve 2-4 horas para download dos modelos
2. **Espaço em Disco**: Certifique-se de ter 50GB+ livres
3. **RAM**: Recomendado 16GB+ (8GB mínimo)
4. **Interrupção**: Use `Ctrl+C` ou `./run-experiment.sh --stop`
5. **Backup**: Faça backup da pasta `results/` regularmente

## 🎯 Comandos Essenciais

```bash
# Setup completo em um comando
./run-experiment.sh

# Para máquinas limitadas
./run-experiment.sh --simple

# Apenas testar sem executar
./run-experiment.sh --dry-run

# Acompanhar execução
./run-experiment.sh --logs
```

## 🛑 Parar e Limpar

```bash
# Parar experimento
./run-experiment.sh --stop

# Limpar tudo (CUIDADO: remove modelos!)
./run-experiment.sh --clean
```

---

## 💡 Resumo

Este Docker Compose automatiza completamente o experimento do script.sh:

- **🤖 Totalmente Automatizado**: Zero intervenção manual
- **📊 108 Classificações**: Todos os modelos e técnicas
- **💾 Resultados Organizados**: Salvos automaticamente
- **🔍 Logs Detalhados**: Para acompanhar progresso
- **🛡️ Duas Versões**: Normal e simplificada para máquinas limitadas

Execute `./run-experiment.sh` e deixe rodar! 🚀