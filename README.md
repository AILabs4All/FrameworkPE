# Pangolin - Prompt Engineering Framework

O **Pangolin** é um framework modular e extensível feito em Python voltado para a experimentação, teste e comparação sistemática de diferentes técnicas de *Prompt Engineering* utilizando múltiplos Modelos de Linguagem de Larga Escala (LLMs).

## 🚀 Visão Geral

O Pangolin permite que você isole seus experimentos em "projetos". Cada projeto possui sua própria estrutura de diretórios para manter dados, configurações, plugins (prompts e modelos), logs e resultados completamente independentes.

### Principais Características

- **Projetos Isolados**: Cada experimento tem sua própria área de trabalho.
- **Suporte a Múltiplos Modelos**: APIs (OpenAI, Anthropic), modelos locais via Ollama, e HuggingFace.
- **Técnicas Avançadas Embutidas**: Progressive Hint, Self-Hint, Hypothesis Testing, Zero-Shot, etc.
- **Importação Automática**: O framework copia os plugins necessários para dentro do seu projeto para garantir a reprodutibilidade.
- **Métricas Embutidas**: Rastreamento de logs de execução, métricas de desempenho, contagem de tokens e custos.
- **Formatos de Saída Flexíveis**: CSV, JSON ou Excel (XLSX).

---

## 💻 Instalação

### Instalação (Ambiente Virtual recomendado)

```bash
# Clone ou entre no diretório do projeto
cd FrameworkPE

# Cria e ativa um ambiente virtual (Linux/Mac)
python3 -m venv venv
source venv/bin/activate

# Atualiza dependências básicas
pip install --upgrade pip setuptools wheel

# Instala o Pangolin em modo editável e instala as dependências
pip install -e . --no-cache-dir
```

> **Nota:** Certifique-se de instalar as dependências do arquivo `requirements.txt` caso não use a instalação via `setup.py`: `pip install -r requirements.txt`.

---

## 🛠️ Como Usar (CLI)

O Pangolin agora utiliza a biblioteca Typer para a sua CLI, providenciando uma interface mais clara. O comando principal pode ser invocado via Python:

```bash
# Garantindo que você está na raiz do FrameworkPE e no ambiente virtual
python -m pangolin.cli --help
```

Ou, utilizando o script auxiliar presente na raiz do projeto:
```bash
pg --help
```

### Fluxo de Trabalho (Workflow) Básico

#### 1. Inicializar um novo projeto de experimento

```bash
pg init --name meu_experimento
```
Isso criará uma pasta chamada `meu_experimento` contendo os subdiretórios `data/`, `prompts/`, `model/`, `logs/`, `output/` e o arquivo `config.yaml`.

#### 2. Preparar os dados e configurar

```bash
cd meu_experimento

# Copie seus dados de teste para a pasta data/
cp /caminho/para/meus_dados.csv data/
```

Edite o arquivo `config.yaml` gerado (se necessário) para definir qual modelo e qual técnica de prompt usar por padrão, bem como o arquivo de entrada.

#### 3. Aplicar as configurações

O comando `apply` vai ler o seu `config.yaml`, validar se as configurações estão corretas, e copiar os plugins (código Python do modelo e da técnica de prompt) necessários do núcleo do framework para as pastas `model/` e `prompts/` do seu projeto. 

Isso garante que o seu projeto é autossuficiente (você pode alterar o prompt especificamente para este projeto sem afetar o framework).

```bash
pg apply
```

#### 4. Executar o experimento

Roda o experimento utilizando os dados e a técnica configurados no `config.yaml`.

```bash
pg run
```

Se desejar, você pode sobrescrever configurações do `config.yaml` diretamente via linha de comando:

```bash
pg run --model ollama_llama3:8b --technique self_hint --output csv
```

#### 5. Checar Informações do Projeto

Para ver um resumo do projeto atual (diretórios, contagem de arquivos e configurações básicas do `config.yaml`):

```bash
pg info
```

#### 6. Remover o projeto

Se desejar apagar o projeto atual e todos os seus arquivos:

```bash
pg destroy --name meu_experimento
```

---

## 🧠 Modelos e Técnicas Disponíveis

O Pangolin suporta nativamente uma vasta gama de provedores (providers) e técnicas de prompt avançadas.

### 🌐 Providers (Provedores)
O framework é capaz de se comunicar com diversos provedores ao redor do globo, repassando suas chamadas via APIs ou instâncias locais. 

