# Arquitetura do Framework

## Visão Geral da Arquitetura

O **Security Incident Classification Framework** implementa uma arquitetura pluginável baseada em camadas, projetada para flexibilidade, extensibilidade e manutenibilidade. A estrutura separa claramente as responsabilidades entre diferentes componentes.

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE INTERFACE                      │
├─────────────────────────────────────────────────────────────┤
│  main.py  │  Scripts Shell  │  CLI Arguments  │  Config     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   CAMADA DE ORQUESTRAÇÃO                    │
├─────────────────────────────────────────────────────────────┤
│           SecurityIncidentFramework (core/)                 │
│  • Fluxo principal de processamento                         │
│  • Coordenação entre componentes                            │
│  • Validação de entrada e saída                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  CAMADA DE GERENCIAMENTO                    │
├─────────────────────────────────────────────────────────────┤
│   PluginManager  │  ConfigLoader  │  MetricsCollector      │
│  • Registro de    │  • Carrega e    │  • Coleta métricas   │
│    plugins        │    valida       │  • Monitora          │
│  • Instanciação   │    config       │    performance       │
│    dinâmica       │  • Resolve env  │                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE PLUGINS                        │
├─────────────────────┬───────────────────────────────────────┤
│    MODELOS          │           TÉCNICAS DE PROMPT          │
├─────────────────────┼───────────────────────────────────────┤
│  • APIModel         │  • ProgressiveHintPlugin              │
│    - OpenAI         │  • SelfHintPlugin                     │
│    - HuggingFace    │  • ProgressiveRectificationPlugin     │
│  • LocalModel       │  • HypothesisTestingPlugin            │
│    - Ollama         │                                       │
└─────────────────────┴───────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   CAMADA DE UTILITÁRIOS                     │
├─────────────────────────────────────────────────────────────┤
│  FileHandlers  │  Logger  │  SecurityExtractor  │  Metrics │
│  • Leitura/     │  • Log   │  • Extração NIST   │  • Token │
│    escrita      │    estrut│  • Categorização   │    count │
│  • CSV/JSON/    │    urado │  • Validação       │  • Tempo │
│    XLSX         │  • Multi │                    │  • Mem.  │
└─────────────────────────────────────────────────────────────┘
```

## Fluxo de Execução Detalhado

### 1. Inicialização (Bootstrap)

```python
# main.py ou script shell
framework = SecurityIncidentFramework(config_path)
├── ConfigLoader.load() → Carrega configuração
├── PluginManager() → Registra plugins disponíveis
├── MetricsCollector() → Inicia coleta de métricas
└── Validação da configuração
```

### 2. Validação de Entrada

```python
process_incidents(input_dir, columns, model_name, technique, ...)
├── load_data_files(input_dir) → Carrega arquivos de dados
├── validate_columns(dataframes, columns) → Verifica colunas obrigatórias
├── _get_model_config(model_name) → Obtém configuração do modelo
└── _get_prompt_config(technique) → Obtém configuração da técnica
```

### 3. Instanciação Dinâmica

```python
# Criação de instâncias via PluginManager
model_instance = plugin_manager.create_model_instance(plugin_type, config)
prompt_instance = plugin_manager.create_prompt_instance(plugin_type, model)
```

### 4. Processamento Iterativo

```python
for dataframe in dataframes:
    for index, row in dataframe.iterrows():
        ├── _build_prompt(row, columns) → Constrói prompt base
        ├── prompt_instance.execute() → Aplica técnica específica
        ├── model_instance.send_prompt() → Envia para LLM/SLM
        └── Coleta resultados e métricas
