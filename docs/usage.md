# Guia de Uso Completo

## Pré-requisitos

### Requisitos de Sistema

| Componente | Versão Mínima | Recomendada | Observações |
|------------|---------------|-------------|-------------|
| **Python** | 3.8+ | 3.11+ | Necessário para execução do framework |
| **pip** | 21.0+ | Última | Gerenciador de pacotes Python |
| **Sistema Operacional** | Linux/macOS/Windows | Ubuntu 22.04+ | Testado principalmente em Linux |
| **RAM** | 4GB | 8GB+ | Depende do modelo usado |
| **Armazenamento** | 2GB | 10GB+ | Para modelos locais |

### Dependências Externas (Opcionais)

| Ferramenta | Uso | Instalação |
|------------|-----|------------|
| **Ollama** | Modelos locais | Instalação automática via script |
| **Docker** | Containerização | `docker.com` |
| **curl** | Downloads e APIs | Geralmente pré-instalado |
| **git** | Controle de versão | `git-scm.com` |

## Instalação

### 1. Instalação Básica

#### Clone do Repositório
```bash
# Via HTTPS
git clone https://github.com/seu-usuario/security-incident-framework.git
cd security-incident-framework

# Via SSH (se configurado)
git clone git@github.com:seu-usuario/security-incident-framework.git
cd security-incident-framework
```

#### Ambiente Virtual (Recomendado)
```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
# Linux/macOS:
source venv/bin/activate

# Windows:
# venv\Scripts\activate

# Verificar ativação
which python  # Deve mostrar o caminho do venv
```

#### Instalar Dependências
```bash
# Instalar dependências principais
pip install -r requirements.txt

# Verificar instalação
python -c "import litellm, pandas, tqdm; print('Dependências OK!')"
```

### 2. Instalação com Docker

#### Dockerfile Básico
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python  
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do framework
COPY . .

