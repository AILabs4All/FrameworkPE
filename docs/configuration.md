# Configuração Detalhada

## Visão Geral

O framework utiliza um sistema de configuração hierárquico baseado em JSON que permite customização completa de todos os aspectos do sistema. Esta seção detalha cada opção de configuração disponível.

## Estrutura de Configuração

### Arquivo Principal (default_config.json)

```json
{
  "framework": {
    "name": "Security Incident Classification Framework",
    "version": "2.0.0",
    "description": "Framework pluginável para classificação de incidentes de segurança",
    "author": "Security Team",
    "license": "MIT"
  },
  "logging": {
    "level": "INFO",
    "log_dir": "logs",
    "max_file_size_mb": 10,
    "backup_count": 5,
    "enable_console": true,
    "enable_file": true,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S"
  },
  "models": {
    // Configurações de modelos - ver seção específica
  },
  "prompt_techniques": {
    // Configurações de técnicas - ver seção específica
  },
  "nist_categories": {
    // Categorias NIST - ver seção específica
  },
  "output": {
    // Configurações de saída - ver seção específica
  },
  "performance": {
    // Configurações de performance - ver seção específica
  }
}
```

## Configuração de Modelos

### OpenAI Models

```json
{
  "models": {
    "openai_gpt4": {
      "plugin": "APIModel",
      "provider": "openai",
      "model": "gpt-4",
      "api_key": "${OPENAI_API_KEY}",
      "base_url": null,
      "temperature": 0.7,
      "max_tokens": 2000,
      "top_p": 1.0,
      "frequency_penalty": 0.0,
      "presence_penalty": 0.0,
      "timeout": 30,
      "retry_attempts": 3,
      "retry_delay": 1.0,
      "rate_limit": 2.0
    },
    "openai_gpt35": {
      "plugin": "APIModel",
      "provider": "openai", 
      "model": "gpt-3.5-turbo",
      "api_key": "${OPENAI_API_KEY}",
      "base_url": null,
      "temperature": 0.7,
      "max_tokens": 1500,
      "timeout": 20,
      "retry_attempts": 2,
      "rate_limit": 3.0
    }
  }
}
```

**Parâmetros OpenAI:**
- `model`: Nome do modelo OpenAI (gpt-4, gpt-3.5-turbo, etc.)
- `api_key`: Chave da API OpenAI (use variável de ambiente)
- `base_url`: URL base personalizada (opcional)
- `temperature`: Criatividade da resposta (0.0-2.0)
- `max_tokens`: Limite de tokens na resposta
- `top_p`: Nucleus sampling (0.0-1.0)
- `frequency_penalty`: Penalidade por repetição (-2.0 a 2.0)
- `presence_penalty`: Penalidade por presença (-2.0 a 2.0)
- `timeout`: Timeout da requisição em segundos
- `retry_attempts`: Tentativas de retry em caso de erro
- `retry_delay`: Delay entre tentativas (segundos)
- `rate_limit`: Requisições por segundo

### HuggingFace Models

```json
{
  "models": {
    "huggingface_bert": {
      "plugin": "HuggingFaceModel",
      "provider": "huggingface",
      "model": "bert-base-uncased",
      "api_key": "${HUGGINGFACE_API_KEY}",
      "base_url": "https://api-inference.huggingface.co/models/",
      "task": "text-classification",
      "temperature": 0.7,
      "max_tokens": 1000,
      "timeout": 60,
      "retry_attempts": 3,
      "use_cache": true,
      "wait_for_model": true
    }
  }
}
```

**Parâmetros HuggingFace:**
- `model`: Nome do modelo no HuggingFace Hub
- `api_key`: Token do HuggingFace
- `base_url`: URL da API (padrão: api-inference.huggingface.co)
- `task`: Tipo de tarefa (text-classification, text-generation, etc.)
- `use_cache`: Usar cache do HuggingFace
- `wait_for_model`: Aguardar modelo carregar se necessário

### Ollama Models

