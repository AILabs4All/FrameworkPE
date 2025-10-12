# Security Incident Classification Framework - Documentação

![Framework](https://img.shields.io/badge/Framework-Security%20Incident%20Classification-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![Architecture](https://img.shields.io/badge/Architecture-Plugin%20Based-orange)

## Visão Geral

O **Security Incident Classification Framework** é uma solução robusta e extensível para classificação automatizada de incidentes de segurança usando técnicas avançadas de prompt engineering e modelos de linguagem (LLM/SLM). O framework suporta múltiplos provedores (OpenAI, HuggingFace, Ollama) e implementa diversas técnicas de prompt para maximizar a precisão da classificação.

### Características Principais

- 🔌 **Arquitetura Pluginável**: Facilita extensão com novos modelos e técnicas
- 🌐 **Multi-Provider**: Suporte para APIs e modelos locais
- 📊 **Métricas Integradas**: Monitoramento de performance e uso de tokens
- 🛠️ **Scripts de Automação**: Facilita execução e integração
- 📝 **Logging Avançado**: Sistema de logs configurável e detalhado
- 🎯 **Classificação NIST**: Categorização baseada em padrões NIST

## Índice da Documentação

### 📖 Documentos Principais

- **[Arquitetura](architecture.md)** - Estrutura geral, fluxo de dados e componentes
- **[Classes e Métodos](classes.md)** - Detalhamento técnico de todas as classes
- **[Sistema de Plugins](plugins.md)** - Como estender o framework com novos plugins
- **[Scripts de Automação](scripts.md)** - Documentação dos scripts auxiliares
- **[Guia de Uso](usage.md)** - Instalação, configuração e execução
- **[Boas Práticas](best-practices.md)** - Diretrizes para desenvolvimento e extensão

### 🎯 Documentos Específicos

- **[Configuração](configuration.md)** - Detalhes do arquivo de configuração
- **[Técnicas de Prompt](prompt-techniques.md)** - Explicação das técnicas implementadas
- **[Tratamento de Dados](data-handling.md)** - Manipulação de arquivos e formatos
- **[Métricas e Logs](metrics-logs.md)** - Sistema de monitoramento e debug

## Início Rápido

### Pré-requisitos
- Python 3.8+
- pip ou conda para gerenciamento de pacotes

### Instalação Rápida
```bash
# Clone o repositório
git clone https://github.com/AILabs4All/FrameworkPE.git
cd security-incident-framework

# Instale dependências
pip install -r requirements.txt

# Execute exemplo básico
./scripts/run_ollama_classification.sh data/ \
  --columns "Pedido" \
  --model ollama_deepseek_15b \
  --technique progressive_hint \
  --output csv
```

### Estrutura do Projeto
```
security-incident-framework/
├── 📁 config/           # Configurações centralizadas
├── 📁 core/             # Núcleo do framework
├── 📁 plugins/          # Plugins de modelos e prompts
├── 📁 utils/            # Utilitários e helpers
├── 📁 scripts/          # Scripts de automação
├── 📁 data/             # Dados de entrada
├── 📁 docs/             # Documentação completa
├── 🐍 main.py           # Script principal
└── 📋 requirements.txt  # Dependências Python
```

## Exemplos de Uso

### Classificação com Modelo Local
```bash
./scripts/run_ollama_classification.sh data/ \
  --columns "description" \
  --model ollama_mistral \
  --technique self_hint \
  --output json
```

### Classificação com API OpenAI
```bash
python main.py data/ \
  --columns "incident_text" \
  --model openai_gpt4 \
  --technique progressive_rectification \
  --output xlsx
```

## Contribuindo

Para contribuir com o projeto:

1. Leia as [Boas Práticas](best-practices.md)
2. Consulte o [Sistema de Plugins](plugins.md) para extensões
3. Siga as diretrizes de [Configuração](configuration.md)
4. Utilize o sistema de [Métricas e Logs](metrics-logs.md) para debug

## Suporte

- 📚 Consulte a documentação completa nos links acima
- 🐛 Reporte bugs ou solicite funcionalidades via issues
- 💡 Contribua com melhorias via pull requests

---

**Versão:** 2.0.0  
**Última Atualização:** Setembro 2025  
**Licença:** [Especificar licença]