**Resolução Dinâmica de Chaves (NOVIDADE):**
Não é mais necessário depender de configurações arbitrárias para encontrar as chaves de acesso. O Pangolin agora resolve nativamente a sua chave de autenticação lendo o arquivo `.env` (localizado na raiz do projeto) e procurando por uma combinação dinâmica construída com o *nome do provider* em caixa alta, seguido de `_API_KEY`. Da mesma maneira resolve variáveis base URL com `_BASE_URL`.

**Exemplos de provedores suportados e suas chaves esperadas:**
- **`openai`**: O sistema procurará automaticamente por `OPENAI_API_KEY`.
- **`anthropic`**: Procurará por `ANTHROPIC_API_KEY`.
- **`gemini`** (ou `google`): Procurará por `GEMINI_API_KEY`.
- **`ollama`** (ou `local`): Modelos hospedados localmente via Ollama (pode receber o `OLLAMA_BASE_URL` para mudar a porta padrão).
- **`huggingface`**: Procurará por `HUGGINGFACE_API_KEY`.
- **`deepseek`**: Procurará por `DEEPSEEK_API_KEY`.
- **Diversos outros suportados nativamente construídos dinamicamente**: `cohere`, `azure`, `bedrock`, `vertex`, `palm`, `groq`, etc. (Cada um seguindo o padrão, ex: `GROQ_API_KEY`).

### 💡 Técnicas de Prompt
Você pode definir as técnicas a serem executadas pelos modelos diretamente no arquivo de configuração do seu projeto ou modificá-las via terminal.
As técnicas padrão embarcadas no sistema e suas reações são:
- **`progressive_hint`**: Realiza quebras graduais e fornece dicas de análise que aumentam em complexidade progressivamente.
- **`progressive_rectification`**: Aplica mecanismos para o próprio modelo revisar, avaliar criticamente, e retificar possíveis falhas de suas hipóteses iniciais.
- **`self_hint`**: Induz o modelo a definir primeiramente quais informações ele precisa antes de resolver, criando suas próprias 'dicas' balizadoras.
- **`hypothesis_testing`**: Baseia-se em levantar hipóteses explícitas de causa/efeito sobre as entradas do usuário antes de traçar uma conclusão.
- **`free_prompt`**: Prompt genérico desprovido de restrições ou injeções elaboradas para testes basais (controle).
- **`zeroshot`**: (Ou *zero-shot_b*), execução crua em único disparo para observar a resolução nativa do framework não-viesada de aprendizado de exemplos da máquina.

---

## 🤖 Como rodar múltiplos modelos em um mesmo projeto (Multi-target)

---

## 🏗️ Arquitetura Agnóstica: Criando Configurações de Tarefas (TaskConfig)

O Pangolin foi remodelado para adotar uma **Arquitetura Totalmente Agnóstica ao Domínio**. Isso significa que as técnicas de prompting (Zero-Shot, Self-Hint, Hypothesis Testing, etc.) **não contêm código hardcoded** de um domínio específico (como regras de Cibersegurança ou categorias do NIST). Em vez disso, toda a inteligência e o contexto da tarefa são injetados externamente através de objetos JSON/YAML (`TaskConfig`).

### O Fluxo de Execução

Como detalhado na modelagem do framework:
1. **DataFrame Row:** Uma linha de dados (ex: CSV de emails) entra no sistema.
2. **build_input_text(row):** O plugin constrói a entrada dinamicamente usando a chave `input_builder` definida no seu JSON.
3. **execute():** O plugin abstrato do framework gera o prompt em tempo de execução incorporando as categorias, system_prompt e few_shot_examples do `TaskConfig`.
4. **send_prompt(prompt):** O modelo LLM configurado (via `api_model` ou `local_model`) processa a entrada.
5. **extract_answer(response):** A classe base extrai e padroniza a saída do modelo baseando-se nas regras da chave `extraction` (seja por JSON ou template).
6. **Resultado Estruturado:** Uma resposta formatada é acoplada às métricas e salva.

### Como usar o framework corretamente para sua Tarefa

Para que o framework resolva um problema novo (classificação de spam, análise de sentimento, triagem jurídica, etc.), você precisa fornecer um arquivo JSON de configuração (ex: `task_config.json`) em seu projeto com a seguinte estrutura esperada pelas classes base:

```json
{
  "system_prompt": "You are an email filtering assistant determining whether an incoming email is 'SPAM' or 'LEGITIMATE'.",
  "categories": [
    "SPAM",
    "LEGITIMATE"
  ],
  "unknown_category": "UNKNOWN",
  "input_builder": "Sender: {Sender} / Subject: {Subject} / Body: {Body}",
  "output_format": "You must output valid JSON: {\"category\": \"<SPAM or LEGITIMATE>\", \"explanation\": \"<why>\"}",
  "extraction": {
    "method": "json"
  },
  "context_hints_triggers": {
    "SPAM": "Focus on urgency words, requested payments, or unfamiliar sketchy domains.",
    "LEGITIMATE": "Check if it comes from an internal corporate domain or known contacts."
  },
  "few_shot_examples": [
    {
      "input": "Sender: boss@company.com / Subject: Q3 Report / Body: Here it is.",
      "output": "{\"category\": \"LEGITIMATE\", \"explanation\": \"Internal sender.\"}"
    }
  ]
}
```

Ao carregar esse JSON nos seus scripts/CLI, você o repassa ao instanciar os `PromptPlugins` (que herdam de `BasePromptPlugin(model_plugin, task_config)`). O framework fará o intermédio entre as regras desta JSON e as estratégias complexas de raciocínio de cada plugin automaticamente!

Graças ao processamento em cadeia, você pode definir em seu `config.yaml` um Array (Lista) de múltiplos modelos. Todos serão validados e irão competir entre si iterando com a técnica especificada.

Veja os exemplos de configuração para rodar automaticamente os potentes **DeepSeek**, **GPT-5**, **Gemini 3** e **Claude Sonnet** em sequência:

```yaml
models:
  # DeepSeek - Modelo nativo e focado em alta velocidade/raciocínio
  # Requer a variável DEEPSEEK_API_KEY declarada na raiz.
  - name: deepseek-v4-flash
    provider: deepseek
    temperature: 0.2
    max_tokens: 2048

  # OpenAI - Integrando o modelo avançado de nova geração 
  - name: gpt-5
    provider: openai
    temperature: 0.2
    max_tokens: 4096
    
  # Google - Integrando o modelo Gemini de terceira geração
  - name: gemini-3.0-pro
    provider: gemini
    temperature: 0.2
    max_tokens: 2048
    
  # Anthropic - Utilizando a familia de modelos Claude Sonnet
  - name: claude-3-sonnet-20240229
    provider: anthropic
    temperature: 0.3
    max_tokens: 4096

prompt:
  technique: progressive_hint
  custom_prompts_dir: prompts
```

Quando você rodar `./pg.sh run` com aquele arquivo ali, ele vai aplicar a técnica `progressive_hint` sequencialmente nos 4 LLMs, gravar 4 outputs unificados, extrair 4 métricas, e relatar todas juntas!

> **Nota**: Para redirecionar e customizar domínios exógenos em qualquer API particular (ex: Groq, Together), sempre declare por `.env`, seguindo o padrão, como `GROQ_BASE_URL=https://api.groq.com/openai/v1`. O sistema injetará a lógica do motor sem falhas.

---

## 📂 Estrutura Organizacional

### A Estrutura do Framework (`FrameworkPE/pangolin/`)
- `cli.py`: Ponto de entrada principal da Interface de Linha de Comando (CLI) gerada com *Typer*.
- `commands/`: Definições dos comandos CLI (init, apply, run, info, destroy, list).
- `cmd/`: A lógica/backend implementada por baixo de cada comando CLI.
- `core/`: Componentes centrais do sistema (`pangolin_project.py`, carregadores de configurações, gerenciamento de plugins).
- `plugins/`: Implementações embutidas de Modelos (`models/`) e Técnicas de Prompt (`prompts/`).
- `utils/`: Utilitários compartilhados (logs, formatadores de saída, métricas).

### A Estrutura de um Projeto de Experimento
Gerada automaticamente quando você roda o `init do`:
```text
meu_experimento/
├── data/          # Seus arquivos CSV/JSON/XLSX de entrada
├── prompts/       # Código exportado das técnicas de prompt (pode ser modificado por você)
├── model/         # Código exportado dos provedores de LLM
├── logs/          # Arquivos de log gerados durante o `run`
├── output/        # Resultados processados (arquivos finais gerados)
├── config.yaml    # Configuração central do seu projeto
└── README.md
```

## 🤝 Extensibilidade

Você pode estender o Pangolin criando suas próprias técnicas de prompt. Ao rodar `apply`, os arquivos do núcleo do framework vão para as pastas do seu projeto. Você pode editar diretamente os arquivos `.py` dentro da pasta `prompts/` do seu projeto para experimentar variações específicas de uma técnica sem alterar o código original do Pangolin. O framework sempre dará prioridade em carregar os arquivos contidos na pasta do seu projeto.
