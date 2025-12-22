# Pangolin - Framework de Teste e Comparacao de Prompts

Framework modular e extensivel para teste e comparacao sistematica de tecnicas de prompt engineering com multiplos modelos de linguagem (LLMs).

## Visao Geral

O Pangolin permite criar projetos isolados para testar e comparar diferentes tecnicas de prompt com diversos modelos de linguagem, mantendo dados, configuracoes, logs e resultados organizados em estruturas independentes.

### Principais Caracteristicas

- **Projetos Isolados**: Cada experimento tem estrutura propria de diretorios
- **Multiplos Modelos**: Suporte para API (OpenAI, Anthropic), Ollama, HuggingFace
- **Tecnicas Avancadas**: Progressive Hint, Self-Hint, Hypothesis Testing, Zero-Shot, e mais
- **Importacao Automatica**: Plugins de modelos e prompts copiados automaticamente
- **Metricas Completas**: Rastreamento de desempenho, custos e tokens
- **Formatos Flexiveis**: Exportacao em CSV, JSON, XLSX

---

## Instalacao

### 1. Instalar o Pacote

**Instalacao Global:**
```bash
cd FrameworkPE
pip install -e . --no-cache-dir
```

**Instalacao em Ambiente Virtual (Recomendado):**
```bash
cd FrameworkPE

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate  # Windows

# Atualizar pip, setuptools e wheel
pip install --upgrade pip setuptools wheel

# Instalar Pangolin
pip install -e . --no-cache-dir
```

**Nota**: Se houver erro de `AssertionError` durante instalação, primeiro atualize o pip:
```bash
python3 -m pip install --upgrade pip setuptools wheel
pip install -e . --no-cache-dir
```

### 2. Problema com Espacos no Caminho

Se o diretorio contem espacos (como "Area de Trabalho"), use o script wrapper:

```bash
# Em vez de 'pg', use './run_pg.sh'
./run_pg.sh init --name meu_projeto
./run_pg.sh apply
./run_pg.sh run

# OU crie um alias
alias pg='python3 /caminho/completo/pangolin_cli.py'
```

### 3. Desinstalar o Pangolin

Para remover completamente o Pangolin do sistema:

```bash
# Desinstalar o pacote
pip uninstall pangolin -y

# Opcional: Remover arquivos de configuracao do usuario
rm -rf ~/.pangolin

# Opcional: Remover alias se criou
# Edite seu ~/.bashrc ou ~/.zshrc e remova a linha do alias pg
```

**Nota**: A desinstalacao NAO remove seus projetos criados. Para remover um projeto especifico, use:

```bash
cd seu_projeto
../run_pg.sh destroy --name seu_projeto --force
```

---

## Uso Rapido

### Fluxo Completo em 5 Passos

```bash
# 1. Criar projeto
./run_pg.sh init --name meu_teste
cd meu_teste

# 2. Adicionar dados
cp seus_dados.csv data/

# 3. Configurar (opcional - editar config.yaml)
nano config.yaml

# 4. Aplicar configuracoes e importar plugins
../run_pg.sh apply

# 5. Executar processamento
../run_pg.sh run --verbose
```

### Saida do Comando Apply

```
Aplicando configuracoes do projeto 'meu_teste'...
Validacao da configuracao: OK

Validando disponibilidade de plugins...
   - Modelo 'ollama_gemma2:9b': OK (plugin: LocalModel)
   - Tecnica 'progressive_hint': OK (plugin: ProgressiveHintPlugin)

Arquivos importados:
   Modelos: local_model.py, base_model.py
   Prompts: progressive_hint.py, base_prompt.py

Configuracoes aplicadas com sucesso!
```

---

## Comandos Disponiveis

### pg init

Cria novo projeto com estrutura completa:

```bash
./run_pg.sh init --name nome_do_projeto
```

**O que cria:**
- `data/` - Arquivos de entrada (CSV, JSON, XLSX)
- `prompts/` - Prompts customizados (importados no apply)
- `model/` - Plugins de modelos (importados no apply)
- `logs/` - Logs de execucao e metricas
- `output/` - Resultados do processamento
- `config.yaml` - Configuracoes do projeto
- `README.md` - Documentacao do projeto

### pg apply

Valida configuracoes e importa plugins necessarios:

```bash
cd meu_projeto
../run_pg.sh apply
```

**O que faz:**
1. Valida estrutura do `config.yaml`
2. Verifica disponibilidade de plugins
3. **Importa automaticamente** arquivos de modelos para `model/`
4. **Importa automaticamente** arquivos de prompts para `prompts/`
5. Cria arquivos `__init__.py` necessarios

