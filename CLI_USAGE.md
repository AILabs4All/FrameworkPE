# SICF CLI - Guia de Uso

## 📋 Descrição

CLI simples para o Security Incident Classification Framework configurável via YAML.

## 🚀 Instalação Rápida

```bash
# Certifique-se de que as dependências estão instaladas
pip install -r requirements.txt

# Torne o script executável
chmod +x sicf.py
```

## ⚙️ Configuração

Edite o arquivo `cli_config.yaml` para configurar modelos e técnicas:

```yaml
framework:
  name: "My Classifier"
  version: "1.0.0"

models:
  ollama_gemma2:
    plugin: "LocalModel"
    provider: "ollama"
    model: "gemma2:9b"
    temperature: 0.2
    base_url: "http://localhost:11434"

prompt_techniques:
  zeroshot:
    plugin: "ZeroShotPlugin"
  progressive_hint:
    plugin: "ProgressiveHintPlugin"
    default_params:
      max_hints: 4
```

## 💻 Comandos Disponíveis

### 1. Classificar Incidentes

```bash
./sicf.py classify \
  --config cli_config.yaml \
  --input data/ \
  --columns description \
  --model ollama_gemma2 \
  --technique progressive_hint \
  --format json
```

**Parâmetros:**
- `--config, -c`: Arquivo de configuração YAML (obrigatório)
- `--input, -i`: Arquivo ou diretório com incidentes (obrigatório)
- `--columns, -col`: Colunas a usar (obrigatório, pode ser múltiplas)
- `--model, -m`: Nome do modelo do config (obrigatório)
- `--technique, -t`: Nome da técnica do config (obrigatório)
- `--output, -o`: Arquivo de saída (opcional)
- `--format, -f`: Formato de saída: csv, json, xlsx (padrão: json)

**Exemplos:**

```bash
# Exemplo básico
./sicf.py classify -c cli_config.yaml -i data/ -col description -m ollama_gemma2 -t zeroshot

# Com múltiplas colunas
./sicf.py classify -c cli_config.yaml -i incidents.csv -col description severity source -m ollama_mistral -t self_hint

# Salvando em arquivo específico
./sicf.py classify -c cli_config.yaml -i data/ -col description -m ollama_deepseek -t progressive_hint -o results.json -f json
```

### 2. Listar Modelos Disponíveis

```bash
./sicf.py list-models --config cli_config.yaml
```

**Saída:**
```
📋 Available models:

  • ollama_gemma2
    Provider: ollama
    Model: gemma2:9b

  • ollama_mistral
    Provider: ollama
    Model: mistral:7b
```

### 3. Listar Técnicas Disponíveis

```bash
./sicf.py list-techniques --config cli_config.yaml
```

**Saída:**
```
🎯 Available techniques:

  • zeroshot
    Plugin: ZeroShotPlugin

  • progressive_hint
    Plugin: ProgressiveHintPlugin
```

### 4. Informações do Framework

```bash
./sicf.py info --config cli_config.yaml
```

**Saída:**
```
============================================================
  Security Incident Classification Framework
  Version: 2.0.0
============================================================

📊 Statistics:
   Models configured: 3
   Techniques configured: 5
   NIST categories: Enabled
```

## 📝 Exemplos Práticos

### Exemplo 1: Classificação Rápida (Zero-shot)

```bash
./sicf.py classify \
  -c cli_config.yaml \
  -i data/incidents.csv \
  -col description \
  -m ollama_gemma2 \
  -t zeroshot \
  -o quick_results.json
```

### Exemplo 2: Classificação com Múltiplas Colunas

```bash
./sicf.py classify \
  -c cli_config.yaml \
  -i data/ \
  -col description severity source_ip \
  -m ollama_mistral \
  -t progressive_hint \
  -o detailed_results.json
```

### Exemplo 3: Classificação Avançada

```bash
./sicf.py classify \
  -c cli_config.yaml \
  -i incidents.xlsx \
  -col incident_description \
  -m ollama_deepseek \
  -t hypothesis_testing \
  -o analysis.xlsx \
  -f xlsx
```

### Exemplo 4: Pipeline Completo

```bash
# 1. Verificar configuração
./sicf.py info -c cli_config.yaml

# 2. Listar modelos disponíveis
./sicf.py list-models -c cli_config.yaml

# 3. Listar técnicas
./sicf.py list-techniques -c cli_config.yaml

# 4. Classificar
./sicf.py classify \
  -c cli_config.yaml \
  -i data/new_incidents.csv \
  -col description \
  -m ollama_gemma2 \
  -t progressive_hint \
  -o results.json
```

## 🔧 Personalização

### Adicionar Novo Modelo

Edite `cli_config.yaml`:

```yaml
models:
  meu_modelo:
    plugin: "LocalModel"
    provider: "ollama"
    model: "llama2:7b"
    temperature: 0.3
    max_tokens: 1500
    base_url: "http://localhost:11434"
```

Depois use:
```bash
./sicf.py classify -c cli_config.yaml -i data/ -col description -m meu_modelo -t zeroshot
```

### Adicionar Nova Técnica

Edite `cli_config.yaml`:

```yaml
prompt_techniques:
  minha_tecnica:
    plugin: "FreePromptPlugin"
    default_params:
      custom_template: "Meu prompt personalizado"
```

## 📊 Formatos de Saída

### JSON
```json
{
  "id": "INC001",
  "categoria": "CAT1",
  "explicacao": "SSH brute force attack",
  "model": "ollama_gemma2",
  "technique": "progressive_hint"
}
```

### CSV
```csv
id,categoria,explicacao,model,technique
INC001,CAT1,SSH brute force attack,ollama_gemma2,progressive_hint
```

### XLSX
Planilha Excel com todas as colunas formatadas.

## 🐛 Debug

Para ver erros detalhados, adicione `--debug`:

```bash
./sicf.py classify -c cli_config.yaml -i data/ -col description -m ollama_gemma2 -t zeroshot --debug
```

## 📖 Categorias NIST

O framework classifica em 12 categorias:

- **CAT1**: Account Compromise
- **CAT2**: Malware
- **CAT3**: Denial of Service Attack
- **CAT4**: Data Leak
- **CAT5**: Vulnerability Exploitation
- **CAT6**: Insider Abuse
- **CAT7**: Social Engineering
- **CAT8**: Physical Incident
- **CAT9**: Unauthorized Modification
- **CAT10**: Misuse of Resources
- **CAT11**: Third-Party Issues
- **CAT12**: Intrusion Attempt

## 💡 Dicas

1. **Use zero-shot primeiro** para testes rápidos
2. **Use progressive_hint** para maior precisão
3. **Configure timeout** para modelos lentos
4. **Salve logs** para análise posterior
5. **Teste com poucos dados** antes de processar tudo

## 🆘 Ajuda

```bash
# Ajuda geral
./sicf.py --help

# Ajuda para comando específico
./sicf.py classify --help
```

## 📝 Requisitos

- Python 3.8+
- Ollama (para modelos locais)
- Dependências: `pip install -r requirements.txt`

## ⚡ Performance

- Zero-shot: ~2s por incidente
- Progressive hint: ~8s por incidente
- Hypothesis testing: ~15s por incidente

---

**Desenvolvido por AILabs4All** 🚀