```

### 5. Finalização e Saída

```python
├── save_results(results, output_format) → Salva em formato especificado
├── metrics_collector.generate_report() → Gera relatório de métricas
└── Logs de finalização
```

## Estrutura de Pastas e Responsabilidades

### `/core/` - Núcleo do Framework

| Arquivo | Responsabilidade | Função Principal |
|---------|------------------|------------------|
| `framework.py` | Orquestração principal | Coordena todo o fluxo de processamento |
| `config_loader.py` | Gerenciamento de configurações | Carrega, valida e resolve configurações |
| `plugin_manager.py` | Sistema de plugins | Registra e instancia plugins dinamicamente |
| `base_plugins.py` | Interfaces base | Define contratos para plugins |

### `/plugins/` - Sistema Extensível

#### `/plugins/models/` - Plugins de Modelos
- **`base_model.py`**: Interface base para todos os modelos
- **`api_model.py`**: Implementação para APIs (OpenAI, HuggingFace)
- **`local_model.py`**: Implementação para modelos locais (Ollama)
- **Específicos**: `openai_model.py`, `huggingface_model.py`, `ollama_model.py`

#### `/plugins/prompts/` - Técnicas de Prompt
- **`base_prompt.py`**: Interface base para técnicas
- **`progressive_hint.py`**: Progressive Hint Prompting
- **`self_hint.py`**: Self Hint Prompting  
- **`progressive_rectification.py`**: Progressive Rectification
- **`hypothesis_testing.py`**: Hypothesis Testing

### `/utils/` - Utilitários e Suporte

| Arquivo | Função | Características |
|---------|--------|-----------------|
| `file_handlers.py` | I/O de arquivos | Suporte CSV, JSON, XLSX |
| `logger.py` | Sistema de logs | Logs estruturados e configuráveis |
| `metrics.py` | Coleta de métricas | Performance, tokens, tempo |
| `security_extractor.py` | Extração NIST | Categorização de incidentes |

### `/config/` - Configurações Centralizadas

- **`default_config.json`**: Configuração principal
- Suporte a variáveis de ambiente (`${OPENAI_API_KEY}`)
- Validação automática de campos obrigatórios

### `/scripts/` - Automação

- **`run_ollama_classification.sh`**: Automação completa para modelos locais
- Instalação automática do Ollama
- Gerenciamento do ciclo de vida do servidor
- Download automático de modelos

## Padrões Arquiteturais Implementados

### 1. Plugin Architecture
- Interfaces bem definidas (`BaseModel`, `BasePrompt`)
- Carregamento dinâmico de plugins
- Extensibilidade sem modificar código core

### 2. Strategy Pattern
- Técnicas de prompt intercambiáveis
- Modelos intercambiáveis
- Configuração via JSON

### 3. Factory Pattern
- `PluginManager` como factory de plugins
- Instanciação baseada em configuração
- Abstração da criação de objetos

### 4. Observer Pattern
- Sistema de métricas observa execução
- Logs estruturados para auditoria
- Callbacks para coleta de dados

## Fluxo de Dados

### Entrada → Processamento → Saída

```
Dados de Entrada (CSV/JSON/XLSX)
         ↓
    Validação e Carregamento
         ↓
    Construção de Prompts
         ↓
    Aplicação de Técnica de Prompt
         ↓
    Envio para Modelo (API/Local)
         ↓
    Processamento da Resposta  
         ↓
    Extração de Categoria NIST
         ↓
    Coleta de Métricas
         ↓
    Formatação de Resultados
         ↓
    Saída (CSV/JSON/XLSX)
```

## Características de Design

### ✅ Vantagens da Arquitetura

- **Modularidade**: Componentes independentes e reutilizáveis
- **Extensibilidade**: Novos plugins sem modificar código existente
- **Testabilidade**: Cada camada pode ser testada isoladamente
- **Manutenibilidade**: Separação clara de responsabilidades
- **Configurabilidade**: Comportamento controlado via configuração
- **Observabilidade**: Logs e métricas em todos os níveis

### 🔄 Pontos de Extensão

1. **Novos Modelos**: Implementar `BaseModel`
2. **Novas Técnicas**: Implementar `BasePrompt`  
3. **Novos Formatos**: Estender `FileHandlers`
4. **Novas Métricas**: Adicionar ao `MetricsCollector`
5. **Nova Configuração**: Estender `ConfigLoader`

### 🛡️ Tratamento de Erros

- Validação em múltiplas camadas
- Fallbacks para configurações ausentes
- Logs detalhados para debugging
- Graceful degradation em falhas de plugins

## Considerações de Performance

- **Lazy Loading**: Plugins carregados sob demanda
- **Streaming**: Processamento iterativo de grandes datasets
- **Caching**: Configurações cacheadas após carregamento
- **Monitoring**: Métricas de tempo e memória
- **Rate Limiting**: Controle de requisições para APIs

Esta arquitetura garante que o framework seja robusto, extensível e fácil de manter, seguindo as melhores práticas de desenvolvimento de software enterprise.