# Tornar scripts executáveis
RUN chmod +x scripts/*.sh

EXPOSE 8000
CMD ["python", "main.py", "--help"]
```

#### Build e Execução
```bash
# Build da imagem
docker build -t security-framework .

# Execução básica
docker run --rm security-framework python main.py --list-models

# Execução com volumes
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  security-framework \
  python main.py data/ --columns "text" --model openai_gpt35 --technique progressive_hint
```

### 3. Configuração de APIs

#### OpenAI
```bash
# Definir API key
export OPENAI_API_KEY="sk-your-api-key-here"

# Verificar configuração
python -c "import os; print('OpenAI configurado!' if os.getenv('OPENAI_API_KEY') else 'API key não encontrada')"
```

#### HuggingFace
```bash
# Definir API key
export HUGGINGFACE_API_KEY="hf_your-token-here"

# Verificar configuração
python -c "import os; print('HuggingFace configurado!' if os.getenv('HUGGINGFACE_API_KEY') else 'Token não encontrado')"
```

#### Configuração Persistente
```bash
# Adicionar ao .bashrc/.zshrc
echo 'export OPENAI_API_KEY="sk-your-key"' >> ~/.bashrc
echo 'export HUGGINGFACE_API_KEY="hf_your-token"' >> ~/.bashrc

# Recarregar shell
source ~/.bashrc
```

## Configuração

### Arquivo de Configuração Principal

O arquivo `config/default_config.json` controla todo o comportamento do framework:

```json
{
  "framework": {
    "name": "Security Incident Classification Framework",
    "version": "2.0.0",
    "description": "Framework pluginável para classificação de incidentes"
  },
  "logging": {
    "level": "INFO",
    "log_dir": "logs",
    "enable_console": true,
    "enable_file": true
  },
  "models": {
    "openai_gpt4": {
      "plugin": "APIModel",
      "provider": "openai",
      "model": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 2000,
      "api_key": "${OPENAI_API_KEY}",
      "base_url": null
    },
    "ollama_deepseek": {
      "plugin": "LocalModel", 
      "provider": "ollama",
      "model": "deepseek-r1:1.5b",
      "temperature": 0.7,
      "max_tokens": 2000,
      "base_url": "http://localhost:11434"
    }
  },
  "prompt_techniques": {
    "progressive_hint": {
      "plugin": "ProgressiveHintPlugin",
      "description": "Progressive Hint Prompting",
      "default_params": {
        "max_hints": 4,
        "limite_rouge": 0.9
      }
    }
  },
  "nist_categories": {
    "enabled": true,
    "categories": {
      "CAT1": {
        "name": "Account Compromise",
        "description": "unauthorized access to user or administrator accounts"
      }
      // ... outras categorias
    }
  },
  "output": {
    "formats": ["csv", "json", "xlsx"],
    "default_format": "csv",
    "include_metadata": true,
    "include_timestamps": true
  }
}
```

### Configurações Personalizadas

#### Criar Configuração de Produção
```bash
# Copiar configuração base
cp config/default_config.json config/production.json

# Editar configurações específicas
vim config/production.json
```

#### Exemplo de Configuração Customizada
```json
{
  "framework": {
    "name": "Production Security Framework",
    "version": "2.0.0"
  },
  "logging": {
    "level": "WARNING",
    "log_dir": "/var/log/security-framework",
    "enable_console": false,
    "enable_file": true
  },
  "models": {
    "production_gpt4": {
      "plugin": "APIModel",
      "provider": "openai", 
      "model": "gpt-4-turbo",
      "temperature": 0.3,
      "max_tokens": 1500,
      "api_key": "${OPENAI_PRODUCTION_KEY}",
      "rate_limit": 2.0
    }
  },
  "output": {
    "default_format": "json",
    "include_metadata": true,
    "include_timestamps": true
  },
  "performance": {
    "rate_limiting": {
      "api_models": 2.0,
      "local_models": 0.2
    },
    "memory_monitoring": true,
    "token_tracking": true
  }
}
```

## Preparação de Dados

### Formatos Suportados

#### CSV
```csv
id,description,severity,timestamp
1,"Suspicious login attempt from unknown IP",High,2024-01-15 10:30:00
2,"Malware detected on workstation",Critical,2024-01-15 11:45:00
3,"Failed authentication attempts",Medium,2024-01-15 12:15:00
```

#### JSON
```json
[
  {
    "id": 1,
    "description": "Suspicious login attempt from unknown IP",
    "severity": "High",
    "timestamp": "2024-01-15 10:30:00"
  },
  {
    "id": 2, 
    "description": "Malware detected on workstation",
    "severity": "Critical",
    "timestamp": "2024-01-15 11:45:00"
  }
]
```

#### Excel (XLSX)
- Suporta múltiplas abas
- Primeira linha deve conter cabeçalhos
- Encoding automático

### Estrutura de Dados Recomendada

#### Colunas Essenciais
| Coluna | Tipo | Obrigatória | Descrição |
|--------|------|-------------|-----------|
| `id` | String/Integer | Não | Identificador único |
| `description` | String | Sim | Descrição do incidente |
| `timestamp` | String | Não | Data/hora do incidente |
| `severity` | String | Não | Severidade (Low/Medium/High/Critical) |
| `source` | String | Não | Fonte do incidente |

#### Exemplo de Estrutura Completa
```csv
id,incident_title,incident_description,severity,source,timestamp,affected_systems,initial_classification
INC001,"Malware Detection","Antivirus detected malware on employee workstation",High,"Security Team","2024-01-15 10:30:00","WKS-001","Malware"
INC002,"Failed Logins","Multiple failed login attempts detected",Medium,"SIEM","2024-01-15 11:45:00","AD-SERVER","Account Compromise"
```

### Validação de Dados

#### Script de Validação
```python
# scripts/validate_data.py
import pandas as pd
import sys
from pathlib import Path

def validate_data_file(file_path):
    """Valida arquivo de dados."""
    try:
        # Carrega arquivo
        if file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
        elif file_path.suffix.lower() == '.json':
            df = pd.read_json(file_path)
        elif file_path.suffix.lower() == '.xlsx':
            df = pd.read_excel(file_path)
        else:
            print(f"❌ Formato não suportado: {file_path.suffix}")
            return False
        
        # Validações básicas
        if df.empty:
            print(f"❌ Arquivo vazio: {file_path}")
            return False
            
        print(f"✅ Arquivo carregado: {len(df)} linhas, {len(df.columns)} colunas")
        print(f"📊 Colunas: {list(df.columns)}")
        
        # Verifica colunas com texto
        text_columns = df.select_dtypes(include=['object']).columns
        if len(text_columns) == 0:
            print("⚠️  Nenhuma coluna de texto encontrada")
            
        # Verifica valores nulos
        null_counts = df.isnull().sum()
        if null_counts.any():
            print("⚠️  Valores nulos encontrados:")
            for col, count in null_counts[null_counts > 0].items():
                print(f"   {col}: {count} valores nulos")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao processar {file_path}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python validate_data.py <arquivo_ou_diretorio>")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    
    if path.is_file():
        validate_data_file(path)
    elif path.is_dir():
        for file_path in path.glob("*"):
            if file_path.suffix.lower() in ['.csv', '.json', '.xlsx']:
                print(f"\n--- Validando {file_path.name} ---")
                validate_data_file(file_path)
    else:
        print(f"❌ Caminho não encontrado: {path}")
```

## Execução

### 1. Usando o Script Python Diretamente

#### Comando Básico
```bash
python main.py data/ \
  --columns "description" \
  --model openai_gpt35 \
  --technique progressive_hint \
  --output csv
```

#### Parâmetros Principais

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|-------------|-----------|---------|
| `input_dir` | ✅ | Diretório com dados | `data/` |
| `--columns` | ✅ | Colunas para análise | `"description,details"` |
| `--model` | ✅ | Modelo configurado | `openai_gpt4` |
| `--technique` | ✅ | Técnica de prompt | `progressive_hint` |
| `--output` | ❌ | Formato de saída | `csv` (padrão) |
| `--config` | ❌ | Arquivo de configuração | `config/custom.json` |
| `--output-dir` | ❌ | Diretório de saída | `results/` |

#### Exemplos Avançados

**Múltiplas Colunas:**
```bash
python main.py data/ \
  --columns "incident_title,incident_description,severity" \
  --model openai_gpt4 \
  --technique self_hint \
  --output json \
  --max_iter 5
```

**Configuração Personalizada:**
```bash
python main.py data/ \
  --columns "text" \
  --model production_gpt4 \
  --technique progressive_rectification \
  --config config/production.json \
  --output xlsx \
  --output-dir results/production/
```

**Com Parâmetros de Técnica:**
```bash
python main.py data/ \
  --columns "description" \
  --model openai_gpt35 \
  --technique progressive_hint \
  --output csv \
  --max_hints 6 \
  --limite_rouge 0.95
```

### 2. Usando Scripts de Automação

#### Script Ollama (Recomendado para Modelos Locais)
```bash
# Execução básica
./scripts/run_ollama_classification.sh data/ \
  --columns "description" \
  --model ollama_deepseek_15b \
  --technique progressive_hint \
  --output csv

# Com variáveis de ambiente
OLLAMA_KEEP_MODELS=1 PYTHON_BIN=/usr/bin/python3.11 \
./scripts/run_ollama_classification.sh data/ \
  --columns "incident_text" \
  --model ollama_mistral \
  --technique self_hint \
  --output json
```

### 3. Execução em Lote

#### Script de Lote Personalizado
```bash
#!/bin/bash
# scripts/batch_classification.sh

set -euo pipefail

DATA_DIR="data/incidents"
OUTPUT_BASE="results/$(date +%Y%m%d_%H%M%S)"
MODELS=("openai_gpt35" "openai_gpt4" "ollama_deepseek_15b")
TECHNIQUES=("progressive_hint" "self_hint" "progressive_rectification")

mkdir -p "${OUTPUT_BASE}"

# Matriz de execuções
for model in "${MODELS[@]}"; do
  for technique in "${TECHNIQUES[@]}"; do
    echo "[INFO] Executando: ${model} + ${technique}"
    
    output_dir="${OUTPUT_BASE}/${model}_${technique}"
    mkdir -p "${output_dir}"
    
    if [[ "${model}" == ollama_* ]]; then
      # Usar script Ollama
      OLLAMA_KEEP_MODELS=1 ./scripts/run_ollama_classification.sh \
        "${DATA_DIR}" \
        --columns "description,severity" \
        --model "${model}" \
        --technique "${technique}" \
        --output json \
        --output-dir "${output_dir}"
    else
      # Usar execução direta
      python main.py "${DATA_DIR}" \
        --columns "description,severity" \
        --model "${model}" \
        --technique "${technique}" \
        --output json \
        --output-dir "${output_dir}"
    fi
    
    echo "[INFO] Concluído: ${model} + ${technique}"
    sleep 2  # Pausa entre execuções
  done
done

echo "[INFO] Execução em lote concluída. Resultados em: ${OUTPUT_BASE}"
```

## Exemplos Práticos

### Exemplo 1: Classificação Básica

**Cenário:** Classificar incidentes simples com OpenAI GPT-3.5

```bash
# 1. Preparar dados
cat > data/sample.csv << EOF
id,description
1,"User reported suspicious email with attachment"
2,"Multiple failed login attempts from external IP"
3,"Unauthorized access to file server detected"
4,"Malware alert triggered on workstation"
EOF

# 2. Executar classificação
python main.py data/ \
  --columns "description" \
  --model openai_gpt35 \
  --technique progressive_hint \
  --output csv

# 3. Verificar resultados
ls -la output/
head output/classification_results_*.csv
```

### Exemplo 2: Análise Comparativa

**Cenário:** Comparar diferentes técnicas de prompt no mesmo dataset

```bash
#!/bin/bash
# Análise comparativa de técnicas

DATA_FILE="data/incidents_sample.csv"
OUTPUT_DIR="results/comparison_$(date +%Y%m%d)"
MODEL="openai_gpt4"

mkdir -p "${OUTPUT_DIR}"

# Técnicas a comparar
techniques=("progressive_hint" "self_hint" "progressive_rectification" "hypothesis_testing" "free_prompt")

for technique in "${techniques[@]}"; do
  echo "=== Testando técnica: ${technique} ==="
  
  python main.py data/ \
    --columns "incident_description" \
    --model "${MODEL}" \
    --technique "${technique}" \
    --output json \
    --output-dir "${OUTPUT_DIR}/${technique}" \
    2>&1 | tee "${OUTPUT_DIR}/${technique}/execution.log"
  
  echo "Técnica ${technique} concluída"
  echo ""
done

# Gerar relatório comparativo
python scripts/compare_results.py "${OUTPUT_DIR}" \
  --output "${OUTPUT_DIR}/comparison_report.html"

echo "Análise comparativa concluída!"
echo "Relatório disponível em: ${OUTPUT_DIR}/comparison_report.html"
```

### Exemplo 3: Pipeline de Produção

**Cenário:** Pipeline automatizado para ambiente de produção

```bash
#!/bin/bash
# scripts/production_pipeline.sh

set -euo pipefail

# Configurações
PROD_CONFIG="config/production.json"
DATA_SOURCE="/data/security_incidents"
OUTPUT_BASE="/results/production"
BACKUP_DIR="/backup/security_framework"
LOG_FILE="/var/log/security-framework/pipeline.log"

# Função de log
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}"
}

# Validação inicial
log "INFO: Iniciando pipeline de produção"

# Verificar dados de entrada
if [[ ! -d "${DATA_SOURCE}" ]]; then
  log "ERROR: Diretório de dados não encontrado: ${DATA_SOURCE}"
  exit 1
fi

# Criar diretórios
OUTPUT_DIR="${OUTPUT_BASE}/$(date +%Y%m%d_%H%M%S)"
mkdir -p "${OUTPUT_DIR}" "${BACKUP_DIR}"

# Backup da configuração
cp "${PROD_CONFIG}" "${BACKUP_DIR}/config_$(date +%Y%m%d_%H%M%S).json"

# Validar dados
log "INFO: Validando dados de entrada"
python scripts/validate_data.py "${DATA_SOURCE}" >> "${LOG_FILE}" 2>&1

# Executar classificação principal
log "INFO: Executando classificação principal"
python main.py "${DATA_SOURCE}" \
  --columns "incident_description,severity,source" \
  --model production_gpt4 \
  --technique progressive_hint \
  --config "${PROD_CONFIG}" \
  --output json \
  --output-dir "${OUTPUT_DIR}/primary" \
  >> "${LOG_FILE}" 2>&1

# Executar classificação de backup
log "INFO: Executando classificação de backup"
OLLAMA_KEEP_MODELS=1 ./scripts/run_ollama_classification.sh \
  "${DATA_SOURCE}" \
  --columns "incident_description,severity,source" \
  --model ollama_deepseek_15b \
  --technique self_hint \
  --config "${PROD_CONFIG}" \
  --output json \
  --output-dir "${OUTPUT_DIR}/backup" \
  >> "${LOG_FILE}" 2>&1

# Gerar relatórios
log "INFO: Gerando relatórios"
python scripts/generate_report.py "${OUTPUT_DIR}" \
  --format html \
  --output "${OUTPUT_DIR}/executive_report.html" \
  >> "${LOG_FILE}" 2>&1

# Notificação (webhook, email, etc.)
log "INFO: Enviando notificações"
curl -X POST "${WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d "{\"status\": \"completed\", \"output_dir\": \"${OUTPUT_DIR}\"}" \
  >> "${LOG_FILE}" 2>&1

log "INFO: Pipeline de produção concluído com sucesso"
log "INFO: Resultados disponíveis em: ${OUTPUT_DIR}"
```

### Exemplo 4: Processamento Incremental

**Cenário:** Processar apenas novos incidentes desde a última execução

```bash
#!/bin/bash
# scripts/incremental_processing.sh

set -euo pipefail

STATE_FILE="/var/lib/security-framework/last_processed.txt"
DATA_DIR="data/incidents"
OUTPUT_DIR="results/incremental"

# Obter timestamp da última execução
if [[ -f "${STATE_FILE}" ]]; then
  LAST_PROCESSED=$(cat "${STATE_FILE}")
  echo "[INFO] Última execução: ${LAST_PROCESSED}"
else
  LAST_PROCESSED="1970-01-01 00:00:00"
  echo "[INFO] Primeira execução"
fi

# Encontrar arquivos novos/modificados
NEW_FILES=$(find "${DATA_DIR}" -type f \
  \( -name "*.csv" -o -name "*.json" -o -name "*.xlsx" \) \
  -newer "${STATE_FILE}" 2>/dev/null || find "${DATA_DIR}" -type f \
  \( -name "*.csv" -o -name "*.json" -o -name "*.xlsx" \))

if [[ -z "${NEW_FILES}" ]]; then
  echo "[INFO] Nenhum arquivo novo encontrado"
  exit 0
fi

echo "[INFO] Arquivos a processar:"
echo "${NEW_FILES}"

# Criar diretório temporário
TEMP_DIR=$(mktemp -d)
trap "rm -rf ${TEMP_DIR}" EXIT

# Copiar apenas arquivos novos
echo "${NEW_FILES}" | while read -r file; do
  cp "${file}" "${TEMP_DIR}/"
done

# Processar arquivos novos
python main.py "${TEMP_DIR}" \
  --columns "description,severity" \
  --model openai_gpt4 \
  --technique progressive_hint \
  --output csv \
  --output-dir "${OUTPUT_DIR}/$(date +%Y%m%d_%H%M%S)"

# Atualizar timestamp
date '+%Y-%m-%d %H:%M:%S' > "${STATE_FILE}"

echo "[INFO] Processamento incremental concluído"
```

## Interpretação de Resultados

### Formato de Saída CSV
```csv
informacoes_das_colunas,categoria,explicacao,confianca,tecnica,timestamp,erro
"description: Malware detected on workstation",CAT2,"This incident involves malware detection which falls under category CAT2 - Malware infection",0.95,progressive_hint,2024-01-15 14:30:22,False
"description: Failed login attempts",CAT1,"Multiple failed authentication attempts indicate potential account compromise - CAT1",0.87,progressive_hint,2024-01-15 14:30:25,False
```

### Formato de Saída JSON
```json
[
  {
    "informacoes_das_colunas": "description: Malware detected on workstation",
    "categoria": "CAT2", 
    "explicacao": "This incident involves malware detection which falls under category CAT2 - Malware infection",
    "confianca": 0.95,
    "tecnica": "progressive_hint",
    "timestamp": "2024-01-15 14:30:22",
    "erro": false,
    "metadata": {
      "modelo": "openai_gpt4",
      "tokens_entrada": 156,
      "tokens_saida": 89,
      "tempo_processamento": 2.3
    }
  }
]
```

### Categorias NIST

| Código | Nome | Descrição | Exemplos |
|--------|------|-----------|----------|
| CAT1 | Account Compromise | Acesso não autorizado a contas | Phishing, brute force, roubo de credenciais |
| CAT2 | Malware | Infecção por código malicioso | Ransomware, trojans, vírus |
| CAT3 | Denial of Service | Indisponibilidade de sistemas | DDoS, ataques volumétricos |
| CAT4 | Data Leak | Vazamento de dados sensíveis | Exposição acidental, roubo de dados |
| CAT5 | Vulnerability Exploitation | Exploração de vulnerabilidades | RCE, SQL injection, XSS |
| ... | ... | ... | ... |

### Métricas de Qualidade

#### Confiança
- **0.0 - 0.3:** Baixa confiança, revisar manualmente
- **0.3 - 0.7:** Confiança moderada, validação recomendada  
- **0.7 - 0.9:** Alta confiança, provável classificação correta
- **0.9 - 1.0:** Muito alta confiança, classificação muito provável

#### Interpretação de Erros
```json
{
  "categoria": "ERROR",
  "explicacao": "Erro no processamento: API rate limit exceeded",
  "erro": true,
  "erro_detalhes": {
    "tipo": "RateLimitError",
    "mensagem": "Too many requests",
    "codigo": 429
  }
}
```

## Monitoramento e Logs

### Estrutura de Logs

```
logs/
├── framework.log              # Log principal do framework
├── security_incident_framework.log  # Log da classe principal
├── plugin_manager.log         # Log do gerenciador de plugins
├── metrics.log               # Log de métricas
└── errors.log                # Log de erros específicos
```

### Visualização de Logs em Tempo Real

```bash
# Log principal
tail -f logs/framework.log

# Apenas erros
tail -f logs/framework.log | grep ERROR

# Múltiplos logs
tail -f logs/*.log

# Com filtro colorido
tail -f logs/framework.log | grep --color=always -E "(ERROR|WARNING|INFO)"
```

### Análise de Logs

```bash
# scripts/analyze_logs.sh
#!/bin/bash

LOG_DIR="logs"
REPORT_FILE="logs/analysis_$(date +%Y%m%d_%H%M%S).txt"

echo "=== Análise de Logs - $(date) ===" > "${REPORT_FILE}"
echo "" >> "${REPORT_FILE}"

# Contagem de níveis de log
echo "== Níveis de Log ==" >> "${REPORT_FILE}"
grep -h "INFO\|WARNING\|ERROR\|DEBUG" "${LOG_DIR}"/*.log | \
  sed 's/.*- \([A-Z]*\) -.*/\1/' | \
  sort | uniq -c | sort -nr >> "${REPORT_FILE}"

echo "" >> "${REPORT_FILE}"

# Erros mais frequentes
echo "== Erros Mais Frequentes ==" >> "${REPORT_FILE}"
grep -h "ERROR" "${LOG_DIR}"/*.log | \
  sed 's/.*ERROR - //' | \
  sort | uniq -c | sort -nr | head -10 >> "${REPORT_FILE}"

echo "" >> "${REPORT_FILE}"

# Atividade por hora
echo "== Atividade por Hora ==" >> "${REPORT_FILE}"
grep -h "2024-" "${LOG_DIR}"/*.log | \
  sed 's/^\([0-9-]* [0-9]*\):.*/\1/' | \
  sort | uniq -c >> "${REPORT_FILE}"

echo "Análise salva em: ${REPORT_FILE}"
```

Este guia completo fornece todas as informações necessárias para instalar, configurar e usar o framework efetivamente em diferentes cenários, desde desenvolvimento até produção.