```json
{
  "models": {
    "ollama_deepseek_15b": {
      "plugin": "LocalModel",
      "provider": "ollama",
      "model": "deepseek-r1:1.5b",
      "base_url": "http://localhost:11434",
      "temperature": 0.7,
      "max_tokens": 2000,
      "context_length": 4096,
      "timeout": 120,
      "keep_alive": "5m",
      "stream": false,
      "num_predict": -1,
      "num_ctx": 2048,
      "repeat_penalty": 1.1,
      "repeat_last_n": 64,
      "seed": -1,
      "stop": [],
      "tfs_z": 1.0,
      "top_k": 40,
      "top_p": 0.9
    },
    "ollama_mistral": {
      "plugin": "LocalModel",
      "provider": "ollama",
      "model": "mistral:7b",
      "base_url": "http://localhost:11434",
      "temperature": 0.3,
      "max_tokens": 1500
    }
  }
}
```

**Parâmetros Ollama:**
- `model`: Nome do modelo no Ollama (deepseek-r1:1.5b, mistral:7b, etc.)
- `base_url`: URL do servidor Ollama
- `context_length`: Tamanho do contexto
- `keep_alive`: Tempo para manter modelo carregado
- `stream`: Resposta em streaming
- `num_predict`: Número de tokens a prever (-1 = sem limite)
- `num_ctx`: Tamanho do contexto para geração
- `repeat_penalty`: Penalidade por repetição
- `repeat_last_n`: Últimos N tokens para penalidade
- `seed`: Seed para reprodutibilidade (-1 = aleatório)
- `stop`: Tokens de parada
- `tfs_z`: Tail Free Sampling
- `top_k`: Top-K sampling
- `top_p`: Top-P (nucleus) sampling

## Configuração de Técnicas de Prompt

### Progressive Hint

```json
{
  "prompt_techniques": {
    "progressive_hint": {
      "plugin": "ProgressiveHintPlugin",
      "description": "Progressive Hint Prompting technique",
      "enabled": true,
      "default_params": {
        "max_hints": 4,
        "limite_rouge": 0.9,
        "hint_strategy": "incremental",
        "base_prompt_template": "templates/progressive_hint_base.txt",
        "hint_templates": [
          "templates/hint_1.txt",
          "templates/hint_2.txt", 
          "templates/hint_3.txt",
          "templates/hint_4.txt"
        ]
      },
      "validation": {
        "min_confidence": 0.1,
        "max_iterations": 10,
        "early_stop_threshold": 0.95
      }
    }
  }
}
```

**Parâmetros Progressive Hint:**
- `max_hints`: Número máximo de dicas
- `limite_rouge`: Limite ROUGE para parada antecipada
- `hint_strategy`: Estratégia de dicas (incremental, adaptive, etc.)
- `base_prompt_template`: Template do prompt base
- `hint_templates`: Templates das dicas
- `min_confidence`: Confiança mínima para aceitar resultado
- `max_iterations`: Máximo de iterações
- `early_stop_threshold`: Limite para parada antecipada

### Self Hint

```json
{
  "prompt_techniques": {
    "self_hint": {
      "plugin": "SelfHintPlugin",
      "description": "Self Hint technique",
      "enabled": true,
      "default_params": {
        "max_self_hints": 3,
        "reflection_prompt": "templates/self_reflection.txt",
        "improvement_prompt": "templates/self_improvement.txt",
        "confidence_threshold": 0.8
      }
    }
  }
}
```

### Progressive Rectification

```json
{
  "prompt_techniques": {
    "progressive_rectification": {
      "plugin": "ProgressiveRectificationPlugin", 
      "description": "Progressive Rectification technique",
      "enabled": true,
      "default_params": {
        "max_rectifications": 5,
        "rectification_threshold": 0.7,
        "comparison_method": "semantic_similarity",
        "rectification_prompt": "templates/rectification.txt"
      }
    }
  }
}
```

### Hypothesis Testing

```json
{
  "prompt_techniques": {
    "hypothesis_testing": {
      "plugin": "HypothesisTestingPlugin",
      "description": "Hypothesis Testing technique", 
      "enabled": true,
      "default_params": {
        "num_hypotheses": 3,
        "evidence_threshold": 0.6,
        "hypothesis_template": "templates/hypothesis.txt",
        "evidence_template": "templates/evidence.txt",
        "conclusion_template": "templates/conclusion.txt"
      }
    }
  }
}
```

