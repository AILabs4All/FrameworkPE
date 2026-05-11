# Pangolin — Prompt Engineering Framework

**Pangolin** é um framework Python modular e extensível para experimentação sistemática com técnicas de *Prompt Engineering* em Modelos de Linguagem de Grande Escala (LLMs). Ele organiza experimentos em projetos isolados, suporta múltiplos provedores de LLM e disponibiliza seis técnicas avançadas de prompting prontas para uso — todas configuráveis via YAML, sem necessidade de alterar código.

---

## Índice

- [Visão Geral](#visão-geral)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Fluxo de Trabalho Básico](#fluxo-de-trabalho-básico)
- [Técnicas de Prompt Disponíveis](#técnicas-de-prompt-disponíveis)
- [Provedores de Modelos Suportados](#provedores-de-modelos-suportados)
- [Documentação Completa](#documentação-completa)

---

## Visão Geral

O Pangolin resolve o problema de **reprodutibilidade e comparação em experimentos com LLMs**. Cada projeto tem sua própria estrutura isolada de dados, schemas de prompt, plugins de modelo, logs e resultados — permitindo executar e comparar múltiplas técnicas e modelos de forma sistemática.

### Características Principais

| Recurso | Descrição |
|---|---|
| **Projetos isolados** | Cada experimento tem sua própria área de trabalho autossuficiente |
| **Agnóstico ao domínio** | Funciona para qualquer tarefa de classificação ou análise textual |
| **6 técnicas embutidas** | Progressive Hint, Self-Hint, Hypothesis Testing, Progressive Rectification, Free Prompt, Zero-Shot |
| **Multi-modelo** | Execute a mesma técnica em vários LLMs simultâneamente |
| **Schemas declarativos** | Crie e customize técnicas editando apenas arquivos YAML |
| **Métricas integradas** | Rastreamento automático de tokens, tempo, memória e ROUGE |
| **Múltiplos formatos** | Entrada e saída em CSV, JSON ou XLSX |
| **Credenciais dinâmicas** | Resolução automática de chaves de API via `.env` |

---

## Requisitos

- Python 3.8 ou superior
- `pip` atualizado

Para modelos locais:
- [Ollama](https://ollama.com) instalado e em execução

---

## Instalação

```bash
# Clone o repositório ou entre no diretório do framework
cd FrameworkPE

# Crie e ative o ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate          # Linux / macOS
# venv\Scripts\activate           # Windows

# Atualize ferramentas de build
pip install --upgrade pip setuptools wheel

# Instale o Pangolin em modo editável
pip install -e .
```

Após a instalação, o comando `pg` estará disponível no ambiente virtual:

```bash
pg --help
```

### Configuração de Credenciais

Crie um arquivo `.env` na raiz do seu projeto de experimento com as chaves das APIs que irá utilizar:

```dotenv
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
DEEPSEEK_API_KEY=...
GROQ_API_KEY=...

# Endpoints customizados (opcional)
OLLAMA_BASE_URL=http://localhost:11434
```

O Pangolin resolve as credenciais automaticamente a partir do padrão `{PROVIDER}_API_KEY`.

---

## Fluxo de Trabalho Básico

Todo experimento no Pangolin segue quatro etapas:

```
pg init → editar config.yaml → pg apply → pg run
```

### 1. Inicializar o projeto

```bash
pg init --name meu_experimento
```

Cria a seguinte estrutura:

```
meu_experimento/
├── data/           # Coloque seus arquivos CSV/JSON/XLSX aqui
├── schema/         # Schemas YAML das técnicas de prompt
├── model/          # Plugins de modelo (preenchido pelo apply)
├── logs/           # Logs e métricas de execução
├── output/         # Resultados gerados
├── config.yaml     # Configuração central do projeto
└── README.md
```

### 2. Adicionar dados e configurar

```bash
# Copie seus dados de entrada para data/
cp /caminho/para/dados.csv meu_experimento/data/

# Edite a configuração do projeto
nano meu_experimento/config.yaml
```

Exemplo mínimo de `config.yaml`:

```yaml
project:
  name: meu_experimento
  description: "Classificação de e-mails"

data:
  input_columns: [assunto, corpo]
  required_columns: [id, categoria_real]

models:
  - name: gpt-4o-mini
    provider: openai
    temperature: 0.2
    max_tokens: 1024

prompt:
  technique: [progressive_hint]
  schema_dir: schema

output:
  format: csv
  save_metrics: true
  save_logs: true
```

### 3. Aplicar configurações

```bash
cd meu_experimento
pg apply
```

O `apply` valida o `config.yaml` e copia para o projeto os schemas YAML e plugins de modelo correspondentes às técnicas e provedores configurados.

### 4. Executar o experimento

```bash
pg run
```

Ou sobrescrever configurações diretamente via CLI:

```bash
pg run --model anthropic/claude-3-haiku-20240307 --technique self_hint --output json
```

### Outros Comandos

```bash
# Ver resumo do projeto atual (estrutura, arquivos, config)
pg info

# Listar projetos existentes
pg list

# Remover o projeto e todos os seus arquivos
pg destroy --name meu_experimento
```

---

## Técnicas de Prompt Disponíveis

| Técnica | Identificador | Descrição |
|---|---|---|
| **Progressive Hint** | `progressive_hint` | Fornece dicas progressivas ao modelo para refinamento iterativo da resposta |
| **Self-Hint** | `self_hint` | O modelo elabora um plano próprio antes de classificar |
| **Hypothesis Testing** | `hypothesis_testing` | Testa hipóteses para cada categoria sistematicamente |
| **Progressive Rectification** | `progressive_rectification` | Usa mascaramento e retificação progressiva para corrigir erros |
| **Free Prompt** | `free_prompt` | Prompt flexível com exemplos e dicas configuráveis |
| **Zero-Shot** | `zeroshot` | Classificação direta sem exemplos pré-definidos |

Para detalhes técnicos de cada técnica, consulte [SCHEMAS_REFERENCIA_RAPIDA.md](SCHEMAS_REFERENCIA_RAPIDA.md).

---

## Provedores de Modelos Suportados

O Pangolin usa [LiteLLM](https://github.com/BerriAI/litellm) para comunicação com APIs, cobrindo a grande maioria dos provedores disponíveis no mercado.

| Provedor | `provider` | Variável de ambiente |
|---|---|---|
| OpenAI | `openai` | `OPENAI_API_KEY` |
| Anthropic | `anthropic` | `ANTHROPIC_API_KEY` |
| Google Gemini | `gemini` | `GEMINI_API_KEY` |
| DeepSeek | `deepseek` | `DEEPSEEK_API_KEY` |
| Groq | `groq` | `GROQ_API_KEY` |
| Azure OpenAI | `azure` | `AZURE_API_KEY` + `AZURE_BASE_URL` |
| AWS Bedrock | `bedrock` | Credenciais AWS padrão |
| Ollama (local) | `ollama` | — (requer Ollama instalado) |
| HuggingFace | `huggingface` | `HUGGINGFACE_API_KEY` |

### Executar com múltiplos modelos

Declare uma lista em `models` no `config.yaml` para executar a mesma técnica em todos os modelos automaticamente:

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

## Documentação Completa

| Documento | Conteúdo |
|---|---|
| [GUIA_ARQUITETURA_PROMPTS.md](GUIA_ARQUITETURA_PROMPTS.md) | Arquitetura interna, componentes, fluxo de execução, como estender o framework |
| [SCHEMAS_REFERENCIA_RAPIDA.md](SCHEMAS_REFERENCIA_RAPIDA.md) | Referência técnica de todos os schemas de prompt e campos disponíveis |
| [docs/CONFIG_REFERENCE.md](docs/CONFIG_REFERENCE.md) | Referência completa de todos os campos do `config.yaml` |
| [docs/DATASETS_GUIDE.md](docs/DATASETS_GUIDE.md) | Guia de formatação e preparação de datasets |
| [docs/NEW_PROJECT_GUIDE.md](docs/NEW_PROJECT_GUIDE.md) | Guia passo a passo para criar e configurar um novo projeto |
