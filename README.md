# Pangolin

Pangolin é um framework Python para comparar estratégias de *prompt engineering*
em tarefas que recebem dados tabulares e produzem respostas de LLM. Um projeto
Pangolin reúne configuração, dados, schemas de prompt, resultados e logs. O
framework chama modelos por APIs compatíveis com LiteLLM, pelo Ollama ou pelo
plugin local de Transformers.

## Requisitos

- Python 3.9 ou superior.
- Ollama instalado e em execução para usar modelos locais via Ollama.
- Credencial e dependências apropriadas para o provider escolhido.

## Instalação

Na raiz deste repositório:

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate       # Windows PowerShell
python -m pip install --upgrade pip
python -m pip install -e .
pg --help
```

`pg` é a única interface de linha de comando. Ela é implementada em
`pangolin/cli.py` com Typer. O runtime suporta Python 3.9 ou superior porque
Pandas 2.1, dependência do pacote, não suporta Python 3.8.

## Começar um experimento

```bash
pg init --name meu_experimento
cd meu_experimento
```

O comando cria `data/`, `schema/`, `model/`, `logs/`, `output/` e
`config.yaml`. Coloque um CSV, JSON ou XLSX em `data/` e ajuste a configuração:

```yaml
project:
  name: meu_experimento
  description: Comparação de estratégias de prompt

data:
  input_columns: [descricao]
  required_columns: [id]

models:
  - name: gemma2:9b
    provider: ollama
    temperature: 0.2
    max_tokens: 1024

prompt:
  technique: [zeroshot, progressive_hint]
  schema_dir: schema

output:
  format: json
  save_metrics: true
  save_logs: true
```

Cada arquivo de entrada precisa conter as colunas de `required_columns` e
`input_columns`. As colunas de entrada são concatenadas e enviadas ao modelo.
Configure API keys no ambiente ou em um `.env` na raiz do projeto; não coloque
segredos no `config.yaml` nem versione `.env`.

```dotenv
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
```

Para mudar o endpoint do Ollama, defina `base_url` no item do modelo em
`config.yaml`.

Valide a configuração e copie os schemas padrão selecionados:

```bash
pg apply
```

Execute o experimento:

```bash
pg run
```

Os resultados são gravados em `output/` por modelo e técnica; logs e métricas
ficam em `logs/`. Os valores de `save_metrics` e `save_logs` são aceitos na
configuração, mas ainda não controlam a persistência em todos os componentes.
Consulte [a referência de configuração](docs/CONFIG_REFERENCE.md) para o
comportamento detalhado.

Os logs de interação incluem prompt e resposta completos em JSON. Restrinja o
acesso a `logs/` se os dados puderem conter informações sensíveis. A contagem
local de tokens é uma estimativa e pode divergir do consumo registrado pelo
provider.

## CLI

| Comando | Ação |
|---|---|
| `pg init --name NOME` | Cria projeto no diretório atual |
| `pg apply` | Valida configuração e importa schemas do framework |
| `pg run` | Executa os modelos e técnicas configurados |
| `pg run --model NOME` | Executa somente um modelo já declarado no YAML |
| `pg run --technique NOME` | Sobrescreve as técnicas com uma técnica |
| `pg run --columns a,b` | Sobrescreve as colunas de entrada |
| `pg run --output csv\|json\|xlsx` | Sobrescreve o formato de saída |
| `pg run --temperature 0.2` | Sobrescreve a temperatura do modelo |
| `pg run --max-tokens 1024` | Sobrescreve o limite de tokens da resposta |
| `pg run --max-iterations 3` | Sobrescreve o limite de iterações da estratégia |
| `pg info` | Mostra informações do projeto atual |
| `pg list` | Lista projetos no diretório atual |
| `pg destroy --name NOME` | Pede confirmação e remove o projeto atual |
| `pg destroy --name NOME --force` | Remove sem confirmação |

Use `pg <comando> --help` para ver as opções. `--model` seleciona um modelo
por seu campo `name` em `config.yaml`; não aceita um identificador provider/model
inventado na linha de comando.

## Providers e modelos

O suporte é definido centralmente em `pangolin/core/plugin_manager.py`.

| Provider | Implementação | Observação |
|---|---|---|
| `openai`, `anthropic`, `gemini`, `google`, `cohere`, `deepseek`, `groq` | `APIModel` / LiteLLM | A chave de ambiente segue `{PROVIDER}_API_KEY`; consulte também os requisitos do LiteLLM |
| `openrouter` | `OpenRouterModel` / LiteLLM | `OPENROUTER_API_KEY`; aceita nomes de modelo com prefixo da organização |
| `azure`, `bedrock`, `vertex`, `palm` | `APIModel` / LiteLLM | Exigem configuração específica do provider além dos parâmetros comuns |
| `ollama`, `local` | `LocalModel` / LiteLLM | Ollama deve estar acessível; endpoint padrão `http://localhost:11434` |
| `huggingface` | `HuggingfaceModel` | Requer `torch` e `transformers`, que não são instalados pelas dependências base atuais |

