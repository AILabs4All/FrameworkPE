# Pangolin — Guia de Arquitetura e Prompt Engineering

Este documento descreve a arquitetura interna do framework Pangolin, o fluxo completo de execução, o sistema de plugins e como estender o framework com novas técnicas de prompt.

---

## Índice

- [Visão Geral da Arquitetura](#visão-geral-da-arquitetura)
- [Estrutura de Diretórios do Framework](#estrutura-de-diretórios-do-framework)
- [Componentes Principais](#componentes-principais)
- [Fluxo Completo de Execução](#fluxo-completo-de-execução)
- [Sistema de Schemas YAML](#sistema-de-schemas-yaml)
- [Sistema de Plugins](#sistema-de-plugins)
- [Estratégias de Prompt em Detalhe](#estratégias-de-prompt-em-detalhe)
- [Como Criar uma Nova Técnica](#como-criar-uma-nova-técnica)
- [Observabilidade e Métricas](#observabilidade-e-métricas)
- [Padrões de Design Utilizados](#padrões-de-design-utilizados)

---

## Visão Geral da Arquitetura

O Pangolin é estruturado em três camadas:

```
┌─────────────────────────────────────────────────┐
│                 CLI (Typer)                      │
│   pg init │ pg apply │ pg run │ pg info ...      │
└───────────────────┬─────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────┐
│              Core Framework                      │
│  PangolinProject  │  PangolinFramework           │
│  ConfigLoader     │  PluginManager               │
│  SchemaValidator  │  MetricsCollector            │
└───────────────────┬─────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────┐
│              Plugin Layer                        │
│  Models: APIModel │ LocalModel │ HuggingfaceModel│
│  Prompts: SchemaPromptPlugin (genérico)          │
│  Schemas: progressive_hint.yaml │ self_hint.yaml │
│           hypothesis_testing.yaml │ zeroshot.yaml│
└─────────────────────────────────────────────────┘
```

**Princípio fundamental:** as técnicas de prompting **não contêm lógica de domínio hardcoded**. Todo o contexto (categorias, palavras-chave, exemplos, system prompt) é injetado via schemas YAML e configuração do projeto. Isso torna o framework aplicável a qualquer tarefa de classificação ou análise textual.

---

## Estrutura de Diretórios do Framework

```
FrameworkPE/
├── pangolin/
│   ├── cli.py                        # Ponto de entrada da CLI (Typer)
│   ├── commands/                     # Definições dos comandos CLI
│   │   ├── init.py
│   │   ├── apply.py
│   │   ├── run.py
│   │   ├── list_cmd.py
│   │   ├── info.py
│   │   └── destroy.py
│   ├── cmd/                          # Lógica de negócio dos comandos
│   │   ├── init.py                   # cmd_init()
│   │   ├── apply.py                  # cmd_apply()
│   │   └── run.py                    # run_command()
│   ├── core/
│   │   ├── framework.py              # PangolinFramework (orquestrador)
│   │   ├── plugin_manager.py         # PluginManager
│   │   ├── config/
│   │   │   ├── loader.py             # Carregador de config JSON/YAML
│   │   │   └── schema_validator.py   # Validador de schemas YAML
│   │   ├── project/
│   │   │   ├── pangolin_project.py   # PangolinProject (ciclo de vida)
│   │   │   └── scaffold.py           # Funções de criação de estrutura
│   │   ├── io/
│   │   │   ├── file_handlers.py      # Carregamento/salvamento de dados
│   │   │   └── response_parser.py    # Parser de respostas dos modelos
│   │   └── observability/
│   │       ├── logger.py             # Sistema de logging estruturado
│   │       └── metrics.py            # Coleta de métricas
│   ├── plugins/
│   │   ├── models/
│   │   │   ├── base_model.py         # Classe abstrata BaseModel
│   │   │   ├── api_model.py          # APIModel via LiteLLM
│   │   │   ├── local_model.py        # LocalModel via Ollama
│   │   │   └── hungguiface_model.py  # HuggingfaceModel
│   │   └── prompts/
│   │       ├── base_prompt.py        # BasePromptPlugin (abstrata)
│   │       ├── schema_prompt_plugin.py  # Plugin genérico (executa qualquer schema)
│   │       └── config/
│   │           └── prompt_config.py  # Dataclasses + PromptConfigFactory
│   └── schemas/                      # Schemas YAML padrão do framework
│       ├── progressive_hint.yaml
│       ├── self_hint.yaml
│       ├── hypothesis_testing.yaml
│       ├── progressive_rectification.yaml
│       ├── free_prompt.yaml
│       └── zeroshot.yaml
├── README.md
├── GUIA_ARQUITETURA_PROMPTS.md       # Este arquivo
├── SCHEMAS_REFERENCIA_RAPIDA.md
├── docs/
│   ├── CONFIG_REFERENCE.md
│   ├── DATASETS_GUIDE.md
│   └── NEW_PROJECT_GUIDE.md
├── setup.py
└── requirements.txt
```

---

## Componentes Principais

### `PangolinProject` — Ciclo de vida do projeto

Localização: `pangolin/core/project/pangolin_project.py`

Gerencia todo o ciclo de vida de um projeto isolado:

| Método | Descrição |
|---|---|
| `create()` | Cria a estrutura de diretórios e o `config.yaml` padrão |
| `apply()` | Valida o config, importa plugins e schemas para o projeto |
| `destroy()` | Remove completamente o projeto do disco |
| `load_config()` | Lê e retorna o `config.yaml` |
| `validate_config()` | Valida estrutura e campos obrigatórios, retorna lista de erros |
| `load_prompt_schema(name)` | Carrega um schema YAML (projeto → framework como fallback) |
| `get_info()` | Retorna metadados e estatísticas do projeto |

**Resolução de schema (prioridade):**
```
projeto/schema/<tecnica>.yaml   ←  primeiro
pangolin/schemas/<tecnica>.yaml ←  fallback
```

### `PangolinFramework` — Orquestrador de execução

Localização: `pangolin/core/framework.py`

Coordena o processamento completo de dados:

```python
framework.process_incidents(
    input_dir="data/",
    columns=["description"],
    model_config={"name": "gpt-4o-mini", "provider": "openai", ...},
    prompt_techniques=["progressive_hint", "self_hint"],
    output_format="csv"
)
```

Responsabilidades:
- Carrega e valida os dados de entrada
- Instancia o modelo via `PluginManager`
- Para cada técnica: carrega schema → cria config → instancia plugin → processa dados
- Salva resultados e métricas

### `PluginManager` — Registro de plugins

Localização: `pangolin/core/plugin_manager.py`

Mantém o registro de plugins de modelo e cria instâncias conforme o provedor configurado.

Mapeamento de provedores para plugins:

| Provedor | Plugin |
|---|---|
| `openai`, `anthropic`, `gemini`, `google`, `cohere`, `azure`, `bedrock`, `vertex`, `palm`, `deepseek`, `groq` | `APIModel` (via LiteLLM) |
| `ollama`, `local` | `LocalModel` |
| `huggingface` | `HuggingfaceModel` |

### `SchemaPromptPlugin` — Plugin genérico de prompts

Localização: `pangolin/plugins/prompts/schema_prompt_plugin.py`

Um único plugin capaz de executar **qualquer** técnica de prompt definida em schema YAML. Recebe uma instância de `PromptConfig` e delega para o método de estratégia correspondente.

```
SchemaPromptPlugin.execute()
    ├── strategy == "progressive_hint"       → _execute_progressive_hint()
    ├── strategy == "self_hint"              → _execute_self_hint()
    ├── strategy == "hypothesis_testing"     → _execute_hypothesis_testing()
    ├── strategy == "progressive_rectification" → _execute_progressive_rectification()
    ├── strategy == "free_prompt"            → _execute_free_prompt()
    └── strategy == "zeroshot"              → _execute_zeroshot()
```

### `PromptConfigFactory` — Fábrica de configurações

Localização: `pangolin/plugins/prompts/config/prompt_config.py`

Converte um dicionário YAML em um dataclass tipado:

```python
schema_dict = yaml.safe_load(open("schema/progressive_hint.yaml"))
config = PromptConfigFactory.create(schema_dict)
# Retorna: ProgressiveHintConfig(max_hints=4, quality_threshold=0.9, ...)
```

Registro interno:

| Estratégia | Dataclass |
|---|---|
| `progressive_hint` | `ProgressiveHintConfig` |
| `self_hint` | `SelfHintConfig` |
| `hypothesis_testing` | `HtpConfig` |
| `progressive_rectification` | `ProgressiveRectificationConfig` |
| `free_prompt` | `FreePromptConfig` |
| `zeroshot` | `ZeroShotConfig` |

---

## Fluxo Completo de Execução

```
┌──────────────┐
│  pg run      │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  run_command()  [cmd/run.py]             │
│  • Lê config.yaml                        │
│  • Resolve colunas, técnicas, modelos    │
│  • Instancia PangolinFramework           │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  process_incidents()  [core/framework.py]│
│                                          │
│  1. load_data_files(input_dir)           │
│     → Carrega CSV/JSON/XLSX para DataFrame│
│                                          │
│  2. validate_columns(df, columns)        │
│     → Verifica se as colunas existem     │
│                                          │
│  3. PluginManager.create_model_instance()│
│     → Instancia APIModel / LocalModel    │
│                                          │
│  4. Para cada TÉCNICA configurada:       │
│     a. project.load_prompt_schema(name)  │
│        → Lê YAML do projeto ou framework │
│     b. PromptConfigFactory.create(schema)│
│        → Converte dict → dataclass tipado│
│     c. SchemaPromptPlugin(model, config) │
│        → Instancia o plugin genérico     │
│                                          │
│     5. Para cada LINHA do dataset:       │
│        a. build_input_text(row, columns) │
│           → Monta texto do input         │
│        b. plugin.execute(text, row, ...)  │
│           → Executa a estratégia de prompt│
│        c. modelo.send_prompt(prompt)     │
│           → Chama a API / modelo local   │
│        d. extract_answer(response)       │
│           → Extrai categoria + explicação│
│        e. Coleta métricas de tokens      │
│           → input_tokens, output_tokens  │
│                                          │
│  6. save_results(results, output_dir)    │
│     → CSV / JSON / XLSX                  │
│                                          │
│  7. metrics_collector.persist()          │
│     → Salva JSON de métricas em logs/    │
└──────────────────────────────────────────┘
```

---

## Sistema de Schemas YAML

Os schemas YAML são o coração da extensibilidade do Pangolin. Eles definem completamente uma técnica de prompt: o texto do prompt, parâmetros, templates extras e configuração de extração de resposta.

### Localização dos schemas

```
pangolin/schemas/         ← Schemas padrão do framework (não edite)
meu_projeto/schema/       ← Schemas do projeto (sobrescrevem os padrão)
```

Se o projeto tiver um schema com o mesmo nome que o do framework, o schema do projeto tem prioridade. Isso permite customizar uma técnica para um experimento específico sem alterar o código original.

### Estrutura de um schema

```yaml
# ─── Identificação ───────────────────────────────────────────────
technique: nome_da_tecnica      # Identificador único (deve coincidir com o nome do arquivo)
name: "Nome Legível"            # Nome descritivo para exibição
description: "O que ela faz"    # Descrição completa da abordagem
acronym: "NT"                   # Sigla usada em logs e saídas

# ─── Execução ────────────────────────────────────────────────────
strategy: nome_da_tecnica       # Identifica qual método do plugin será chamado

# ─── Prompt ──────────────────────────────────────────────────────
prompt_text: |
  Texto do prompt principal.
  Use placeholders entre chaves: {input_framework}
  {output_format}

# ─── Formato de saída ────────────────────────────────────────────
output_format: |
  Category: [código ou rótulo]
  Explanation: [justificativa]

# ─── Parâmetros da técnica ───────────────────────────────────────
params:
  max_iter: 4
  quality_threshold: 0.9

# ─── Extração de resposta ────────────────────────────────────────
extraction:
  method: json              # "json" ou "regex"
  unknown_category: UNKNOWN
```

### Placeholders disponíveis

| Placeholder | Disponível em | Descrição |
|---|---|---|
| `{input_framework}` | Todos | Texto de entrada da linha do dataset |
| `{output_format}` | Todos | Bloco de formato de resposta do schema |
| `{system_prompt}` | `free_prompt`, `zeroshot` | Prompt de sistema configurável |
| `{categories_info}` | `free_prompt`, `zeroshot` | Lista de categorias formatada |
| `{examples_section}` | `free_prompt` | Bloco de exemplos formatado |
| `{context_hints}` | `free_prompt` | Dicas de contexto por palavra-chave |
| `{category}` | `hypothesis_testing` | Categoria sendo testada na iteração atual |
| `{keywords_str}` | `hypothesis_testing` | Palavras-chave da categoria atual |
| `{previous_category}` | `progressive_hint` | Resultado da iteração anterior |
| `{plan_instructions}` | `self_hint` | Instruções para o modelo elaborar o plano |
| `{rejected_category}` | `progressive_rectification` | Categoria(s) rejeitada(s) para retificação |
| `{subcategory}` | `progressive_rectification` | Subcategoria para mascaramento |

---

## Sistema de Plugins

### Plugin de Modelo

Todos os plugins de modelo herdam de `BaseModel`:

```python
class BaseModel:
    def send_prompt(self, prompt: str) -> str: ...
    def get_model_info(self) -> dict: ...
```

**APIModel** usa LiteLLM e aceita qualquer provedor compatível. A chamada é construída dinamicamente com base no padrão `provider/model_name`.

**LocalModel** se comunica com o Ollama via API HTTP local.

**HuggingfaceModel** carrega modelos diretamente do HuggingFace Hub.

### Isolamento de plugins por projeto

Ao executar `pg apply`, os arquivos de plugin necessários são copiados do framework para a pasta `model/` do projeto. Isso garante que:

1. O projeto é autossuficiente e portátil
2. Customizações no plugin do projeto não afetam outros projetos
3. Versões de plugin ficam fixadas para reprodutibilidade

---

## Estratégias de Prompt em Detalhe

### Progressive Hint (PHP)

Refina a classificação iterativamente fornecendo ao modelo a predição anterior como "dica":

```
1ª chamada: prompt_text(input)              → resposta_1
2ª chamada: hint_template(input, resposta_1) → resposta_2
3ª chamada: hint_template(input, resposta_2) → resposta_3
...até max_hints ou quality_threshold atingido
```

Parâmetros configuráveis: `max_hints`, `quality_threshold`, `mode`.

### Self-Hint (SHP)

O modelo elabora seu próprio plano antes de responder:

```
1ª chamada: "Entenda o problema e crie um plano de análise" → plano
2ª chamada: prompt + plano → resposta final
...até max_iter ou quality_threshold atingido
```

Parâmetros: `max_iter`, `quality_threshold`, `mode`.

### Hypothesis Testing (HTP)

Testa hipóteses sistemáticas para cada categoria definida em `key_words`:

```
Para cada categoria em key_words:
  → "Hipótese verdadeira: o input pertence a {categoria}? [SUPPORTED/NOT SUPPORTED]"
  → "Hipótese falsa:      o input NÃO pertence a {categoria}? [SUPPORTED/NOT SUPPORTED]"

Decisão: categoria onde H_true=SUPPORTED e H_false=NOT SUPPORTED
```

Parâmetros: `max_iter`, `quality_threshold`, `key_words` (obrigatório).

### Progressive Rectification (PRP)

Usa mascaramento de palavras-chave e retificação progressiva:

```
1ª chamada: prompt(input)                          → resposta_1
   → Mascara palavras-chave da categoria_1 no texto
2ª chamada: rectification_template(input_mascarado, "not: categoria_1") → resposta_2
   → Mascara palavras-chave da categoria_2
3ª chamada: rectification_template(input_mascarado, "not: categoria_1, categoria_2") → ...
```

Parâmetros: `max_iter`, `quality_threshold`, `mode`, `key_words`.

### Free Prompt (FREE)

Prompt flexível e totalmente configurável com suporte a exemplos, categorias e dicas de contexto:

```
[system_prompt]
CATEGORIES: [categories_info]
[examples_section]   ← se use_examples=true
[context_hints]      ← se use_context_hints=true
INPUT: [input_framework]
[output_format]
```

Parâmetros: `use_examples`, `use_structured_output`, `use_context_hints`, `temperature_override`.

### Zero-Shot (ZS)

Classificação direta em uma única chamada, sem exemplos nem refinamento iterativo. Útil como linha de base:

```
[system_prompt]
[categories_info]
INPUT: [input_framework]
[output_format]
```

Parâmetros: `mode`, `temperature_override` (padrão: `0.0`).

---

## Como Criar uma Nova Técnica

### Passo 1 — Criar o schema YAML

Crie `meu_projeto/schema/minha_tecnica.yaml`:

```yaml
technique: minha_tecnica
name: "Minha Técnica"
description: "Descrição detalhada do que a técnica faz"
acronym: "MT"
strategy: minha_tecnica    # Deve coincidir com o método no plugin

prompt_text: |
  Analise o seguinte texto:
  {input_framework}

  {output_format}

output_format: |
  Category: [categoria]
  Explanation: [justificativa]

params:
  max_iter: 3
  meu_parametro: valor

extraction:
  method: json
  unknown_category: UNKNOWN
```

### Passo 2 — Criar o dataclass de configuração (opcional)

Se a técnica tiver parâmetros específicos, adicione em `pangolin/plugins/prompts/config/prompt_config.py`:

```python
@dataclass
class MinhaTecnicaConfig(PromptConfig):
    max_iter: int = 3
    meu_parametro: str = "valor"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        base = PromptConfig.from_dict(data)
        params = data.get("params", {})
        return cls(
            **{k: v for k, v in vars(base).items()},
            max_iter=int(params.get("max_iter", 3)),
            meu_parametro=params.get("meu_parametro", "valor"),
        )
```

### Passo 3 — Registrar no Factory

No mesmo arquivo, registre no `PromptConfigFactory`:

```python
class PromptConfigFactory:
    registry: Dict[str, Any] = {
        # ... entradas existentes ...
        "minha_tecnica": MinhaTecnicaConfig,
    }
```

### Passo 4 — Implementar o método de execução

No `SchemaPromptPlugin`, adicione:

```python
def _execute_minha_tecnica(self, incident_text: str, data_row, columns, **kwargs):
    config = self.prompt_config  # MinhaTecnicaConfig
    results = []

    for i in range(config.max_iter):
        prompt = config.prompt_text.format(
            input_framework=incident_text,
            output_format=config.output_format,
        )
        response = self.model.send_prompt(prompt)
        answer = self._extract_answer(response)
        results.append(answer)

        if self._quality_ok(answer):
            break

    return results
```

### Passo 5 — Usar a nova técnica

Em `config.yaml`:

```yaml
prompt:
  technique: [minha_tecnica]
  schema_dir: schema
```

```bash
pg apply
pg run
```

---

## Observabilidade e Métricas

### Logs

O framework usa um logger estruturado configurado em `pangolin/core/observability/logger.py`. Logs são salvos em `projeto/logs/` com timestamp.

Níveis de log utilizados:
- `INFO` — progresso normal (técnica iniciada, modelo carregado, dados salvos)
- `WARNING` — situações não-críticas (schema não encontrado no projeto, fallback usado)
- `ERROR` — erros de execução (falha ao carregar dados, erro de API)

### Métricas coletadas

O `MetricsCollector` registra automaticamente para cada execução:

| Métrica | Descrição |
|---|---|
| `input_tokens` | Tokens enviados ao modelo |
| `output_tokens` | Tokens gerados pelo modelo |
| `total_tokens` | Soma de input + output |
| `execution_time` | Tempo total de processamento (segundos) |
| `memory_usage` | Pico de memória RAM usada (MB) |
| `model_name` | Modelo utilizado |
| `technique` | Técnica de prompt aplicada |
| `num_records` | Número de registros processados |

As métricas são salvas em `projeto/logs/metrics_<timestamp>.json`.

---

## Padrões de Design Utilizados

| Padrão | Onde | Propósito |
|---|---|---|
| **Strategy** | `SchemaPromptPlugin` + estratégias | Permite trocar técnicas de prompt sem alterar o código cliente |
| **Factory** | `PromptConfigFactory` | Cria o dataclass correto a partir do identificador de estratégia |
| **Plugin Architecture** | `PluginManager` + `BaseModel` | Extensão de modelos sem modificar o núcleo |
| **Template Method** | `BasePromptPlugin` | Define o esqueleto de execução; subclasses preenchem os detalhes |
| **Dataclass** | `PromptConfig` e subclasses | Configuração tipada, validada e imutável |