### pg run

Executa processamento de prompts:

```bash
# Usando configuracoes do config.yaml
../run_pg.sh run

# Sobrescrevendo parametros
../run_pg.sh run \
  --columns descricao severidade \
  --model ollama_llama3:8b \
  --technique self_hint \
  --output csv \
  --temperature 0.2 \
  --max-tokens 2048 \
  --verbose
```

**Opcoes:**
- `--columns` - Colunas dos dados para processar
- `--model` - Nome do modelo (sobrescreve config.yaml)
- `--technique` - Tecnica de prompt (sobrescreve config.yaml)
- `--output` - Formato: csv, json ou xlsx
- `--max-iterations` - Iteracoes maximas para tecnicas iterativas
- `--temperature` - Temperatura do modelo (0.0 a 1.0)
- `--max-tokens` - Maximo de tokens na resposta
- `--verbose, -v` - Saida detalhada

### pg info

Mostra informacoes do projeto atual:

```bash
../run_pg.sh info
```

**Saida:**
```
Informacoes do projeto 'meu_projeto':

Diretorios:
   Projeto: /caminho/completo/meu_projeto
   Data: /caminho/data (5 arquivos)
   Prompts: /caminho/prompts (3 arquivos)
   Model: /caminho/model (2 arquivos)
   Logs: /caminho/logs (10 arquivos)
   Output: /caminho/output (3 arquivos)

Configuracao:
   Modelo: ollama_gemma2:9b
   Tecnica: progressive_hint
```

### pg list

Lista todos os projetos:

```bash
./run_pg.sh list
```

### pg destroy

Remove projeto (requer confirmacao):

```bash
cd meu_projeto
../run_pg.sh destroy --name meu_projeto

# Ou sem confirmacao
../run_pg.sh destroy --name meu_projeto --force
```

---

## Estrutura de um Projeto

```
meu_projeto/
├── data/              # Arquivos de entrada
│   ├── dados.csv
│   └── incidentes.json
├── prompts/           # Plugins de prompts (importados automaticamente)
│   ├── __init__.py
│   ├── base_prompt.py
│   └── progressive_hint.py
├── model/             # Plugins de modelos (importados automaticamente)
│   ├── __init__.py
│   ├── base_model.py
│   └── local_model.py
├── logs/              # Logs e metricas
│   ├── pg-run_20251218_180530.log
│   └── performance_gemma2_progressive.json
├── output/            # Resultados
│   ├── resultados_gemma2_progressive.json
│   └── resultados_llama3_selfhint.csv
├── config.yaml        # Configuracoes do projeto
└── README.md          # Documentacao do projeto
```

---

## Modelos Suportados

### Ollama (Local - Recomendado)

```yaml
model:
  name: ollama_gemma2:9b
  provider: ollama
  temperature: 0.2
```

**Modelos disponiveis:**
- **Pequenos (7-10B)**: mistral:7b, llama3.1:8b, gemma2:9b, phi4:14b
- **Medios (14-32B)**: deepseek-r1:14b, granite3.2:8b, qwen3:32b
- **Grandes (70B+)**: llama3.3:70b, deepseek-r1:70b, cogito:70b

### API (Cloud)

```yaml
model:
  name: openai_gpt4
  provider: openai
  api_key: ${OPENAI_API_KEY}
```

**Providers suportados:**
- **OpenAI**: GPT-4, GPT-4-turbo, GPT-3.5-turbo
- **Anthropic**: Claude-3 (Opus, Sonnet, Haiku)
- **Google**: Gemini Pro, Gemini Ultra

### HuggingFace

```yaml
model:
  name: meta-llama/Llama-2-7b
  provider: huggingface
  model_path: /caminho/local/modelo
```

---

## Tecnicas de Prompt

### 1. Progressive Hint
Refinamento iterativo com hints progressivos para melhorar respostas.

```yaml
prompt:
  technique: progressive_hint
```

### 2. Progressive Rectification
Correcao progressiva de erros em respostas anteriores.

```yaml
prompt:
  technique: progressive_rectification
```

### 3. Self-Hint
Auto-geracao de hints pelo proprio modelo.

```yaml
prompt:
  technique: self_hint
```

### 4. Hypothesis Testing
Teste de multiplas hipoteses antes da resposta final.

```yaml
prompt:
  technique: hypothesis_testing
```

### 5. Free Prompt
Prompt livre totalmente customizavel.

```yaml
prompt:
  technique: free_prompt
```

### 6. Zero-Shot
Classificacao direta sem exemplos ou contexto adicional.