## Categorias NIST

### Configuração Completa

```json
{
  "nist_categories": {
    "enabled": true,
    "version": "2.0",
    "language": "pt-br",
    "categories": {
      "CAT1": {
        "name": "Account Compromise",
        "name_pt": "Comprometimento de Conta",
        "description": "Unauthorized access to user or administrator accounts",
        "description_pt": "Acesso não autorizado a contas de usuário ou administrador",
        "examples": [
          "Phishing attack resulting in credential theft",
          "Brute force attack on user account",
          "Credential stuffing attack",
          "Account takeover through social engineering"
        ],
        "keywords": [
          "phishing", "credential", "login", "brute force", 
          "password", "account", "unauthorized access"
        ],
        "severity_mapping": {
          "low": ["failed login attempts"],
          "medium": ["suspicious login patterns"],
          "high": ["confirmed account compromise"],
          "critical": ["administrative account compromise"]
        }
      },
      "CAT2": {
        "name": "Malware",
        "name_pt": "Malware",
        "description": "Malicious software infection or detection",
        "description_pt": "Infecção ou detecção de software malicioso",
        "examples": [
          "Ransomware infection",
          "Trojan horse detection",
          "Virus outbreak",
          "Spyware installation"
        ],
        "keywords": [
          "malware", "virus", "trojan", "ransomware",
          "spyware", "infection", "quarantine"
        ],
        "severity_mapping": {
          "low": ["potentially unwanted program"],
          "medium": ["adware detection"],
          "high": ["trojan infection"],
          "critical": ["ransomware outbreak"]
        }
      },
      "CAT3": {
        "name": "Denial of Service",
        "name_pt": "Negação de Serviço",
        "description": "Service disruption or unavailability",
        "description_pt": "Interrupção ou indisponibilidade de serviços",
        "examples": [
          "DDoS attack on web server",
          "Network flooding",
          "Resource exhaustion attack",
          "Application layer DoS"
        ],
        "keywords": [
          "ddos", "denial", "service", "unavailable",
          "flooding", "overload", "timeout"
        ]
      }
      // ... mais categorias
    },
    "custom_categories": {
      "enabled": true,
      "categories": {
        "CUSTOM1": {
          "name": "Internal Policy Violation",
          "description": "Violation of internal security policies"
        }
      }
    }
  }
}
```

## Configuração de Saída

### Formatos e Opções

```json
{
  "output": {
    "formats": ["csv", "json", "xlsx", "xml"],
    "default_format": "csv",
    "compression": {
      "enabled": false,
      "format": "gzip",
      "level": 6
    },
    "csv": {
      "delimiter": ",",
      "quotechar": "\"",
      "encoding": "utf-8",
      "include_header": true,
      "date_format": "%Y-%m-%d %H:%M:%S"
    },
    "json": {
      "indent": 2,
      "ensure_ascii": false,
      "sort_keys": false,
      "separators": [",", ":"]
    },
    "xlsx": {
      "sheet_name": "Classification Results",
      "include_charts": false,
      "freeze_header": true,
      "auto_filter": true
    },
    "include_metadata": true,
    "include_timestamps": true,
    "include_performance_metrics": false,
    "fields": {
      "informacoes_das_colunas": {
        "enabled": true,
        "description": "Input columns information"
      },
      "categoria": {
        "enabled": true, 
        "description": "NIST category classification"
      },
      "explicacao": {
        "enabled": true,
        "description": "Classification explanation"
      },
      "confianca": {
        "enabled": true,
        "description": "Confidence score (0-1)",
        "format": "%.3f"
      },
      "tecnica": {
        "enabled": true,
        "description": "Prompt technique used"
      },
      "timestamp": {
        "enabled": true,
        "description": "Processing timestamp",
        "format": "%Y-%m-%d %H:%M:%S"
      },
      "erro": {
        "enabled": true,
        "description": "Error flag"
      }
    }
  }
}
```

