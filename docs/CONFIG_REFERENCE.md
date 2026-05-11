# Referência Completa do config.yaml

O arquivo `config.yaml` é a **configuração central** de cada projeto Pangolin. Ele define quais dados serão processados, quais modelos serão utilizados, quais técnicas de prompt serão aplicadas e como os resultados serão salvos.

Este documento descreve todos os campos disponíveis, seus tipos, valores padrão, restrições e boas práticas.

---

## Índice

- [Estrutura Geral](#estrutura-geral)
- [Seção `project`](#seção-project)
- [Seção `data`](#seção-data)
- [Seção `models`](#seção-models)
- [Seção `prompt`](#seção-prompt)
- [Seção `output`](#seção-output)
- [Exemplos Completos](#exemplos-completos)
- [Validação](#validação)
- [Boas Práticas](#boas-práticas)

---

## Estrutura Geral

O `config.yaml` é dividido em cinco seções, todas obrigatórias:

```yaml
project:    # Metadados do projeto
  ...

data:       # Configuração dos dados de entrada
  ...

models:     # Lista de modelos LLM a utilizar
  - ...

prompt:     # Técnicas de prompt a aplicar
  ...

output:     # Formato e salvamento dos resultados
  ...
```

---

## Seção `project`

Metadados descritivos do projeto. Não afetam a execução, mas são registrados em logs e relatórios.

```yaml
project:
  name: meu_experimento
  description: "Classificação de incidentes de segurança"
  created_at: "2024-01-15T10:30:00"
  version: "1.0.0"
  last_applied: "2024-01-15T11:00:00"  # Preenchido automaticamente pelo pg apply
```

| Campo | Tipo | Obrigatório | Descrição |
|---|---|:---:|---|
| `name` | string | **Sim** | Identificador do projeto. Deve corresponder ao nome do diretório |
| `description` | string | Não | Descrição do experimento ou tarefa |
| `created_at` | string (ISO 8601) | Não | Data de criação. Preenchido automaticamente pelo `pg init` |
| `version` | string | Não | Versão do experimento |
| `last_applied` | string (ISO 8601) | Não | Última execução do `pg apply`. Atualizado automaticamente |

---

## Seção `data`

Define quais colunas do dataset de entrada serão usadas no experimento.

```yaml
data:
  input_columns: [description]
  required_columns: [id, target]
```

| Campo | Tipo | Obrigatório | Descrição |
|---|---|:---:|---|
| `input_columns` | list[string] | **Sim** | Colunas cujos valores serão concatenados para formar o texto de entrada do prompt |
| `required_columns` | list[string] | Não | Colunas que devem existir no dataset, mas não são usadas como input (ex: `id`, rótulo real para avaliação) |

### Como `input_columns` funciona

As colunas listadas em `input_columns` são concatenadas em sequência para montar o texto passado ao modelo:

```yaml
data:
  input_columns: [assunto, corpo]
```

Para uma linha com `assunto = "Reunião amanhã"` e `corpo = "Confirmado para 14h"`, o input gerado será:

```
assunto: Reunião amanhã
corpo: Confirmado para 14h
```

### Exemplo com múltiplas colunas

```yaml
data:
  input_columns: [titulo, descricao, severidade]
  required_columns: [id, categoria_real, timestamp]
```

---

## Seção `models`

Lista de modelos LLM a utilizar no experimento. O framework executa todas as técnicas de prompt em **cada modelo** da lista, em sequência.

```yaml
models:
  - name: gpt-4o-mini
    provider: openai
    temperature: 0.2
    max_tokens: 1024
```

Cada item da lista aceita os seguintes campos:

| Campo | Tipo | Obrigatório | Padrão | Descrição |
|---|---|:---:|---|---|
| `name` | string | **Sim** | — | Nome do modelo conforme o provedor (ex: `gpt-4o-mini`, `claude-3-haiku-20240307`, `gemma2:9b`) |
| `provider` | string | **Sim** | — | Identificador do provedor (ver tabela abaixo) |
| `temperature` | float | Não | `0.2` | Temperatura de amostragem (0.0 = determinístico, 1.0 = criativo) |
| `max_tokens` | int | Não | `2048` | Número máximo de tokens na resposta |

### Provedores suportados

| `provider` | Plugin | Variável de ambiente necessária |
|---|---|---|
| `openai` | APIModel | `OPENAI_API_KEY` |
| `anthropic` | APIModel | `ANTHROPIC_API_KEY` |
| `gemini` / `google` | APIModel | `GEMINI_API_KEY` |
| `deepseek` | APIModel | `DEEPSEEK_API_KEY` |
| `groq` | APIModel | `GROQ_API_KEY` |
| `cohere` | APIModel | `COHERE_API_KEY` |
| `azure` | APIModel | `AZURE_API_KEY` + `AZURE_BASE_URL` |
| `bedrock` | APIModel | Credenciais AWS padrão |
| `vertex` | APIModel | Credenciais Google Cloud padrão |
| `ollama` / `local` | LocalModel | — (requer Ollama em execução) |
| `huggingface` | HuggingfaceModel | `HUGGINGFACE_API_KEY` |

### Configuração de credenciais

Crie um arquivo `.env` na raiz do projeto de experimento:

```dotenv
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...

# Para endpoints customizados
OLLAMA_BASE_URL=http://localhost:11434
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

O Pangolin resolve automaticamente a chave correta com base no padrão `{PROVIDER}_API_KEY`.

### Exemplo com múltiplos modelos

```yaml
models:
  - name: gpt-4o-mini
    provider: openai
    temperature: 0.2
    max_tokens: 2048

  - name: claude-3-haiku-20240307
    provider: anthropic
    temperature: 0.2
    max_tokens: 2048

  - name: gemma2:9b
    provider: ollama
    temperature: 0.2
    max_tokens: 2048
```

---

## Seção `prompt`

Define quais técnicas de prompt serão aplicadas e onde os schemas estão localizados.

```yaml
prompt:
  technique: [progressive_hint]
  schema_dir: schema
```

| Campo | Tipo | Obrigatório | Padrão | Descrição |
|---|---|:---:|---|---|
| `technique` | list[string] ou string | **Sim** | — | Técnica(s) a aplicar. Aceita string única ou lista |
| `schema_dir` | string | Não | `schema` | Diretório relativo onde os schemas YAML do projeto estão localizados |

### Técnicas disponíveis

| Valor | Técnica |
|---|---|
| `progressive_hint` | Progressive Hint Prompting |
| `self_hint` | Self-Hint Prompting |
| `hypothesis_testing` | Hypothesis Testing Prompting |
| `progressive_rectification` | Progressive Rectification Prompting |
| `free_prompt` | Free Prompt |
| `zeroshot` | Zero-Shot Prompting |

### Executar múltiplas técnicas

```yaml
prompt:
  technique:
    - zeroshot
    - progressive_hint
    - self_hint
  schema_dir: schema
```

O framework executará cada técnica para cada modelo configurado e gerará saídas separadas.

### Usar schema customizado

Se você criou ou modificou um schema em `schema/` do projeto, ele terá prioridade sobre o schema padrão do framework. Não é necessário alterar `schema_dir` — o diretório `schema` já é o padrão.

---

## Seção `output`

Controla o formato de salvamento dos resultados e a geração de artefatos de observabilidade.

```yaml
output:
  format: json
  save_metrics: true
  save_logs: true
```

| Campo | Tipo | Obrigatório | Padrão | Descrição |
|---|---|:---:|---|---|
| `format` | string | Não | `json` | Formato dos arquivos de resultado. Valores aceitos: `json`, `csv`, `xlsx` |
| `save_metrics` | bool | Não | `true` | Se `true`, salva arquivo de métricas de execução em `logs/` |
| `save_logs` | bool | Não | `true` | Se `true`, salva arquivo de log detalhado em `logs/` |

### Formatos de saída

| Formato | Extensão | Melhor para |
|---|---|---|
| `json` | `.json` | Integração com scripts, flexibilidade estrutural |
| `csv` | `.csv` | Análise em planilhas, processamento com pandas |
| `xlsx` | `.xlsx` | Relatórios, visualização no Excel |

Os resultados são salvos em `output/` com o padrão de nome:
```
output/resultado_<modelo>_<tecnica>_<timestamp>.<formato>
```

---

## Exemplos Completos

### Experimento simples — modelo local, uma técnica

```yaml
project:
  name: teste_local
  description: "Teste inicial com Ollama"
  version: "1.0.0"

data:
  input_columns: [description]
  required_columns: [id, target]

models:
  - name: gemma2:9b
    provider: ollama
    temperature: 0.2
    max_tokens: 2048

prompt:
  technique: [zeroshot]
  schema_dir: schema

output:
  format: csv
  save_metrics: true
  save_logs: true
```

### Experimento comparativo — múltiplos modelos e técnicas

```yaml
project:
  name: comparacao_llms
  description: "Comparação de GPT-4 vs Claude vs Gemini com Progressive Hint e Self-Hint"
  version: "1.0.0"

data:
  input_columns: [assunto, corpo_email]
  required_columns: [id, categoria_real]

models:
  - name: gpt-4o-mini
    provider: openai
    temperature: 0.2
    max_tokens: 2048

  - name: claude-3-haiku-20240307
    provider: anthropic
    temperature: 0.2
    max_tokens: 2048

  - name: gemini-1.5-flash
    provider: gemini
    temperature: 0.2
    max_tokens: 2048

prompt:
  technique:
    - progressive_hint
    - self_hint
  schema_dir: schema

output:
  format: xlsx
  save_metrics: true
  save_logs: true
```

### Experimento com Hypothesis Testing

```yaml
project:
  name: classificacao_nist
  description: "Classificação de incidentes usando NIST CSF com HTP"
  version: "2.0.0"

data:
  input_columns: [descricao_incidente]
  required_columns: [id, categoria_nist]

models:
  - name: gpt-4o
    provider: openai
    temperature: 0.1
    max_tokens: 4096

prompt:
  technique: [hypothesis_testing]
  schema_dir: schema

output:
  format: json
  save_metrics: true
  save_logs: true
```

> **Nota:** Para `hypothesis_testing`, lembre-se de preencher o campo `key_words` no schema `schema/hypothesis_testing.yaml` com as categorias e palavras-chave do seu domínio.

---

## Validação

O Pangolin valida o `config.yaml` automaticamente ao executar `pg apply`. As seguintes regras são verificadas:

| Regra | Descrição |
|---|---|
| Seções obrigatórias | `project`, `data`, `models`, `prompt`, `output` devem existir |
| `project.name` | Campo obrigatório |
| `data.input_columns` | Deve ser uma lista não-vazia |
| `models` | Deve ser uma lista com pelo menos um item |
| Cada modelo | Deve ter `name` e `provider` |
| `prompt.technique` | Campo obrigatório |
| `prompt.schema_dir` | Se presente, deve ser uma string |
| `output.format` | Se presente, deve ser `json`, `csv` ou `xlsx` |

### Executar validação manualmente

```bash
cd meu_experimento
pg apply
```

Erros de validação serão exibidos antes da importação dos plugins.

---

## Boas Práticas

**Versionamento do experimento**
```yaml
project:
  version: "2.1.0"   # Incremente a cada mudança significativa de configuração
```

**Temperature por tipo de tarefa**
- Classificação determinística: `temperature: 0.0` ou `0.1`
- Respostas com alguma variação: `temperature: 0.2` a `0.4`
- Geração criativa: `temperature: 0.7` a `1.0`

**Começar com menos técnicas**

Inicie com `zeroshot` para estabelecer a linha de base, depois adicione técnicas iterativamente:

```yaml
# Fase 1 — baseline
prompt:
  technique: [zeroshot]

# Fase 2 — comparação
prompt:
  technique: [zeroshot, progressive_hint, self_hint]
```

**Controle de custos**

Para modelos de API com cobrança por token, configure `max_tokens` de forma conservadora e prefira modelos menores em etapas iniciais de experimentação:

```yaml
models:
  - name: gpt-4o-mini        # Mais barato para testes iniciais
    provider: openai
    max_tokens: 1024

  - name: gpt-4o             # Mais caro, use quando houver resultado promissor
    provider: openai
    max_tokens: 2048
```

**Schemas customizados por projeto**

Copie o schema padrão para `schema/` e edite conforme necessário. O schema do projeto sempre tem prioridade:

```bash
cp FrameworkPE/pangolin/schemas/progressive_hint.yaml meu_projeto/schema/
# Edite meu_projeto/schema/progressive_hint.yaml com seu contexto específico
```
