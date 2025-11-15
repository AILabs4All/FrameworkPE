# Framework de Classificação de Incidentes de Segurança

## Visão Geral

O **Framework de Classificação de Incidentes de Segurança** é uma solução plugável e extensível para classificação automatizada de incidentes de segurança cibernética usando técnicas avançadas de prompt engineering e diferentes modelos de linguagem (LLMs/SLMs).

### Características Principais

- **Arquitetura Plugável**: Sistema modular que permite adicionar novos modelos e técnicas facilmente
- **Múltiplos Provedores**: Suporte para OpenAI, Hugging Face, Ollama e outros via LiteLLM
- **Técnicas de Prompt Avançadas**: Implementação de Progressive Hint, Self Hint, Progressive Rectification e Hypothesis Testing
- **Classificação NIST**: Categorização automática seguindo padrões NIST (CAT1-CAT12)
- **Métricas Detalhadas**: Tracking de tokens, custos e performance
- **Configuração Flexível**: Sistema de configuração JSON/YAML com variáveis de ambiente

## Instalação Rápida

### Pré-requisitos

- Python 3.8+
- pip
- Git

### Setup Automatizado

```bash
# Clone o repositório
git clone <repository-url>
cd security-incident-framework

# Execute o script de setup
./create_framework.sh
```

### Setup Manual

```bash
# Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente (opcional)
cp .env.example .env
# Edite .env com suas chaves de API
```

## Uso

### Comando Básico

```bash
python main.py data/ --columns "descricao" --model openai_gpt4 --technique progressive_hint
```

### Exemplos Práticos

#### 1. Usando OpenAI GPT-4 com Progressive Hint
```bash
python main.py incidents/ \
  --columns "description" "severity" \
  --model openai_gpt4 \
  --technique progressive_hint \
  --output json \
  --max-iterations 5
```

#### 2. Usando Ollama Local com Self Hint
```bash
python main.py data/ \
  --columns "incident_description" \
  --model ollama_llama3 \
  --technique self_hint \
  --temperature 0.7 \
  --output xlsx
```

#### 2.1 Execução protegida com verificação automática (Ollama)
```bash
./scripts/run_ollama_classification.sh data/ \
  --columns "incident_description" \
  --model ollama_llama3 \
  --technique self_hint \
  --output csv
```

Esse wrapper shell:

- Verifica se o Ollama está instalado e instala automaticamente, se necessário
- Garante que o serviço `ollama serve` esteja disponível (inicia e encerra durante o fluxo)
- Confere se o modelo solicitado já está presente; caso contrário, faz o download
- Remove o modelo local após o término da classificação, evitando ocupar espaço em disco (`export OLLAMA_KEEP_MODELS=1` para manter)

#### 3. Usando Hugging Face com Hypothesis Testing
```bash
python main.py incidents/ \
  --columns "description" "type" "impact" \
  --model hf_bert \
  --technique hypothesis_testing \
  --max-tokens 512 \
  --verbose
```

### Comandos Informativos

```bash
# Listar modelos disponíveis
python main.py --list-models

# Listar técnicas disponíveis
python main.py --list-techniques

# Informações do framework
python main.py --info
```

## Configuração

### Estrutura de Configuração

O arquivo `config/default_config.json` define:

```json
{
  "framework": {
    "name": "Security Incident Classification Framework",
    "version": "2.0.0"
  },
  "models": {
    "openai_gpt4": {
      "plugin": "OpenAIModelPlugin",
      "provider": "openai",
      "model": "gpt-4-turbo",
      "api_key": "${OPENAI_API_KEY}",
      "temperature": 0.3
    },
    "ollama_llama3": {
      "plugin": "OllamaModelPlugin",
      "provider": "ollama",
      "model": "llama3:8b",
      "api_base": "http://localhost:11434"
    }
  },
  "prompt_techniques": {
    "progressive_hint": {
      "plugin": "ProgressiveHintPlugin",
      "default_params": {
        "max_iterations": 3,
        "rouge_threshold": 0.7
      }
    }
  }
}
```

### Variáveis de Ambiente

Crie um arquivo `.env` com suas credenciais:

```env
# OpenAI
OPENAI_API_KEY=sk-your-openai-key

# Hugging Face
HUGGINGFACE_API_TOKEN=hf_your-token

# Azure OpenAI (opcional)
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
```

## Arquitetura

### Estrutura do Projeto

```
security-incident-framework/
├── core/                    # Núcleo do framework
│   ├── framework.py         # Classe principal
│   ├── plugin_manager.py    # Gerenciador de plugins
│   └── config_loader.py     # Carregador de configurações
├── plugins/                 # Sistema de plugins
│   ├── models/              # Plugins de modelos
│   │   ├── base_model.py    # Classe base para modelos
│   │   ├── openai_model.py  # Plugin OpenAI
│   │   ├── ollama_model.py  # Plugin Ollama
│   │   └── huggingface_model.py # Plugin Hugging Face
│   └── prompts/             # Plugins de técnicas
│       ├── base_prompt.py   # Classe base para prompts
│       ├── progressive_hint.py
│       ├── self_hint.py
│       ├── progressive_rectification.py
│       └── hypothesis_testing.py
├── utils/                   # Utilitários
│   ├── logger.py           # Sistema de logging
│   ├── metrics.py          # Métricas e monitoramento
│   ├── file_handlers.py    # Manipulação de arquivos
│   └── security_extractor.py # Extração de categorias NIST
├── config/                  # Configurações
│   └── default_config.json  # Configuração padrão
├── data/                    # Dados de entrada
├── output/                  # Resultados
├── logs/                    # Arquivos de log
└── main.py                  # Ponto de entrada
```

