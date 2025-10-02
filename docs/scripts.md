# Scripts de Automação

## Visão Geral

O framework inclui scripts de automação que facilitam a execução e integração com diferentes ambientes. Estes scripts automatizam tarefas complexas como instalação de dependências, configuração de modelos locais e execução do pipeline completo de classificação.

## Índice de Scripts

1. [run_ollama_classification.sh](#run_ollama_classificationsh) - Automação completa para modelos Ollama
2. [create_framework.sh](#create_frameworksh) - Script de criação/inicialização do projeto
3. [Scripts de Desenvolvimento](#scripts-de-desenvolvimento) - Utilitários para desenvolvimento

---

## run_ollama_classification.sh

**Localização:** `scripts/run_ollama_classification.sh`

**Responsabilidade:** Automatiza todo o ciclo de vida de execução com modelos Ollama, incluindo instalação, configuração, download de modelos e execução da classificação.

### Funcionalidades

- ✅ **Instalação Automática do Ollama** (se não estiver presente)
- ✅ **Inicialização do Servidor Ollama** (se não estiver rodando)
- ✅ **Download Automático de Modelos** (se não estiverem disponíveis localmente)
- ✅ **Validação de Configuração** (lê e valida configurações JSON)
- ✅ **Limpeza Automática** (remove modelos e finaliza servidor se configurado)
- ✅ **Tratamento de Erros** (fallbacks e logs informativos)

### Sintaxe

```bash
./scripts/run_ollama_classification.sh <argumentos_do_main.py>
```

### Parâmetros

O script aceita todos os parâmetros do `main.py`, mas processa alguns especialmente:

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|-------------|-----------|---------|
| `input_dir` | ✅ | Diretório com arquivos de dados | `data/` |
| `--model` | ✅ | Nome do modelo configurado | `ollama_deepseek_15b` |
| `--columns` | ✅ | Colunas para classificação | `"Pedido,Descrição"` |
| `--technique` | ✅ | Técnica de prompt | `progressive_hint` |
| `--output` | ❌ | Formato de saída | `csv` (padrão) |
| `--config` | ❌ | Arquivo de configuração | `config/custom.json` |

### Exemplos de Uso

#### Exemplo Básico
```bash
./scripts/run_ollama_classification.sh data/ \
  --columns "Pedido" \
  --model ollama_deepseek_15b \
  --technique progressive_hint \
  --output csv
```

#### Exemplo com Configuração Personalizada
```bash
./scripts/run_ollama_classification.sh data/ \
  --columns "description,severity" \
  --model ollama_mistral \
  --technique self_hint \
  --output json \
  --config config/production.json
```

#### Exemplo com Parâmetros de Técnica
```bash
./scripts/run_ollama_classification.sh data/ \
  --columns "incident_text" \
  --model ollama_llama2 \
  --technique progressive_rectification \
  --output xlsx \
  --max_iter 5 \
  --limite_qualidade 0.95
```

### Variáveis de Ambiente

O script suporta as seguintes variáveis de ambiente:

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `PYTHON_BIN` | Caminho para Python | `python3` ou `python` |
| `OLLAMA_HOST` | Endpoint do Ollama | `http://localhost:11434` |
| `OLLAMA_KEEP_MODELS` | Manter modelos após execução | `0` (remove) |

#### Exemplos com Variáveis de Ambiente

```bash
# Usar Python personalizado
PYTHON_BIN=/usr/local/bin/python3.11 ./scripts/run_ollama_classification.sh data/ \
  --columns "text" --model ollama_deepseek_15b --technique progressive_hint

# Ollama remoto
OLLAMA_HOST=http://192.168.1.100:11434 ./scripts/run_ollama_classification.sh data/ \
  --columns "incident" --model ollama_mistral --technique self_hint

# Manter modelos baixados
OLLAMA_KEEP_MODELS=1 ./scripts/run_ollama_classification.sh data/ \
  --columns "description" --model ollama_llama2 --technique hypothesis_testing
```

### Fluxo de Execução Detalhado

#### 1. Validação Inicial
```bash
# Verifica se Python está disponível
if [[ -z "${PYTHON_BIN}" ]]; then
  echo "[ERROR] Python 3 não encontrado" >&2
  exit 1
fi

# Valida argumentos mínimos
if [[ $# -lt 1 ]]; then
  echo "Uso: $0 <args do main.py>" >&2
  exit 1
fi
```

#### 2. Parsing de Argumentos
```bash
# Extrai parâmetros específicos do script
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      MODEL_KEY="$2"
      shift 2
      ;;
    --config)
      if [[ "$2" = /* ]]; then
        CONFIG_PATH="$2"  # Caminho absoluto
      else
        CONFIG_PATH="${PROJECT_ROOT}/$2"  # Caminho relativo
      fi
      shift 2
      ;;
    --help|-h)
      "${PYTHON_BIN}" "${PROJECT_ROOT}/main.py" --help
      exit 0
      ;;
    *)
      shift
      ;;
  esac
done
```

#### 3. Validação de Configuração
```python
# Embedded Python script para validar configuração
CONFIG_OUTPUT="$(
  CONFIG_PATH="${CONFIG_PATH}" MODEL_KEY="${MODEL_KEY}" \
  "${PYTHON_BIN}" <<'PY'
import json
import os
import sys

config_path = os.environ["CONFIG_PATH"]
model_key = os.environ["MODEL_KEY"]

with open(config_path, "r", encoding="utf-8") as fh:
    data = json.load(fh)

model_cfg = data.get("models", {}).get(model_key)
if not model_cfg:
    print("::error::")
    sys.exit(0)

provider = model_cfg.get("provider", "")
model_name = model_cfg.get("model", "")
print(f"{provider}::{model_name}")
PY
)"
```

#### 4. Decisão de Execução

```bash
# Se não é Ollama, executa diretamente
if [[ "${PROVIDER}" != "ollama" ]]; then
  exec "${PYTHON_BIN}" "${PROJECT_ROOT}/main.py" "${ORIGINAL_ARGS[@]}"
fi

# Continua com setup Ollama...
```

#### 5. Instalação do Ollama (se necessário)

```bash
if ! command -v ollama >/dev/null 2>&1; then
  echo "[INFO] Ollama não encontrado. Instalando..."
  if ! command -v curl >/dev/null 2>&1; then
    echo "[ERROR] curl é necessário para instalar o Ollama" >&2
    exit 1
  fi
  curl -fsSL https://ollama.ai/install.sh | sh
fi
```

#### 6. Inicialização do Servidor

```bash
OLLAMA_ENDPOINT="${OLLAMA_HOST:-http://localhost:11434}"

if ! curl -sf "${OLLAMA_ENDPOINT}/api/version" >/dev/null 2>&1; then
  echo "[INFO] Iniciando serviço Ollama em background"
  ollama serve >/dev/null 2>&1 &
  OLLAMA_PID=$!
  sleep 2
  
  # Verifica se iniciou com sucesso
  if ! curl -sf "${OLLAMA_ENDPOINT}/api/version" >/dev/null 2>&1; then
    echo "[ERROR] Não foi possível iniciar o serviço Ollama" >&2
    exit 1
  fi
fi
```

#### 7. Download de Modelo

```bash
if ! ollama show "${OLLAMA_MODEL}" >/dev/null 2>&1; then
  echo "[INFO] Modelo ${OLLAMA_MODEL} não encontrado. Fazendo download..."
  ollama pull "${OLLAMA_MODEL}"
else
  echo "[INFO] Modelo ${OLLAMA_MODEL} encontrado localmente"
fi
```

#### 8. Execução do Framework

```bash
echo "[INFO] Executando classificação com ${MODEL_KEY} (${OLLAMA_MODEL})"
"${PYTHON_BIN}" "${PROJECT_ROOT}/main.py" "${ORIGINAL_ARGS[@]}"
```

#### 9. Limpeza (via trap)

```bash
cleanup() {
  local exit_code=$?
  
  # Finaliza servidor Ollama se foi iniciado pelo script
  if [[ -n "${OLLAMA_PID}" ]]; then
    kill "${OLLAMA_PID}" >/dev/null 2>&1 || true
  fi
  
  # Remove modelo se configurado
  if [[ ${REMOVE_MODEL} -eq 1 && -n "${OLLAMA_MODEL}" ]]; then
    ollama rm "${OLLAMA_MODEL}" >/dev/null 2>&1 || true
  fi
  
  exit "${exit_code}"
}

trap cleanup EXIT
```

### Troubleshooting

#### Problemas Comuns

**1. Erro: "Python 3 não encontrado"**
```bash
# Solução: Especificar caminho do Python
PYTHON_BIN=/usr/bin/python3 ./scripts/run_ollama_classification.sh data/ ...
```

**2. Erro: "curl é necessário para instalar o Ollama"**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install curl

# CentOS/RHEL
sudo yum install curl

# macOS
brew install curl
```

**3. Erro: "Não foi possível iniciar o serviço Ollama"**
```bash
# Verificar se porta 11434 está livre
sudo netstat -tulpn | grep 11434

# Usar porta alternativa
OLLAMA_HOST=http://localhost:11435 ./scripts/run_ollama_classification.sh ...
```

**4. Erro: "Modelo não encontrado na configuração"**
```bash
# Listar modelos disponíveis
python main.py --list-models

# Verificar configuração
cat config/default_config.json | jq '.models'
```

#### Logs e Debug

**Ativar logs detalhados:**
```bash
# Debug completo
set -x
./scripts/run_ollama_classification.sh data/ --columns "text" --model ollama_deepseek_15b --technique progressive_hint
set +x
```

**Verificar status Ollama:**
```bash
# Status do servidor
curl -s http://localhost:11434/api/version | jq

# Lista de modelos locais
ollama list

# Informações do modelo
ollama show deepseek-r1:1.5b
```

---

## create_framework.sh

**Localização:** `create_framework.sh`

**Responsabilidade:** Script de inicialização do projeto, criação de estrutura de pastas e configuração inicial.

### Funcionalidades

- 📁 **Criação de Estrutura** de pastas do projeto
- ⚙️ **Configuração Inicial** com templates
- 📦 **Instalação de Dependências** Python
- 🔧 **Configuração de Ambiente** (virtual env)

### Uso

```bash
# Execução básica
./create_framework.sh

# Com diretório personalizado
./create_framework.sh /path/to/project

# Com ambiente virtual
./create_framework.sh --venv myproject-env
```

---

## Scripts de Desenvolvimento

### validate_config.py

**Localização:** `scripts/validate_config.py`

Valida arquivos de configuração JSON/YAML.

```bash
# Validar configuração padrão
python scripts/validate_config.py config/default_config.json

# Validar configuração personalizada
python scripts/validate_config.py config/production.json --strict
```

### benchmark_models.py

**Localização:** `scripts/benchmark_models.py`

Compara performance entre diferentes modelos.

```bash
# Benchmark todos os modelos
python scripts/benchmark_models.py data/test_sample.csv

# Benchmark modelos específicos
python scripts/benchmark_models.py data/test_sample.csv \
  --models openai_gpt4,ollama_mistral,ollama_deepseek_15b \
  --techniques progressive_hint,self_hint
```

### export_results.py

**Localização:** `scripts/export_results.py`

Converte resultados entre formatos.

```bash
# CSV para Excel
python scripts/export_results.py results.csv --output results.xlsx

# JSON para CSV
python scripts/export_results.py results.json --output results.csv --format csv
```

### setup_docker.sh

**Localização:** `scripts/setup_docker.sh`

Configura ambiente Docker para o framework.

```bash
# Criar imagens Docker
./scripts/setup_docker.sh build

# Executar em container
./scripts/setup_docker.sh run data/ --columns "text" --model ollama_mistral
```

---

## Integração com CI/CD

### GitHub Actions

```yaml
# .github/workflows/classification.yml
name: Security Incident Classification

on:
  push:
    paths:
      - 'data/**'
  schedule:
    - cron: '0 6 * * *'  # Diário às 6h

jobs:
  classify:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run classification
      run: |
        ./scripts/run_ollama_classification.sh data/ \
          --columns "incident_description" \
          --model ollama_mistral \
          --technique progressive_hint \
          --output json
    
    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: classification-results
        path: output/
```

### Jenkins Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        PYTHON_BIN = '/usr/bin/python3'
        OLLAMA_KEEP_MODELS = '1'
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('Classify Incidents') {
            parallel {
                stage('Progressive Hint') {
                    steps {
                        sh '''
                            ./scripts/run_ollama_classification.sh data/ \
                              --columns "description" \
                              --model ollama_deepseek_15b \
                              --technique progressive_hint \
                              --output csv
                        '''
                    }
                }
                
                stage('Self Hint') {
                    steps {
                        sh '''
                            ./scripts/run_ollama_classification.sh data/ \
                              --columns "description" \
                              --model ollama_mistral \
                              --technique self_hint \
                              --output json
                        '''
                    }
                }
            }
        }
        
        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: 'output/**/*', fingerprint: true
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
```

---

## Customização de Scripts

### Criar Script Personalizado

```bash
#!/usr/bin/env bash
# scripts/custom_classification.sh

set -euo pipefail

# Configurações personalizadas
DEFAULT_MODEL="ollama_deepseek_15b"
DEFAULT_TECHNIQUE="progressive_hint"
DATA_DIR="data/incidents"
OUTPUT_DIR="results/$(date +%Y%m%d_%H%M%S)"

# Criar diretório de saída
mkdir -p "${OUTPUT_DIR}"

# Executar múltiplas classificações
for technique in progressive_hint self_hint progressive_rectification; do
    echo "[INFO] Executando técnica: ${technique}"
    
    ./scripts/run_ollama_classification.sh "${DATA_DIR}" \
        --columns "incident_text,severity" \
        --model "${DEFAULT_MODEL}" \
        --technique "${technique}" \
        --output json \
        --output-dir "${OUTPUT_DIR}/${technique}"
done

# Gerar relatório comparativo
python scripts/compare_techniques.py "${OUTPUT_DIR}" \
    --output "${OUTPUT_DIR}/comparison_report.html"

echo "[INFO] Classificação completa. Resultados em: ${OUTPUT_DIR}"
```

### Template de Script Base

```bash
#!/usr/bin/env bash
# Template para scripts personalizados

set -euo pipefail

# === CONFIGURATION ===
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python)}"

# === FUNCTIONS ===
log_info() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - $*"
}

log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
}

usage() {
    cat << EOF
Uso: $0 [OPTIONS]

OPTIONS:
    -h, --help          Mostra esta ajuda
    -c, --config PATH   Arquivo de configuração
    -o, --output DIR    Diretório de saída
    
EXAMPLES:
    $0 --config config/custom.json --output results/
EOF
}

# === ARGUMENT PARSING ===
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        *)
            log_error "Argumento desconhecido: $1"
            usage
            exit 1
            ;;
    esac
done

# === MAIN LOGIC ===
main() {
    log_info "Iniciando script personalizado"
    
    # Validações
    [[ -x "${PYTHON_BIN}" ]] || {
        log_error "Python não encontrado: ${PYTHON_BIN}"
        exit 1
    }
    
    # Lógica principal aqui
    log_info "Executando classificação..."
    
    log_info "Script concluído com sucesso"
}

# === EXECUTION ===
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

Os scripts de automação são essenciais para integração do framework em ambientes de produção, proporcionando execução confiável e consistente da classificação de incidentes de segurança.