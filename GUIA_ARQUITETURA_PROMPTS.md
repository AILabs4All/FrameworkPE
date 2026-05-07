# Guia de Refatoração: Arquitectura Modular de Prompts com Schemas YAML

## Visão Geral

O FrameworkPE foi completamente refatorado para suportar uma arquitetura modular de técnicas de prompt engineering baseada em schemas YAML. Este guia descreve como o sistema funciona e como criar novas técnicas de prompt.

## Arquitetura

### Estrutura do Projeto

Cada projeto Pangolin agora possui a seguinte estrutura:

```
project_name/
├── data/           # Base de dados (CSV/JSON/XLSX)
├── model/          # Módulos de modelos de IA
├── prompts/        # Scripts Python de prompts (legado)
├── schema/         # Definições YAML das técnicas de prompt
├── logs/           # Logs de execução e métricas
├── output/         # Resultados das execuções
└── config.yaml     # Configuração do projeto
```

### Componentes Principais

1. **Schemas YAML** (`schema/`)
   - Definem técnicas de prompt de forma declarativa
   - Contêm prompts, parâmetros, exemplos e instruções

2. **Configurações de Prompt** (`config/prompt_config.py`)
   - Dataclasses que representam schemas carregados
   - Validação e conversão de dados

3. **Plugin Genérico** (`schema_prompt_plugin.py`)
   - Executa qualquer técnica de prompt definida por schema
   - Implementa estratégias genéricas

4. **Validador** (`prompt_schema_validator.py`)
   - Valida schemas YAML antes de uso

## Estrutura de um Schema YAML

### Exemplo: Progressive Hint

```yaml
technique: progressive_hint
name: "Progressive Hint"
description: "Gera dicas progressivas para melhorar a classificação"
acronym: "PPH"
strategy: progressive_hint

prompt_text: |
  {input_framework}
  {output_format}

hint_template: |
  Hint: The previous prediction was {previous_category}.
  Please reconsider: {input_framework}
  {output_format}

output_format: |
  If classification is not possible, return: Category: Unknown
  OUTPUT:
  Category: [NIST code]
  Explanation: [Justification]

params:
  max_hints: 4
  quality_threshold: 0.9
  mode: php

extraction:
  method: json
  unknown_category: UNKNOWN
```

### Campos Obrigatórios

- **technique**: Identificador único da técnica
- **name**: Nome descritivo
- **description**: Descrição da abordagem
- **acronym**: Acrônimo/código da técnica
- **strategy**: Tipo de implementação (progressive_hint, hypothesis_testing, etc.)
- **prompt_text**: Template do prompt principal com placeholders

### Campos Opcionais

- **output_format**: Formato esperado da resposta
- **params**: Parâmetros da técnica (iterations, thresholds, etc.)
- **extraction**: Configuração de como extrair dados da resposta
- **categories**: Lista de categorias NIST
- **examples**: Exemplos de classificação
- **key_words**: Palavras-chave por categoria (para HTP)
- **templates**: Templates adicionais (hint, masking, etc.)
- **input_builder**: Padrão de construção da entrada
- **metadata**: Metadados da técnica

## Placeholders Disponíveis

O sistema suporta os seguintes placeholders em templates:

- `{input_framework}`: Texto do incidente a classificar
- `{output_format}`: Formato esperado da saída
- `{category}`: Categoria sendo testada (HTP)
- `{keywords_str}`: Palavras-chave formatadas (HTP)
- `{previous_category}`: Categoria anterior (Progressive Hint)
- `{plan_instructions}`: Instruções de planejamento (Self Hint)
- `{rejected_category}`: Categorias rejeitadas (Rectification)
- Qualquer campo em `params` ou `metadata`

## Como Criar uma Nova Técnica

### Passo 1: Criar o Schema YAML

Crie um arquivo em `schema/nova_tecnica.yaml`:

```yaml
technique: nova_tecnica
name: "Minha Nova Técnica"
description: "Descrição completa"
acronym: "NT"
strategy: nova_tecnica  # Identifica qual executa

prompt_text: |
  Seu prompt aqui com placeholders.
  {input_framework}
  {output_format}

params:
  param1: valor1
  param2: valor2

extraction:
  method: json
```

### Passo 2: Criar a Classe de Configuração (Opcional)

Se precisar de lógica especial, crie em `config/prompt_config.py`:

```python
@dataclass
class MinhaTecnicaConfig(PromptConfig):
    param1: str = ""
    param2: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        base = PromptConfig.from_dict(data)
        return cls(
            # ... campos base ...
            param1=data.get("param1", ""),
            param2=int(data.get("params", {}).get("param2", 0))
        )
```

### Passo 3: Adicionar ao Factory

No `PromptConfigFactory`:

```python
class PromptConfigFactory:
    registry: Dict[str, Any] = {
        # ...
        "nova_tecnica": MinhaTecnicaConfig
    }
```

### Passo 4: Implementar Estratégia no Plugin

No `SchemaPromptPlugin`, adicione método:

```python
def _execute_nova_tecnica(self, incident_text: str, data_row, columns, **kwargs):
    # Sua implementação aqui
    return [{"categoria": "...", "explicacao": "..."}]
```

## Carregamento Automático de Schemas

Quando você:

1. Cria um novo projeto: schemas padrão são copiados automaticamente
2. Define técnicas em `config.yaml`: o sistema carrega os schemas correspondentes
3. Executa `pg run --technique nova_tecnica`: busca `schema/nova_tecnica.yaml`

## Validação de Schemas

Para validar todos os schemas de um projeto:

```python
from core.prompt_schema_validator import PromptSchemaValidator

results = PromptSchemaValidator.validate_directory("schema/")
PromptSchemaValidator.print_validation_report(results)
```

## Integração com o Framework

O framework carrega schemas automaticamente:

```python
# No comando 'run'
prompt_schema = project.load_prompt_schema(technique)
prompt_config = PromptConfigFactory.create(prompt_schema)
prompt_instance = SchemaPromptPlugin(model_instance, prompt_config)
results = prompt_instance.execute(prompt, row, columns, incident_id=incident_id)
```

## Benefícios da Arquitetura

1. **Sem Hardcoding**: Novas técnicas apenas via YAML
2. **Configurável**: Todos os parâmetros em schemas
3. **Extensível**: Factory pattern para novas estratégias
4. **Validável**: Schemas são validados antes de uso
5. **Genérico**: Um plugin executa qualquer técnica
6. **Independente**: Técnicas não dependem umas das outras

## Exemplos de Uso

### Adicionar Hypothesis Testing ao Projeto

1. Criar `schema/hypothesis_testing.yaml`
2. Em `config.yaml`, adicionar: `technique: [hypothesis_testing]`
3. Executar: `pg run`

### Criar Técnica Customizada

1. Criar `schema/minha_tecnica_customizada.yaml` com seu prompt
2. Implementar `_execute_minha_tecnica_customizada` no plugin (se necessário)
3. Usar em `config.yaml`

### Compartilhar Schemas

Copie o arquivo YAML para outro projeto no diretório `schema/`:

```bash
cp projeto1/schema/tecnica.yaml projeto2/schema/
```

## Troubleshooting

### "Schema not found"

- Verifique se o arquivo existe em `schema/`
- Verifique o nome em `config.yaml` vs `schema/*.yaml`
- Use `pg list-schemas` para listar disponíveis

### "Unknown strategy"

- Estratégia não está registrada no `PromptConfigFactory`
- Verifique o campo `strategy` no YAML
- Implemente `_execute_<strategy>` no plugin

### Validação falha

- Execute: `PromptSchemaValidator.validate_directory("schema/")`
- Revise os campos obrigatórios
- Cheque placeholders necessários

## Próximos Passos

1. Migre técnicas legais para schemas YAML
2. Crie técnicas customizadas via schemas
3. Compartilhe schemas entre projetos
4. Estenda com novas estratégias conforme necessário