## Configuração de Performance

### Otimizações e Limites

```json
{
  "performance": {
    "rate_limiting": {
      "enabled": true,
      "api_models": {
        "default": 2.0,
        "openai": 2.0,
        "huggingface": 1.0
      },
      "local_models": {
        "default": 0.2,
        "ollama": 0.1
      },
      "adaptive": {
        "enabled": true,
        "error_backoff_factor": 0.5,
        "success_speedup_factor": 1.1,
        "max_rate": 10.0,
        "min_rate": 0.1
      }
    },
    "memory_monitoring": {
      "enabled": true,
      "max_memory_mb": 4096,
      "warning_threshold": 0.8,
      "cleanup_threshold": 0.9,
      "monitor_interval": 30
    },
    "token_tracking": {
      "enabled": true,
      "log_usage": true,
      "cost_calculation": {
        "enabled": true,
        "currency": "USD",
        "models": {
          "gpt-4": {
            "input_cost_per_1k": 0.03,
            "output_cost_per_1k": 0.06
          },
          "gpt-3.5-turbo": {
            "input_cost_per_1k": 0.001,
            "output_cost_per_1k": 0.002
          }
        }
      }
    },
    "caching": {
      "enabled": true,
      "cache_dir": "cache",
      "max_size_mb": 500,
      "ttl_hours": 24,
      "cleanup_interval": 3600,
      "compression": true
    },
    "parallel_processing": {
      "enabled": true,
      "max_workers": 4,
      "batch_size": 10,
      "queue_timeout": 300
    }
  }
}
```

## Variáveis de Ambiente

### Configuração via Environment

```bash
# API Keys
export OPENAI_API_KEY="sk-your-openai-key"
export HUGGINGFACE_API_KEY="hf_your-huggingface-token"
export ANTHROPIC_API_KEY="your-anthropic-key"

# Framework Configuration
export FRAMEWORK_CONFIG_FILE="/path/to/config.json"
export FRAMEWORK_LOG_LEVEL="INFO"
export FRAMEWORK_LOG_DIR="/var/log/security-framework"
export FRAMEWORK_CACHE_DIR="/var/cache/security-framework"
export FRAMEWORK_DATA_DIR="/var/lib/security-framework"

# Ollama Configuration
export OLLAMA_HOST="http://localhost:11434"
export OLLAMA_KEEP_MODELS="1"
export OLLAMA_NUM_PARALLEL="2"

# Performance Tuning
export FRAMEWORK_MAX_WORKERS="4"
export FRAMEWORK_RATE_LIMIT="2.0"
export FRAMEWORK_TIMEOUT="30"
export FRAMEWORK_MAX_MEMORY_MB="4096"

# Security
export FRAMEWORK_ENCRYPTION_KEY="your-encryption-key"
export FRAMEWORK_DISABLE_TELEMETRY="1"
export FRAMEWORK_AUDIT_ENABLED="1"
```

### Hierarquia de Configuração

A configuração segue esta ordem de precedência:

1. **Argumentos de linha de comando** (maior prioridade)
2. **Variáveis de ambiente**
3. **Arquivo de configuração especificado**
4. **Arquivo de configuração padrão**
5. **Valores padrão do código** (menor prioridade)

### Validação de Configuração

O framework valida automaticamente:

- **Tipos de dados** corretos
- **Valores dentro de limites** aceitáveis
- **Dependências** entre configurações
- **Disponibilidade de recursos** (APIs, modelos)
- **Permissões de arquivo** e diretório
- **Conectividade de rede** quando necessário

### Exemplo de Configuração Mínima

```json
{
  "models": {
    "primary": {
      "plugin": "APIModel",
      "provider": "openai", 
      "model": "gpt-3.5-turbo",
      "api_key": "${OPENAI_API_KEY}"
    }
  },
  "prompt_techniques": {
    "default": {
      "plugin": "ProgressiveHintPlugin"
    }
  }
}
```

Esta configuração mínima é suficiente para executar o framework com funcionalidade básica.