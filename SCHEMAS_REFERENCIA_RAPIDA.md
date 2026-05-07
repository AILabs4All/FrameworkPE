# Schema YAML para Técnicas de Prompt - Referência Rápida

## O que é um Schema?

Um schema YAML define completamente uma técnica de prompt engineering. Inclui o prompt, parâmetros, exemplos e configurações de validação.

## Template Mínimo

```yaml
technique: minha_tecnica
name: "Minha Técnica"
description: "O que ela faz"
acronym: "MT"
strategy: minha_tecnica
prompt_text: "{input_framework}\n{output_format}"
output_format: "Category: [CAT]\nExplanation: [reason]"
```

## Campos por Estratégia

### direct, zeroshot, free_prompt
```yaml
strategy: zeroshot
prompt_text: "..."
output_format: "..."
categories: [...]          # Opcional
examples: [...]            # Opcional
```

### hypothesis_testing
```yaml
strategy: hypothesis_testing
prompt_text: "..."
key_words:
  CAT1: [palavra1, palavra2]
  CAT2: [...]
params:
  max_iter: 12
  quality_threshold: 0.9
```

### progressive_hint
```yaml
strategy: progressive_hint
prompt_text: "..."
hint_template: "Hint: {previous_category}"
params:
  max_hints: 4
  quality_threshold: 0.9
```

### self_hint
```yaml
strategy: self_hint
prompt_text: "..."
plan_instructions: "Devisa um plano..."
params:
  max_iter: 4
  quality_threshold: 0.9
```

### progressive_rectification
```yaml
strategy: progressive_rectification
prompt_text: "..."
masking_template: "Replace '{subcategory}' with 'X'"
rectification_template: "Not: {rejected_category}"
key_words:
  CAT1: [...]
params:
  max_iter: 4
```

## Placeholders Essenciais

- `{input_framework}` - Texto do incidente
- `{output_format}` - Como formatar resposta
- `{category}` - Categoria testada (HTP)
- `{keywords_str}` - Palavras-chave (HTP)
- `{previous_category}` - Previsão anterior (Progressive Hint)
- `{plan_instructions}` - Instruções (Self Hint)

## Validação Automática

Campos obrigatórios sempre validados:
- `technique`
- `name`
- `description`
- `acronym`
- `strategy`
- `prompt_text`

Estratégia `hypothesis_testing` requer: `key_words`

## Exemplo Completo: Progressive Hint

```yaml
technique: progressive_hint
name: "Progressive Hint Prompting"
description: "Gera dicas progressivas para refinar a classificação"
acronym: "PPH"
strategy: progressive_hint

prompt_text: |
  Classifique o incidente:
  
  Incidente: {input_framework}
  
  {output_format}

hint_template: |
  Sua previsão anterior foi: {previous_category}
  Reconsidere e classifique novamente:
  
  Incidente: {input_framework}
  
  {output_format}

output_format: |
  Forneça a resposta no formato:
  Category: [CAT1-CAT12]
  Explanation: [Justificativa clara]

params:
  max_hints: 4
  quality_threshold: 0.9
  mode: php

extraction:
  method: json
  unknown_category: UNKNOWN
```

## Localização dos Schemas

- **Padrão do framework**: `pangolin/schemas/*.yaml`
- **Projeto específico**: `seu_projeto/schema/*.yaml`

Ordem de busca: Projeto → Framework

## Como Usar

1. Crie `seu_projeto/schema/tecnica.yaml`
2. Em `config.yaml`, adicione: `technique: [tecnica]`
3. Execute: `pg run`

## Validar Schema

```bash
python3 -c "
from pangolin.core.prompt_schema_validator import PromptSchemaValidator
results = PromptSchemaValidator.validate_directory('seu_projeto/schema/')
PromptSchemaValidator.print_validation_report(results)
"
```

## Exemplos Inclusos

- `hypothesis_testing.yaml` - Testa hipóteses sistematicamente
- `progressive_hint.yaml` - Refinamento iterativo com dicas
- `self_hint.yaml` - Auto-planejamento e refinamento
- `progressive_rectification.yaml` - Mascaramento e retificação
- `free_prompt.yaml` - Abordagem flexível com exemplos
- `zeroshot.yaml` - Classificação direta sem exemplos

## Dicas

1. Use `params` para valores numéricos configuráveis
2. Strings multi-linha com `|` no YAML
3. Placeholders usam `{nome}` sem `$`
4. Teste com `pg run --verbose` para debug
5. Valide antes de fazer push: `validate_directory()`
