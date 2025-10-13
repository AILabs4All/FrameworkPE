# FreePrompt Plugin

Plugin de técnica de prompt flexível e direto para classificação de incidentes de segurança.

## Visão Geral

O **FreePromptPlugin** implementa uma abordagem direta e configurável para prompting, permitindo enviar prompts ao modelo sem modificações complexas, mas oferecendo flexibilidade através de parâmetros de configuração.

## Características Principais

### 🎯 **Simplicidade e Flexibilidade**
- Prompt direto sem iterações complexas
- Configurações opcionais para personalizar o comportamento
- Processamento inteligente de respostas

### 🧠 **Configurações Adaptáveis**
- **Exemplos**: Incluir/excluir exemplos de classificação
- **Saída estruturada**: Forçar formato específico de resposta
- **Dicas contextuais**: Gerar hints baseados no conteúdo do incidente
- **Temperatura**: Override da temperatura do modelo

### 📊 **Processamento Avançado**
- Extração automática de categoria e explicação
- Métodos de fallback para respostas não estruturadas
- Validação e limpeza de dados

## Configuração

### Configuração Padrão (JSON)
```json
{
  "free_prompt": {
    "plugin": "FreePromptPlugin",
    "description": "Free Prompting - Técnica de prompt direto e flexível",
    "default_params": {
      "use_examples": true,
      "use_structured_output": true,
      "use_context_hints": false,
      "temperature_override": null
    }
  }
}
```

### Parâmetros de Configuração

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `use_examples` | bool | `true` | Inclui exemplos de classificação no prompt |
| `use_structured_output` | bool | `true` | Força formato estruturado de saída |
| `use_context_hints` | bool | `false` | Gera dicas contextuais baseadas no incidente |
| `temperature_override` | float/null | `null` | Override da temperatura do modelo |

## Uso

### Linha de Comando
```bash
# Uso básico
python3 main.py data/ --columns "target" --model foundation_sec --technique free_prompt

# Com modelo local
python3 main.py data/ --columns "target" --model ollama_smollm2_360m --technique free_prompt
```

### Uso Programático
```python
from plugins.prompts.free_prompt import FreePromptPlugin
from plugins.models.hungguiface_model import HuggingfaceModel

# Configuração do modelo
model_config = {
    "plugin": "HuggingfaceModel",
    "model": "fdtn-ai/Foundation-Sec-8B",
    "temperature": 0.1
}

model = HuggingfaceModel(model_config)

# Configuração do plugin com parâmetros customizados
prompt_plugin = FreePromptPlugin(
    model,
    use_examples=True,
    use_structured_output=True,
    use_context_hints=True,
    temperature_override=0.2
)

# Execução
import pandas as pd
data_row = pd.Series({"incident": "Multiple failed SSH login attempts"})
results = prompt_plugin.execute("", data_row, ["incident"])
```

## Estrutura do Prompt

### Componentes do Prompt

1. **Prompt Base**: Definição do papel (cybersecurity expert)
2. **Categorias NIST**: Lista completa com descrições e exemplos
3. **Exemplos** (opcional): Casos de classificação para contexto
4. **Dicas Contextuais** (opcional): Hints baseados no conteúdo
5. **Formato de Saída**: Especificação do formato esperado

### Exemplo de Prompt Gerado

```
You are a cybersecurity expert specializing in incident classification.
Your task is to analyze security incidents and categorize them according to NIST guidelines.

NIST SECURITY INCIDENT CATEGORIES:

• CAT1: Account Compromise – Unauthorized access to user or administrator accounts
  Examples: credential phishing, SSH brute force, OAuth token theft
[... outras categorias ...]

CLASSIFICATION EXAMPLES:

Example 1:
Incident: "Multiple failed SSH login attempts detected from external IP"
Category: CAT12
Explanation: Network scanning and brute force attempts represent intrusion attempts...
[... outros exemplos ...]

ANALYSIS HINTS:
• Consider if this is an intrusion attempt (CAT12) or successful compromise (CAT1)

INCIDENT TO CLASSIFY:
[incident description]

REQUIRED OUTPUT FORMAT:
Category: [CAT1-CAT12 or Unknown]
Explanation: [Detailed justification for the chosen category]
```

## Processamento de Respostas

### Métodos de Extração

1. **Extração Principal**: Usa regex e JSON parsing da classe base
2. **Fallback**: Análise linha por linha para formatos alternativos
3. **Limpeza**: Normalização de categorias (CAT1-CAT12)

### Formato de Saída

```python
{
    "Response": "resposta bruta do modelo",
    "Processed": {
        "Category": "CAT5",
        "Explanation": "Justificativa detalhada..."
    },
    "Category": "CAT5",
    "Explanation": "Justificativa detalhada..."
}
```

## Exemplos de Configuração

### Configuração Minimalista
```python
FreePromptPlugin(
    model,
    use_examples=False,
    use_structured_output=False,
    use_context_hints=False
)
```

### Configuração Máxima
```python
FreePromptPlugin(
    model,
    use_examples=True,
    use_structured_output=True,
    use_context_hints=True,
    temperature_override=0.1
)
```

### Configuração para Modelos Pequenos
```python
FreePromptPlugin(
    model,
    use_examples=True,
    use_structured_output=True,
    use_context_hints=True,
    temperature_override=0.3  # Mais criatividade
)
```

## Vantagens

✅ **Simplicidade**: Não requer múltiplas iterações
✅ **Velocidade**: Execução única, rápida
✅ **Flexibilidade**: Configurável para diferentes cenários
✅ **Compatibilidade**: Funciona com qualquer modelo
✅ **Processamento Robusto**: Lida com diferentes formatos de resposta

## Limitações

⚠️ **Dependência do Modelo**: Qualidade varia conforme o modelo usado
⚠️ **Sem Refinamento**: Não há processo iterativo de melhoria
⚠️ **Contexto Limitado**: Depende apenas do prompt inicial

## Comparação com Outras Técnicas

| Aspecto | Free Prompt | Progressive Hint | Self Hint | Hypothesis Testing |
|---------|-------------|------------------|-----------|-------------------|
| Velocidade | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| Precisão | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Uso de Recursos | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| Configurabilidade | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ |

## Casos de Uso Recomendados

- **Prototipagem Rápida**: Testes iniciais de classificação
- **Modelos Grandes**: Quando o modelo já possui boa capacidade
- **Datasets Grandes**: Quando velocidade é prioridade
- **Baseline**: Como linha de base para comparação com outras técnicas
- **Recursos Limitados**: Quando tokens/tempo são restritos