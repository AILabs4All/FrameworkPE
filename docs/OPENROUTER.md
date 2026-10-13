# Provider OpenRouter

O Pangolin integra o OpenRouter pelo plugin `OpenRouterModel`, usando LiteLLM
para enviar chamadas de chat. O provider é selecionado por
`models[].provider: openrouter`.

## Configuração mínima

Defina a chave no ambiente ou no `.env` do projeto:

```dotenv
OPENROUTER_API_KEY=sua-chave
```

Declare o identificador completo do modelo em `models[].name`. Em geral, ele
inclui o prefixo da organização, como `openai/gpt-5.2`:

```yaml
models:
  - name: openai/gpt-5.2
    provider: openrouter
    temperature: 0.2
    max_tokens: 1024
```

O plugin monta o identificador LiteLLM `openrouter/<models[].name>` e usa
`https://openrouter.ai/api/v1` como endpoint padrão. Para um gateway compatível
ou endpoint alternativo, configure `base_url` (ou `api_base`) no mesmo item.

## Atribuição da aplicação

O OpenRouter aceita cabeçalhos opcionais para identificar a aplicação. O plugin
oferece campos convenientes e também permite cabeçalhos adicionais:

```yaml
models:
  - name: openai/gpt-5.2
    provider: openrouter
    site_url: https://meu-dominio.example
    app_name: Experimento Pangolin
    extra_headers:
      X-OpenRouter-Categories: research
```

`site_url` é enviado como `HTTP-Referer`; `app_name`, como
`X-OpenRouter-Title`. Os itens de `extra_headers` são acrescentados aos dois.

## Parâmetros próprios do OpenRouter

Parâmetros adicionais aceitos pelo endpoint podem ser passados em
`extra_params`, que é encaminhado à chamada LiteLLM:

```yaml
models:
  - name: openai/gpt-5.2
    provider: openrouter
    extra_params:
      route: fallback
      models:
        - openai/gpt-5.2
        - anthropic/claude-sonnet-4.6
      provider:
        sort: price
      response_format:
        type: json_object
      plugins:
        - id: response-healing
```

Os nomes e valores precisam ser aceitos pelo endpoint e pelo modelo escolhido.
O Pangolin consome o texto em `choices[0].message.content`; respostas de tool
calls e streaming ainda não são convertidas em resultados do framework. Para
modo JSON, configure `response_format` conforme o suporte do modelo.

## Logs de uso

Quando a resposta inclui `usage`, o Pangolin grava esse objeto em cada interação
no arquivo JSON de `logs/`. Isso preserva os tokens nativos do modelo e campos
de custo retornados pelo OpenRouter. O resumo geral de métricas ainda usa a
contagem local de tokens; consulte o `provider_usage` da interação para os
valores retornados pela API.

## Resolução no framework

`openrouter` está registrado em `pangolin/core/plugin_manager.py`. O
`pg apply` valida esse provider e copia para `model/` os módulos
`openrouter_model.py`, `api_model.py` e `base_model.py`.
