# Pangolin — Referência de Schemas de Prompt

Este documento é a referência técnica completa para os schemas YAML que definem as técnicas de prompt do Pangolin. Para cada técnica são documentados: finalidade, funcionamento, quando usar, campos disponíveis e como customizar.

---

## Índice

- [O que é um Schema?](#o-que-é-um-schema)
- [Campos Comuns a Todos os Schemas](#campos-comuns-a-todos-os-schemas)
- [Técnicas Disponíveis](#técnicas-disponíveis)
  - [Zero-Shot](#1-zero-shot-zs)
  - [Free Prompt](#2-free-prompt-free)
  - [Progressive Hint](#3-progressive-hint-php)
  - [Self-Hint](#4-self-hint-shp)
  - [Hypothesis Testing](#5-hypothesis-testing-htp)
  - [Progressive Rectification](#6-progressive-rectification-prp)
- [Tabela de Placeholders](#tabela-de-placeholders)
- [Tabela de Campos por Estratégia](#tabela-de-campos-por-estratégia)
- [Template Mínimo](#template-mínimo)
- [Validação de Schemas](#validação-de-schemas)

---

## O que é um Schema?

Um schema YAML é um arquivo declarativo que define **completamente** uma técnica de prompt engineering: o texto do prompt, parâmetros de execução, templates auxiliares e regras de extração de resposta. O framework carrega o schema em tempo de execução e o executa sem necessidade de alterar código Python.

**Localização dos schemas:**

```
pangolin/schemas/         ← Schemas padrão (não modifique)
meu_projeto/schema/       ← Schemas do projeto (têm prioridade)
```

O framework busca primeiro no diretório `schema/` do projeto. Se não encontrar, usa o schema padrão do framework como fallback.

---

## Campos Comuns a Todos os Schemas

Estes campos são **obrigatórios** em qualquer schema:

| Campo | Tipo | Descrição |
|---|---|---|
| `technique` | string | Identificador único. Deve coincidir com o nome do arquivo `.yaml` |
| `name` | string | Nome legível da técnica (usado em logs e relatórios) |
| `description` | string | Descrição da abordagem e do que a técnica faz |
| `acronym` | string | Sigla curta (usada em colunas de saída e métricas) |
| `strategy` | string | Identifica qual método do plugin será executado |
| `prompt_text` | string (multiline) | Template do prompt principal |

Campos **opcionais** comuns:

| Campo | Tipo | Descrição |
|---|---|---|
| `output_format` | string | Bloco de instrução de formato de saída injetado via `{output_format}` |
| `params` | dict | Parâmetros numéricos e de controle da técnica |
| `extraction` | dict | Configuração de como extrair a resposta do modelo |
| `categories` | list | Lista de categorias de classificação |
| `examples` | list | Exemplos de pares entrada/saída |

---

## Técnicas Disponíveis

---

### 1. Zero-Shot (ZS)

**Arquivo:** `zeroshot.yaml` — **Estratégia:** `zeroshot`

#### Finalidade

Classifica o input em uma única chamada ao modelo, sem exemplos e sem refinamento iterativo. É a técnica mais simples e serve como **linha de base** para comparação com técnicas mais elaboradas.

#### Funcionamento

```
[system_prompt]
[categories_info]
INPUT: {input_framework}
[output_format]
```

Uma única chamada ao modelo. Sem iterações.

#### Quando usar

- Como ponto de partida para medir o ganho das outras técnicas
- Quando o tempo de execução é crítico (mínimo de chamadas à API)
- Para tarefas onde o modelo já demonstra boa performance sem auxílio

#### Schema completo

```yaml
technique: zeroshot
name: "Zero Shot"
description: "Zero-Shot Prompting - Técnica direta sem exemplos pré-definidos"
acronym: "ZS"
strategy: zeroshot

prompt_text: |
  {system_prompt}

  {categories_info}

  INPUT:
  {input_framework}

  {output_format}

system_prompt: |
  You are an expert analyst. Classify the input into the most appropriate
  category and justify your answer.

output_format: |
  REQUIRED OUTPUT FORMAT:
  Category: [category code or label]
  Explanation: [Detailed justification]

params:
  mode: zeroshot
  temperature_override: 0.0   # Temperatura 0 para máxima determinismo

categories: []  # Preencha com suas categorias

extraction:
  method: json
  unknown_category: UNKNOWN
```

#### Como customizar

**Definir categorias:**
```yaml
categories:
  - code: SPAM
    name: "Spam"
    description: "E-mail não solicitado ou publicitário"
  - code: LEGIT
    name: "Legítimo"
    description: "E-mail de comunicação interna ou esperada"
```

**Ajustar o system prompt:**
```yaml
system_prompt: |
  Você é um especialista em análise de e-mails corporativos.
  Classifique o e-mail recebido como SPAM ou LEGÍTIMO com justificativa.
```

---

### 2. Free Prompt (FREE)

**Arquivo:** `free_prompt.yaml` — **Estratégia:** `free_prompt`

#### Finalidade

Prompt configurável e flexível que suporta opcionalmente: lista de categorias, exemplos few-shot e dicas de contexto por palavras-chave. É o ponto de entrada ideal para experimentos iniciais com maior controle.

#### Funcionamento

```
[system_prompt]
CATEGORIES: [categories_info]
[examples_section]    ← incluído se use_examples=true
[context_hints]       ← incluído se use_context_hints=true
INPUT: {input_framework}
[output_format]
```

Uma única chamada ao modelo.

#### Quando usar

- Quando você quer controle total sobre a estrutura do prompt
- Quando possui exemplos rotulados para few-shot learning
- Para explorar rapidamente o desempenho com diferentes configurações

#### Schema completo

```yaml
technique: free_prompt
name: "Free Prompt"
description: "Free Prompting - Técnica flexível com exemplos e formatação configuráveis"
acronym: "FREE"
strategy: free_prompt

prompt_text: |
  {system_prompt}

  CATEGORIES:
  {categories_info}

  {examples_section}

  {context_hints}

  INPUT:
  {input_framework}

  {output_format}

system_prompt: |
  You are an expert analyst. Analyze the input and provide a classification
  with justification.

output_format: |
  REQUIRED OUTPUT FORMAT:
  Category: [category code or label]
  Explanation: [Detailed justification for the chosen category]

params:
  use_examples: false           # true para incluir examples_section
  use_structured_output: true
  use_context_hints: false      # true para incluir context_hints
  temperature_override: 0.2

categories: []    # Liste suas categorias aqui

examples: []      # Pares input/output de exemplo

context_hints: [] # Dicas ativadas por palavras-chave

extraction:
  method: json
  unknown_category: UNKNOWN
```

#### Como customizar

**Adicionar exemplos few-shot:**
```yaml
params:
  use_examples: true

examples:
  - input: "Oferta imperdível! Clique aqui para ganhar R$1000"
    output: "Category: SPAM\nExplanation: Linguagem de urgência com promessa de prêmio."
  - input: "Reunião de equipe amanhã às 14h na sala 3"
    output: "Category: LEGIT\nExplanation: Comunicação interna corporativa."
```

**Adicionar dicas de contexto:**
```yaml
params:
  use_context_hints: true

context_hints:
  - keywords: ["oferta", "grátis", "clique aqui", "urgente"]
    hint: "Palavras associadas a SPAM detectadas no texto."
  - keywords: ["reunião", "equipe", "interno", "relatório"]
    hint: "Indicadores de comunicação corporativa legítima."
```

---

### 3. Progressive Hint (PHP)

**Arquivo:** `progressive_hint.yaml` — **Estratégia:** `progressive_hint`

#### Finalidade

Refina a classificação iterativamente fornecendo ao modelo a predição da iteração anterior como uma "dica". O modelo é incentivado a reconsiderar sua resposta à luz do próprio resultado anterior.

#### Funcionamento

```
Iteração 1: prompt_text(input)                         → cat_1
Iteração 2: hint_template(input, previous=cat_1)       → cat_2
Iteração 3: hint_template(input, previous=cat_2)       → cat_3
...
Para após max_hints iterações ou ao atingir quality_threshold
```

#### Quando usar

- Quando o modelo tende a dar respostas imprecisas na primeira tentativa
- Para tarefas onde a consistência entre chamadas é importante
- Quando você deseja um mecanismo de auto-correção baseado em feedback

#### Schema completo

```yaml
technique: progressive_hint
name: "Progressive Hint"
description: "Progressive Hint Prompting - Gera dicas progressivas para melhorar a classificação"
acronym: "PHP"
strategy: progressive_hint

prompt_text: |
  {input_framework}

  {output_format}

hint_template: |
  Hint: The previous prediction was {previous_category}.
  Please reconsider the input and answer again.

  Input:
  {input_framework}

  {output_format}

output_format: |
  If classification is not possible, return:
  Category: Unknown
  Explanation: Unknown

  OUTPUT:
  Category: [category code or label]
  Explanation: [Justification for the chosen category]

params:
  max_hints: 4          # Número máximo de iterações de dica
  quality_threshold: 0.9 # Score mínimo para parar antecipadamente
  mode: php

extraction:
  method: json
  unknown_category: UNKNOWN
```

#### Como customizar

**Ajustar o hint_template:**
```yaml
hint_template: |
  Sua classificação anterior foi: {previous_category}.
  Revise o texto abaixo com atenção e reclassifique se necessário.

  Texto: {input_framework}

  {output_format}
```

**Reduzir iterações para economizar tokens:**
```yaml
params:
  max_hints: 2
  quality_threshold: 0.85
```

---

### 4. Self-Hint (SHP)

**Arquivo:** `self_hint.yaml` — **Estratégia:** `self_hint`

#### Finalidade

O modelo elabora um plano de análise antes de classificar. Em vez de receber dicas externas, o modelo cria suas próprias "dicas" estruturando um raciocínio passo a passo antes de emitir a resposta final.

#### Funcionamento

```
Iteração 1 (planejamento):
  prompt_text(input) + plan_instructions → plano_do_modelo

Iteração 2 (execução):
  prompt_text(input) + plano_do_modelo → resposta_final

...até max_iter ou quality_threshold
```

#### Quando usar

- Quando o raciocínio explícito (chain-of-thought) melhora a precisão na tarefa
- Para tarefas que requerem múltiplos passos de análise
- Quando você quer que o modelo demonstre seu processo de raciocínio

#### Schema completo

```yaml
technique: self_hint
name: "Self Hint"
description: "Self Hint Prompting - O modelo gera seu próprio plano e se auto-refina"
acronym: "SHP"
strategy: self_hint

prompt_text: |
  {input_framework}

  {plan_instructions}

  {output_format}

plan_instructions: |
  Let's first understand the problem and devise a plan to solve it step by step.
  Then execute the plan and classify the input accordingly.

output_format: |
  If classification is not possible, return:
  Category: Unknown
  Explanation: Unknown

  OUTPUT:
  Category: [category code or label]
  Explanation: [Justification for the chosen category]

params:
  max_iter: 4
  quality_threshold: 0.9
  mode: shp

extraction:
  method: json
  unknown_category: UNKNOWN
```

#### Como customizar

**Customizar as instruções de planejamento:**
```yaml
plan_instructions: |
  Antes de responder, siga este processo:
  1. Identifique as palavras-chave mais relevantes no texto.
  2. Liste os indicadores que apontam para cada categoria.
  3. Pese as evidências e chegue a uma conclusão fundamentada.
  Então emita sua classificação final.
```

---

### 5. Hypothesis Testing (HTP)

**Arquivo:** `hypothesis_testing.yaml` — **Estratégia:** `hypothesis_testing`

#### Finalidade

Testa sistematicamente hipóteses para cada categoria definida: para cada categoria, o modelo avalia se o input "pertence" ou "não pertence" a ela com base nas palavras-chave fornecidas. A categoria vencedora é aquela onde a hipótese verdadeira é suportada e a falsa é refutada.

#### Funcionamento

```
Para cada categoria em key_words:
  Prompt: "Para categoria {C} com palavras-chave {K}:
           H_true:  o input pertence a {C}? [SUPPORTED/NOT SUPPORTED]
           H_false: o input NÃO pertence a {C}? [SUPPORTED/NOT SUPPORTED]"

Decisão: categoria onde H_true=SUPPORTED e H_false=NOT SUPPORTED
Conflito: UNKNOWN
```

#### Quando usar

- Quando você tem categorias bem definidas com palavras-chave associadas
- Para tarefas de classificação onde o raciocínio por exclusão é adequado
- Quando precisa de explicabilidade detalhada por categoria

#### Schema completo

```yaml
technique: hypothesis_testing
name: "Hypothesis Testing"
description: "Hypothesis Testing Prompting - Testa hipóteses para cada categoria sistematicamente"
acronym: "HTP"
strategy: hypothesis_testing

prompt_text: |
  Input: "{input_framework}"

  Instructions:
  For category "{category}" (keywords: {keywords_str}), perform the following analysis:

  1. True Hypothesis:
    - Assume the input belongs to this category. Justify based on the description and keywords.
    - Indicate whether the hypothesis is SUPPORTED or NOT SUPPORTED.

  2. False Hypothesis:
    - Assume the input does NOT belong to this category. Justify based on the lack of evidence.
    - Indicate whether the hypothesis is SUPPORTED or NOT SUPPORTED.

  Return the hypotheses in the following format:
      True Hypothesis:[SUPPORTED/NOT SUPPORTED]
      False Hypothesis:[SUPPORTED/NOT SUPPORTED]

  Final Classification Decision:
    - If the True Hypothesis is SUPPORTED and the False Hypothesis is NOT SUPPORTED, return:
      Category: {category}
      Explanation: [Justification for the chosen category]
    - Otherwise, return:
      Category: UNKNOWN
      Explanation: UNKNOWN

output_format: "Category: [category code or label]\nExplanation: [Detailed justification]"

params:
  max_iter: 12          # Máximo de categorias a testar
  quality_threshold: 0.9

# OBRIGATÓRIO: defina suas categorias e palavras-chave
key_words:
  CategoryA:
    - keyword1
    - keyword2
  CategoryB:
    - keyword3
    - keyword4

extraction:
  method: json
  unknown_category: UNKNOWN
```

#### Como customizar

**Definir categorias para classificação de e-mails:**
```yaml
key_words:
  SPAM:
    - oferta
    - grátis
    - clique aqui
    - urgente
    - promoção
    - prêmio
  LEGIT:
    - reunião
    - relatório
    - equipe
    - projeto
    - prazo
    - cliente
```

> **Importante:** O campo `key_words` é **obrigatório** para a estratégia `hypothesis_testing`. O schema falhará na validação se estiver vazio.

---

### 6. Progressive Rectification (PRP)

**Arquivo:** `progressive_rectification.yaml` — **Estratégia:** `progressive_rectification`

#### Finalidade

Usa mascaramento progressivo de palavras-chave e retificação explícita para forçar o modelo a reconsiderar classificações. Mascara os termos da categoria escolhida no texto e pede reclassificação explicitando que a resposta anterior "provavelmente está errada".

#### Funcionamento

```
Iteração 1: prompt_text(input)                             → cat_1
  → Mascara palavras-chave de cat_1 no texto → input_m1

Iteração 2: rectification_template(input_m1, "not: cat_1") → cat_2
  → Mascara palavras-chave de cat_2 no texto → input_m2

Iteração 3: rectification_template(input_m2, "not: cat_1, cat_2") → cat_3
...até max_iter
```

#### Quando usar

- Quando o modelo tende a se prender à primeira resposta (âncora)
- Para explorar categorias alternativas de forma sistemática
- Quando o mascaramento de termos pode revelar classificações mais robustas

#### Schema completo

```yaml
technique: progressive_rectification
name: "Progressive Rectification"
description: "Progressive Rectification Prompting - Valida e retifica respostas usando mascaramento"
acronym: "PRP"
strategy: progressive_rectification

prompt_text: |
  {input_framework}

  {output_format}

masking_template: |
  Replace all occurrences of the word '{subcategory}' with 'X' in the input text.

rectification_template: |
  Input: {input_framework}
  The answer is probably not: {rejected_category}
  Let's think step by step to reclassify.

  {output_format}

output_format: |
  If classification is not possible, return:
  Category: Unknown
  Explanation: Unknown

  OUTPUT:
  Category: [category code or label]
  Explanation: [Justification for the chosen category]

params:
  max_iter: 4
  quality_threshold: 0.9
  mode: prp

# Palavras-chave para mascaramento por categoria
key_words:
  CategoryA:
    - keyword1
    - keyword2
  CategoryB:
    - keyword3

extraction:
  method: json
  unknown_category: UNKNOWN
```

#### Como customizar

**Ajustar o rectification_template:**
```yaml
rectification_template: |
  Texto: {input_framework}

  Nota: a resposta anterior ({rejected_category}) provavelmente está incorreta.
  Reconsidere cuidadosamente e apresente uma nova classificação.

  {output_format}
```

---

## Tabela de Placeholders

| Placeholder | Estratégias | Descrição |
|---|---|---|
| `{input_framework}` | Todas | Texto de entrada construído a partir das colunas configuradas |
| `{output_format}` | Todas | Bloco de instrução de formato de saída |
| `{system_prompt}` | `free_prompt`, `zeroshot` | System prompt configurável no schema |
| `{categories_info}` | `free_prompt`, `zeroshot` | Lista de categorias formatada automaticamente |
| `{examples_section}` | `free_prompt` | Bloco de exemplos few-shot (quando `use_examples=true`) |
| `{context_hints}` | `free_prompt` | Dicas por palavras-chave (quando `use_context_hints=true`) |
| `{plan_instructions}` | `self_hint` | Instruções para o modelo criar seu plano |
| `{previous_category}` | `progressive_hint` | Resultado da chamada anterior |
| `{category}` | `hypothesis_testing` | Categoria sendo testada na iteração atual |
| `{keywords_str}` | `hypothesis_testing` | Palavras-chave da categoria atual, formatadas como string |
| `{rejected_category}` | `progressive_rectification` | Categorias rejeitadas acumuladas |
| `{subcategory}` | `progressive_rectification` | Subcategoria para mascaramento no texto |

---

## Tabela de Campos por Estratégia

| Campo | `zeroshot` | `free_prompt` | `progressive_hint` | `self_hint` | `hypothesis_testing` | `progressive_rectification` |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `technique` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `name` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `description` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `acronym` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `strategy` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `prompt_text` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `output_format` | opt | opt | opt | opt | opt | opt |
| `system_prompt` | opt | opt | — | — | — | — |
| `categories` | opt | opt | — | — | — | — |
| `examples` | — | opt | — | — | — | — |
| `context_hints` | — | opt | — | — | — | — |
| `hint_template` | — | — | opt | — | — | — |
| `plan_instructions` | opt | — | — | opt | — | — |
| `key_words` | — | — | — | — | **req** | opt |
| `masking_template` | — | — | — | — | — | opt |
| `rectification_template` | — | — | — | — | — | opt |
| `params` | opt | opt | opt | opt | opt | opt |
| `extraction` | opt | opt | opt | opt | opt | opt |

`✓` = obrigatório · `opt` = opcional · `req` = obrigatório para esta estratégia · `—` = não aplicável

---

## Template Mínimo

O menor schema válido para qualquer estratégia:

```yaml
technique: minha_tecnica
name: "Minha Técnica"
description: "Descrição do que a técnica faz"
acronym: "MT"
strategy: minha_tecnica
prompt_text: "{input_framework}\n{output_format}"
output_format: "Category: [CAT]\nExplanation: [reason]"
```

---

## Validação de Schemas

Para validar os schemas de um projeto antes de executar:

```bash
python3 -c "
from pangolin.core.config.schema_validator import PromptSchemaValidator
results = PromptSchemaValidator.validate_directory('meu_projeto/schema/')
PromptSchemaValidator.print_validation_report(results)
"
```

O validador verifica:
- Presença de todos os campos obrigatórios
- Estratégia registrada no `PromptConfigFactory`
- Placeholders obrigatórios para a estratégia (ex: `{input_framework}` em `prompt_text`)
- `key_words` não-vazio para `hypothesis_testing`

### Erros comuns

| Erro | Causa | Solução |
|---|---|---|
| `"Schema not found"` | Arquivo `.yaml` não existe no diretório | Verifique o nome em `config.yaml` vs o nome do arquivo |
| `"Unknown strategy"` | Estratégia não registrada no Factory | Verifique o campo `strategy` no YAML |
| `"Missing required field"` | Campo obrigatório ausente | Adicione o campo indicado no erro |
| `"key_words required"` | `hypothesis_testing` sem `key_words` | Preencha o campo `key_words` com suas categorias |
| `"Missing placeholder"` | Placeholder obrigatório ausente no `prompt_text` | Adicione `{input_framework}` ao template |