```yaml
prompt:
  technique: zeroshot
```

### Multiplas Tecnicas

```yaml
prompt:
  technique:
    - progressive_hint
    - self_hint
    - hypothesis_testing
```

---

## Configuracao Completa (config.yaml)

```yaml
project:
  name: meu_projeto
  description: Descricao do experimento
  version: 1.0.0

data:
  input_columns:
    - description
    - severity
    - category
  required_columns:
    - id
    - target

model:
  name: ollama_gemma2:9b
  provider: ollama
  temperature: 0.2
  max_tokens: 2048

prompt:
  technique: progressive_hint
  custom_prompts_dir: prompts
  
output:
  format: json
  save_metrics: true
  save_logs: true

nist_categories:
  enabled: true
```

---

## Exemplos Praticos

### Exemplo 1: Classificacao Basica

```bash
# Criar projeto
./run_pg.sh init --name classificacao_basica
cd classificacao_basica

# Adicionar dados
cp ~/incidentes.csv data/

# Configurar modelo e tecnica
cat > config.yaml << EOF
model:
  name: ollama_gemma2:9b
  temperature: 0.2
prompt:
  technique: progressive_hint
data:
  input_columns: [description]
output:
  format: json
EOF

# Executar
../run_pg.sh apply
../run_pg.sh run --verbose

# Ver resultados
ls output/
cat logs/performance_*.json
```

### Exemplo 2: Comparacao de Tecnicas

```bash
./run_pg.sh init --name comp_tecnicas
cd comp_tecnicas
cp ~/dados.csv data/

../run_pg.sh apply

# Testar diferentes tecnicas
../run_pg.sh run --technique progressive_hint --output csv
../run_pg.sh run --technique self_hint --output csv
../run_pg.sh run --technique hypothesis_testing --output csv

# Comparar resultados
ls -lh output/
```

### Exemplo 3: Comparacao de Modelos

```bash
./run_pg.sh init --name comp_modelos
cd comp_modelos
cp ~/dados.csv data/

../run_pg.sh apply

# Testar diferentes modelos
../run_pg.sh run --model ollama_llama3:8b --technique progressive_hint
../run_pg.sh run --model ollama_gemma2:9b --technique progressive_hint
../run_pg.sh run --model ollama_phi4:14b --technique progressive_hint

# Comparar metricas
cat logs/performance_llama3*.json
cat logs/performance_gemma2*.json
cat logs/performance_phi4*.json
```

### Exemplo 4: Experimento Completo

```bash
./run_pg.sh init --name experimento_completo
cd experimento_completo

# Configurar experimento
cat > config.yaml << EOF
project:
  name: experimento_completo
  description: Teste completo com multiplas configuracoes

model:
  name: ollama_gemma2:9b
  temperature: 0.2

prompt:
  technique:
    - progressive_hint
    - self_hint
    
data:
  input_columns: [description, severity, category]
  
output:
  format: json
  save_metrics: true
EOF

# Adicionar dados
cp ~/dataset_completo.csv data/

# Executar
../run_pg.sh apply
../run_pg.sh run --max-iterations 5 --verbose

# Analise de resultados
cat output/*.json | jq '.[] | {id, categoria, explicacao}'
```

---

## Metricas e Saidas

### Arquivos Gerados

#### Resultados
- `output/resultados_MODEL_TECHNIQUE.csv`
- `output/resultados_MODEL_TECHNIQUE.json`
- `output/resultados_MODEL_TECHNIQUE.xlsx`

#### Logs
- `logs/pg-run_TIMESTAMP.log`
- `logs/performance_MODEL_TECHNIQUE.json`

### Exemplo de Metricas

```json
{
  "total_tokens": 15234,
  "total_cost": 0.0045,
  "average_latency": 1.23,
  "requests_count": 100,
  "errors_count": 0,
  "model_used": "ollama_gemma2:9b",
  "technique_used": "progressive_hint",
  "timestamp": "2025-12-18T18:30:45"
}
```

---

## Troubleshooting

### Erro: "can't open file '/home/user/Area'"

**Causa**: Caminho contem espacos e o comando `pg` nao funciona.

**Solucao**: Use `./run_pg.sh` em vez de `pg`

```bash
./run_pg.sh init --name projeto
cd projeto
../run_pg.sh apply
```

### Erro: "Voce nao esta em um diretorio de projeto"

**Causa**: Executando comando que requer estar dentro do projeto.

**Solucao**: Entre no diretorio do projeto

```bash
cd meu_projeto
../run_pg.sh apply
```

### Erro: "Modelo nao encontrado"

**Causa**: Modelo nao esta instalado ou nome incorreto.

