# Guia Completo: Criando e Configurando um Novo Projeto

Este guia acompanha o processo completo de criação de um projeto Pangolin do zero até a obtenção dos primeiros resultados, com exemplos práticos e explicação de cada decisão.

---

## Índice

- [Pré-requisitos](#pré-requisitos)
- [Passo 1 — Instalar o Pangolin](#passo-1--instalar-o-pangolin)
- [Passo 2 — Inicializar o Projeto](#passo-2--inicializar-o-projeto)
- [Passo 3 — Preparar os Dados](#passo-3--preparar-os-dados)
- [Passo 4 — Configurar o Projeto](#passo-4--configurar-o-projeto)
- [Passo 5 — Customizar Schemas (Opcional)](#passo-5--customizar-schemas-opcional)
- [Passo 6 — Aplicar as Configurações](#passo-6--aplicar-as-configurações)
- [Passo 7 — Executar o Experimento](#passo-7--executar-o-experimento)
- [Passo 8 — Analisar os Resultados](#passo-8--analisar-os-resultados)
- [Exemplo Prático Completo](#exemplo-prático-completo)
- [Comandos de Referência](#comandos-de-referência)

---

## Pré-requisitos

Antes de começar, verifique:

- [ ] Python 3.8 ou superior instalado (`python3 --version`)
- [ ] Pip atualizado (`pip install --upgrade pip`)
- [ ] Chaves de API das LLMs que deseja usar (OpenAI, Anthropic, etc.)
- [ ] Ollama instalado e em execução (somente se usar modelos locais)
- [ ] Dataset preparado em CSV, JSON ou XLSX

---

## Passo 1 — Instalar o Pangolin

```bash
# Entre no diretório do framework
cd FrameworkPE

# Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate    # Linux / macOS
# venv\Scripts\activate     # Windows

# Instale o Pangolin
pip install --upgrade pip setuptools wheel
pip install -e .

# Verifique a instalação
pg --help
```

Saída esperada:
```
 Usage: pg [OPTIONS] COMMAND [ARGS]...

 Pangolin - Prompt Engineering Framework

╭─ Commands ──────────────────────────────────────────────────────────╮
│ init     Inicializa um novo projeto de experimento                   │
│ apply    Aplica as configurações e importa plugins                   │
│ run      Executa o experimento                                       │
│ info     Exibe informações do projeto atual                          │
│ list     Lista projetos existentes                                   │
│ destroy  Remove o projeto e todos os seus arquivos                   │
╰─────────────────────────────────────────────────────────────────────╯
```

---

## Passo 2 — Inicializar o Projeto

```bash
pg init --name meu_experimento
```

Isso cria a seguinte estrutura:

```
meu_experimento/
├── data/           # Coloque seus dados aqui (CSV/JSON/XLSX)
├── schema/         # Schemas YAML das técnicas de prompt
├── model/          # Plugins de modelo (preenchido pelo pg apply)
├── logs/           # Logs e métricas (gerados pelo pg run)
├── output/         # Resultados (gerados pelo pg run)
├── config.yaml     # Configuração central — edite este arquivo
└── README.md       # README do projeto
```

> **Dica:** O nome do projeto se torna o nome do diretório. Use nomes descritivos sem espaços: `classificacao_emails_2024`, `teste_hipotese_nist`, etc.

---

## Passo 3 — Preparar os Dados

Coloque o arquivo de dados na pasta `data/` do projeto:

```bash
cp /caminho/para/seus_dados.csv meu_experimento/data/
```

Certifique-se de que o dataset atende aos requisitos:

1. **Formato:** CSV, JSON ou XLSX
2. **Cabeçalhos:** nomes de colunas sem espaços e em UTF-8
3. **Sem valores ausentes** nas colunas de input

Exemplo de dataset mínimo (`dados.csv`):
```csv
id,texto,categoria_real
1,"Servidor NTP mal configurado detectado","DE-TE"
2,"Tentativa de phishing por e-mail","DE-FE"
3,"Ransomware em endpoint Windows 10","PR-IP"
```

Consulte [docs/DATASETS_GUIDE.md](DATASETS_GUIDE.md) para detalhes completos.

---

## Passo 4 — Configurar o Projeto

Edite o arquivo `config.yaml` gerado pelo `init`:

```bash
nano meu_experimento/config.yaml
# ou: code meu_experimento/config.yaml
```

### Configuração mínima funcional

```yaml
project:
  name: meu_experimento
  description: "Classificação de incidentes de rede"
  version: "1.0.0"

data:
  input_columns: [texto]          # deve existir no seu CSV
  required_columns: [id, categoria_real]  # colunas auxiliares obrigatórias

models:
  - name: gpt-4o-mini
    provider: openai
    temperature: 0.2
    max_tokens: 1024

prompt:
  technique: [zeroshot]           # comece com zeroshot como baseline
  schema_dir: schema

output:
  format: csv
  save_metrics: true
  save_logs: true
```

### Configurar credenciais

Crie o arquivo `.env` dentro do diretório do projeto:

```bash
nano meu_experimento/.env
```

```dotenv
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...
```

> **Importante:** Nunca versione o arquivo `.env`. Adicione-o ao `.gitignore`.

---

## Passo 5 — Customizar Schemas (Opcional)

Após o `pg apply` (próximo passo), os schemas das técnicas configuradas serão copiados para `schema/`. Você pode editá-los para adaptar ao seu domínio.

### Exemplo: customizar o Zero-Shot para classificação de e-mails

Após o `apply`, edite `meu_experimento/schema/zeroshot.yaml`:

```yaml
technique: zeroshot
name: "Zero Shot"
description: "Classificação de e-mails como SPAM ou LEGÍTIMO"
acronym: "ZS"
strategy: zeroshot

prompt_text: |
  {system_prompt}

  {categories_info}

  INPUT:
  {input_framework}

  {output_format}

system_prompt: |
  Você é um especialista em filtragem de e-mails corporativos.
  Analise o e-mail recebido e classifique-o como SPAM ou LEGÍTIMO.

output_format: |
  FORMATO OBRIGATÓRIO DE SAÍDA:
  Category: [SPAM ou LEGÍTIMO]
  Explanation: [Justificativa detalhada]

categories:
  - code: SPAM
    name: "Spam"
    description: "E-mail não solicitado, publicitário ou malicioso"
  - code: LEGIT
    name: "Legítimo"
    description: "E-mail de comunicação corporativa ou pessoal válida"

params:
  temperature_override: 0.0

extraction:
  method: json
  unknown_category: UNKNOWN
```

### Exemplo: customizar Hypothesis Testing com palavras-chave

Edite `meu_experimento/schema/hypothesis_testing.yaml`:

```yaml
# ... campos obrigatórios mantidos ...

key_words:
  SPAM:
    - oferta
    - grátis
    - urgente
    - clique aqui
    - ganhe
    - promoção
  LEGIT:
    - reunião
    - relatório
    - equipe
    - projeto
    - cliente
    - prazo
```

> **Regra importante:** O schema na pasta `schema/` do projeto tem prioridade sobre o schema padrão do framework. Edite apenas os schemas do projeto, nunca os arquivos em `pangolin/schemas/`.

Consulte [SCHEMAS_REFERENCIA_RAPIDA.md](../SCHEMAS_REFERENCIA_RAPIDA.md) para a referência completa.

---

## Passo 6 — Aplicar as Configurações

```bash
cd meu_experimento
pg apply
```

O `apply` realiza três ações:
1. **Valida** o `config.yaml` — reporta erros caso existam
2. **Copia os plugins de modelo** para `model/` (ex: `api_model.py` para OpenAI)
3. **Copia os schemas** das técnicas configuradas para `schema/`

Saída esperada:
```
✓ Configuração válida
✓ Plugin importado: api_model.py (provider: openai)
✓ Schema importado: zeroshot.yaml
✓ Configurações aplicadas com sucesso
```

Se houver erros de validação:
```
✗ Configuração inválida:
  - Campo 'data.input_columns' é obrigatório
  - Campo 'name' é obrigatório no modelo[0]
```

Corrija os erros no `config.yaml` e execute `pg apply` novamente.

---

## Passo 7 — Executar o Experimento

```bash
# Dentro do diretório do projeto
pg run
```

Ou a partir de qualquer diretório:
```bash
pg run --name meu_experimento
```

### Sobrescrever configurações via CLI

```bash
# Usar modelo diferente
pg run --model anthropic/claude-3-haiku-20240307

# Usar técnica diferente
pg run --technique progressive_hint

# Mudar formato de saída
pg run --output xlsx
```

### Progresso da execução

O `pg run` exibe o progresso em tempo real:

```
Iniciando processamento — Modelo: gpt-4o-mini | Técnica: zeroshot
Processando: 100%|████████████████████| 50/50 [02:30<00:00,  3.00s/it]
Resultados salvos em: output/resultado_gpt-4o-mini_zeroshot_20240115_143022.csv
Métricas salvas em: logs/metrics_20240115_143022.json
```

---

## Passo 8 — Analisar os Resultados

Os resultados ficam em `output/`. Cada arquivo contém as colunas originais do dataset mais as colunas adicionadas pelo framework:

| Coluna | Descrição |
|---|---|
| `predicted_category` | Categoria predita pelo modelo |
| `explanation` | Justificativa do modelo |
| `model` | Nome do modelo utilizado |
| `technique` | Técnica de prompt aplicada |
| `input_tokens` | Tokens de entrada consumidos |
| `output_tokens` | Tokens de saída gerados |

### Análise básica com Python

```python
import pandas as pd

df = pd.read_csv("output/resultado_gpt-4o-mini_zeroshot_20240115_143022.csv")

# Acurácia (se houver coluna de categoria real)
acuracia = (df["predicted_category"] == df["categoria_real"]).mean()
print(f"Acurácia: {acuracia:.2%}")

# Distribuição de predições
print(df["predicted_category"].value_counts())

# Casos onde o modelo errou
erros = df[df["predicted_category"] != df["categoria_real"]]
print(f"Erros: {len(erros)}")
print(erros[["id", "texto", "categoria_real", "predicted_category"]].head())
```

### Ver métricas de execução

```bash
cat logs/metrics_*.json
```

```json
{
  "model": "gpt-4o-mini",
  "technique": "zeroshot",
  "num_records": 50,
  "total_input_tokens": 12450,
  "total_output_tokens": 3210,
  "execution_time_seconds": 150.3,
  "memory_peak_mb": 48.2
}
```

### Ver informações do projeto

```bash
pg info
```

---

## Exemplo Prático Completo

Cenário: classificar 50 e-mails como SPAM ou LEGÍTIMO usando GPT-4o-mini com três técnicas.

### 1. Inicializar

```bash
pg init --name classificacao_email
```

### 2. Preparar dados

```bash
cp emails_rotulados.csv classificacao_email/data/
```

### 3. Configurar

```yaml
# classificacao_email/config.yaml
project:
  name: classificacao_email
  description: "Classificação SPAM vs LEGÍTIMO com 3 técnicas"
  version: "1.0.0"

data:
  input_columns: [assunto, corpo]
  required_columns: [id, categoria_real]

models:
  - name: gpt-4o-mini
    provider: openai
    temperature: 0.2
    max_tokens: 1024

prompt:
  technique:
    - zeroshot
    - progressive_hint
    - self_hint
  schema_dir: schema

output:
  format: csv
  save_metrics: true
  save_logs: true
```

### 4. Credenciais

```bash
echo "OPENAI_API_KEY=sk-..." > classificacao_email/.env
```

### 5. Aplicar

```bash
cd classificacao_email
pg apply
```

### 6. Customizar schemas

```bash
# Editar classificacao_email/schema/zeroshot.yaml
# Editar classificacao_email/schema/progressive_hint.yaml
# Editar classificacao_email/schema/self_hint.yaml
# → Adicionar system_prompt e categorias específicas de e-mail em cada um
```

### 7. Executar

```bash
pg run
```

O framework executará as 3 técnicas no modelo configurado, gerando 3 arquivos de resultado em `output/`.

### 8. Comparar resultados

```python
import pandas as pd
import glob

resultados = {}
for arquivo in glob.glob("output/*.csv"):
    df = pd.read_csv(arquivo)
    tecnica = df["technique"].iloc[0]
    acuracia = (df["predicted_category"] == df["categoria_real"]).mean()
    resultados[tecnica] = acuracia

for tecnica, acc in sorted(resultados.items(), key=lambda x: -x[1]):
    print(f"{tecnica:30s}: {acc:.2%}")
```

Saída esperada:
```
progressive_hint              : 88.00%
self_hint                     : 84.00%
zeroshot                      : 76.00%
```

---

## Comandos de Referência

| Comando | Descrição |
|---|---|
| `pg init --name <nome>` | Cria novo projeto |
| `pg apply` | Valida config e importa plugins |
| `pg run` | Executa o experimento |
| `pg run --model <modelo>` | Sobrescreve o modelo |
| `pg run --technique <tecnica>` | Sobrescreve a técnica |
| `pg run --output <csv\|json\|xlsx>` | Sobrescreve o formato de saída |
| `pg info` | Exibe resumo do projeto atual |
| `pg list` | Lista projetos no diretório atual |
| `pg destroy --name <nome>` | Remove o projeto permanentemente |

### Atalho via script

O arquivo `pg.sh` na raiz do framework pode ser usado como alternativa ao comando `pg` se o ambiente virtual não estiver ativo:

```bash
./pg.sh init --name meu_experimento
./pg.sh run
```

---

## Próximos Passos

Após o primeiro experimento:

1. **Adicione mais técnicas** e compare os resultados
2. **Teste múltiplos modelos** adicionando entradas na lista `models`
3. **Customze os schemas** com exemplos few-shot e palavras-chave do seu domínio
4. **Crie técnicas novas** seguindo o guia em [GUIA_ARQUITETURA_PROMPTS.md](../GUIA_ARQUITETURA_PROMPTS.md#como-criar-uma-nova-técnica)
5. **Reutilize schemas entre projetos** copiando os arquivos YAML entre diretórios `schema/`