Para instalar o suporte opcional ao Hugging Face local, use
`python -m pip install -e '.[huggingface]'`.

`HuggingfaceModel` carrega modelos locais do Transformers; não é o mesmo caminho
que chamar uma API hospedada do Hugging Face.

### OpenRouter

O plugin `OpenRouterModel` usa `https://openrouter.ai/api/v1` por padrão e lê a
chave de `OPENROUTER_API_KEY`. O campo `name` deve ser o identificador do modelo
aceito pelo OpenRouter, incluindo o prefixo da organização:

```yaml
models:
  - name: openai/gpt-5.2
    provider: openrouter
    temperature: 0.2
    max_tokens: 1024
    site_url: https://seu-dominio.example
    app_name: Meu experimento Pangolin
    extra_params:
      route: fallback
```

`site_url` e `app_name` viram os cabeçalhos `HTTP-Referer` e
`X-OpenRouter-Title`. `base_url` pode substituir o endpoint padrão. Opções
específicas da API, como `response_format`, `plugins`, `models`, `provider` e
`user`, podem ser passadas em `extra_params`. O `usage` devolvido pelo endpoint,
incluindo custo quando disponível, é preservado em `logs/` junto à interação.
Veja [o guia de OpenRouter](docs/OPENROUTER.md) para detalhes sobre cabeçalhos,
parâmetros e limitações atuais.

## Técnicas de prompt

Os schemas padrão estão em `pangolin/schemas/` e podem ser personalizados em
`<projeto>/schema/`.

| Identificador | Estratégia |
|---|---|
| `zeroshot` | Classificação direta sem exemplos fornecidos |
| `free_prompt` | Prompt livre configurável |
| `progressive_hint` | Refinamento iterativo com dicas |
| `self_hint` | Planejamento seguido de classificação |
| `hypothesis_testing` | Teste de categorias com palavras-chave |
| `progressive_rectification` | Classificação e retificação iterativas |

O campo `strategy` do schema seleciona a implementação executada por
`SchemaPromptPlugin`; uma estratégia nova exige um schema válido e uma
implementação `_execute_<strategy>`.

## Estrutura do pacote

```text
pangolin/
├── cli.py                 # Única interface CLI (Typer)
├── cmd/                   # Handlers dos comandos usados pela CLI
├── core/
│   ├── config/            # Leitura e validação
│   ├── project/           # Projeto, configuração e scaffold
│   ├── io/                # Dados e serialização
│   ├── observability/     # Logs e métricas
│   ├── framework.py       # Orquestração de experimentos
│   └── plugin_manager.py  # Registro e resolução de providers
├── plugins/
│   ├── models/            # Adaptadores de modelos
│   └── prompts/           # Configuração e execução das estratégias
└── schemas/               # Schemas padrão em YAML
```

## Documentação

- [Integração OpenRouter](docs/OPENROUTER.md)