**Solucao**: Para Ollama, instale o modelo

```bash
# Listar modelos instalados
ollama list

# Instalar modelo
ollama pull gemma2:9b

# Verificar nome no config
../run_pg.sh apply  # Mostra modelos disponiveis
```

### Erro: "Nenhum arquivo encontrado em data/"

**Causa**: Diretorio data/ vazio.

**Solucao**: Adicione arquivos de dados

```bash
cp seus_dados.csv data/
ls data/  # Verificar
../run_pg.sh run
```

### Erro: "No module named 'torch'"

**Causa**: Tentando usar HuggingFace sem dependencias.

**Solucao**: Instale dependencias ou use Ollama/API

```bash
# Opcao 1: Instalar dependencias
pip install torch transformers

# Opcao 2: Usar Ollama (recomendado)
# Editar config.yaml:
model:
  provider: ollama
  name: ollama_gemma2:9b
```

### Arquivos nao importados no apply

**Causa**: Tecnica ou modelo nao mapeado.

**Solucao**: Verificar logs do apply

```bash
../run_pg.sh apply
# Verifica mensagens "Plugin importado"
ls model/ prompts/  # Confirmar arquivos
```

---

## Dicas e Melhores Praticas

### 1. Organizacao de Projetos

```bash
# Use nomes descritivos
./run_pg.sh init --name experimento_20251218_gemma2_progressive

# Agrupe projetos relacionados
mkdir experimentos_classificacao/
cd experimentos_classificacao/
../run_pg.sh init --name teste1
../run_pg.sh init --name teste2
```

### 2. Versionamento

```bash
# Versione seus configs
cp config.yaml config.yaml.v1
# Faca alteracoes
cp config.yaml config.yaml.v2

# Use git para projetos
cd meu_projeto
git init
git add .
git commit -m "Configuracao inicial"
```

### 3. Testes Incrementais

```bash
# Teste com amostra pequena primeiro
head -10 dados_completos.csv > data/amostra.csv
../run_pg.sh run --verbose

# Se OK, use dataset completo
cp dados_completos.csv data/
../run_pg.sh run
```

### 4. Comparacao Sistematica

```bash
# Crie script para comparar
cat > comparar.sh << 'EOF'
#!/bin/bash
for model in llama3:8b gemma2:9b phi4:14b; do
  ./run_pg.sh run --model ollama_$model --output json
done
EOF
chmod +x comparar.sh
```

### 5. Backup de Resultados

```bash
# Backup automatico
tar -czf backup_$(date +%Y%m%d).tar.gz output/ logs/

# Ou copie para local seguro
cp -r output/ ~/backups/projeto_$(date +%Y%m%d)/
```

---

## Requisitos do Sistema

### Minimos
- Python 3.8+
- 4GB RAM (para modelos via API)
- 500MB espaco em disco

### Recomendados para Ollama
- Python 3.10+
- 16GB RAM (modelos ate 14B)
- 32GB RAM (modelos 32B+)
- GPU NVIDIA com 8GB+ VRAM (opcional, acelera processamento)

### Dependencias Python

```txt
pandas>=2.1.4
pyyaml
tqdm
openai>=1.6.1
requests>=2.31.0
openpyxl>=3.1.2
litellm
rouge-score>=0.1.2
```

---

## Contribuindo

Contribuicoes sao bem-vindas! Areas prioritarias:

1. **Novas Tecnicas de Prompt**
   - Implementar novos plugins em `plugins/prompts/`
   - Documentar uso e parametros

2. **Suporte a Novos Providers**
   - Adicionar plugins em `plugins/models/`
   - Testar integracao

3. **Melhorias em Metricas**
   - Adicionar novas metricas de avaliacao
   - Visualizacao de resultados

4. **Documentacao**
   - Exemplos de uso
   - Tutoriais passo-a-passo

---

## Licenca

MIT License - veja LICENSE para detalhes

---

## Suporte

Para duvidas, problemas ou sugestoes:
- Abra uma issue no repositorio
- Consulte a documentacao em `docs/`
- Veja exemplos em `exemplo/`

---

## Roadmap

- [ ] Interface web para gerenciamento de projetos
- [ ] Comparacao automatica de resultados com graficos
- [ ] Suporte para mais providers (Cohere, AI21, etc)
- [ ] Sistema de templates de configuracao
- [ ] Cache de respostas para economia de tokens
- [ ] Exportacao de relatorios em PDF
- [ ] Integracao com MLflow para tracking

---

**Versao**: 2.0.0  
**Ultima atualizacao**: Dezembro 2025