### Fluxo de Execução

1. **Inicialização**: Carrega configurações e registra plugins
2. **Validação**: Verifica dados de entrada e parâmetros
3. **Processamento**: Executa técnica de prompt escolhida
4. **Classificação**: Aplica categorização NIST
5. **Resultados**: Salva em formato especificado
6. **Métricas**: Gera relatório de performance

## Técnicas de Prompt

### 1. Progressive Hint Prompting (PHP)
Melhora iterativamente as respostas através de dicas contextuais.

**Parâmetros:**
- `max_iterations`: Máximo de iterações (padrão: 3)
- `rouge_threshold`: Threshold para convergência (padrão: 0.7)

### 2. Self Hint Prompting (SHP)
O modelo gera suas próprias dicas para melhorar a classificação.

**Parâmetros:**
- `max_iterations`: Máximo de iterações (padrão: 3)

### 3. Progressive Rectification Prompting (PRP)
Corrige progressivamente erros de classificação identificados.

**Parâmetros:**
- `max_iterations`: Máximo de iterações (padrão: 3)
- `confidence_threshold`: Threshold de confiança (padrão: 0.8)

### 4. Hypothesis Testing Prompting (HTP)
Testa múltiplas hipóteses de classificação antes da decisão final.

**Parâmetros:**
- `num_hypotheses`: Número de hipóteses (padrão: 3)

## Categorias NIST

O framework classifica incidentes nas seguintes categorias:

| Código | Categoria | Descrição |
|--------|-----------|-----------|
| CAT1 | Account Compromise | Comprometimento de contas |
| CAT2 | Malware | Infecção por código malicioso |
| CAT3 | Denial of Service | Ataques de negação de serviço |
| CAT4 | Data Leak | Vazamento de dados sensíveis |
| CAT5 | Vulnerability Exploitation | Exploração de vulnerabilidades |
| CAT6 | Insider Abuse | Abuso interno |
| CAT7 | Social Engineering | Engenharia social |
| CAT8 | Physical Incident | Incidentes físicos |
| CAT9 | Unauthorized Modification | Modificações não autorizadas |
| CAT10 | Misuse of Resources | Uso indevido de recursos |
| CAT11 | Third-Party Issues | Problemas de terceiros |
| CAT12 | Intrusion Attempt | Tentativas de intrusão |

## Desenvolvendo Plugins

### Plugin de Modelo

```python
from plugins.models.base_model import BaseModelPlugin

class CustomModelPlugin(BaseModelPlugin):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Configuração específica
    
    def send_prompt(self, prompt: str, **kwargs) -> str:
        # Implementação da comunicação com o modelo
        pass
```

### Plugin de Técnica

```python
from plugins.prompts.base_prompt import BasePromptPlugin

class CustomPromptPlugin(BasePromptPlugin):
    def execute(self, prompt: str, incident_data: pd.Series, 
                columns: List[str], **params) -> List[Dict[str, Any]]:
        # Implementação da técnica
        pass
```

## Métricas e Monitoramento

O framework coleta automaticamente:

- **Tokens utilizados** por modelo e técnica
- **Custos estimados** baseados em preços de API
- **Tempo de processamento** por incidente
- **Taxa de sucesso** na classificação
- **Distribuição de categorias** NIST

### Visualização de Métricas

```python
from utils.metrics import MetricsCollector

collector = MetricsCollector()
summary = collector.log_performance_summary()
print(f"Total de tokens: {summary['total_tokens']}")
print(f"Custo total: ${summary['total_cost']:.4f}")
```

## Formatos Suportados

### Entrada
- **CSV**: Arquivos com delimitadores padrão
- **JSON**: Objetos e arrays
- **XLSX**: Planilhas Excel

### Saída
- **CSV**: Formato padrão para análise
- **JSON**: Estruturado para APIs
- **XLSX**: Para relatórios executivos

## Testes

```bash
# Executar todos os testes
python -m pytest tests/

# Testes específicos
python -m pytest tests/test_plugins.py -v

# Testes com coverage
python -m pytest --cov=core --cov=plugins tests/
```

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Diretrizes de Contribuição

- Siga PEP 8 para estilo de código Python
- Adicione testes para novas funcionalidades
- Atualize documentação quando necessário
- Use type hints em todas as funções públicas

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Suporte

### FAQ

**P: Como adicionar um novo provedor de LLM?**
R: Crie um plugin herdando de `BaseModelPlugin` e adicione a configuração no arquivo de config.

**P: O framework funciona offline?**
R: Sim, usando modelos locais via Ollama.

**P: Como customizar as categorias NIST?**
R: Modifique o arquivo `utils/security_extractor.py` e atualize a configuração.

### Contato

- **Issues**: Use o sistema de issues do GitHub
- **Documentação**: Wiki do projeto
- **Email**: [seu-email@exemplo.com]

## Agradecimentos

- [LiteLLM](https://docs.litellm.ai/) pela interface unificada de LLMs
- [Ollama](https://ollama.ai/) por facilitar uso de SLMs locais
- Comunidade NIST pelos padrões de classificação de incidentes