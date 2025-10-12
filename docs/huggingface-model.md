# HuggingfaceModel

Implementação de modelo para usar modelos do HuggingFace Transformers diretamente no framework.

## Características

- **Compatibilidade**: Funciona com qualquer modelo do HuggingFace que suporte `AutoModelForCausalLM`
- **Flexibilidade de dispositivo**: Suporte automático para GPU (CUDA) e CPU
- **Configuração avançada**: Permite configurar parâmetros de loading e geração
- **Integração completa**: Mantém todas as funcionalidades do framework (logging, métricas, rate limiting)

## Configuração

### Configuração Básica

```json
{
  "provider": "huggingface",
  "model": "fdtn-ai/Foundation-Sec-8B",
  "temperature": 0.1,
  "max_tokens": 50,
  "device": "auto"
}
```

### Configuração Avançada

```json
{
  "provider": "huggingface",
  "model": "fdtn-ai/Foundation-Sec-8B",
  "model_path": "fdtn-ai/Foundation-Sec-8B",
  "temperature": 0.1,
  "max_tokens": 50,
  "device": "auto",
  "load_config": {
    "model": {
      "trust_remote_code": false,
      "low_cpu_mem_usage": true,
      "torch_dtype": "auto"
    },
    "tokenizer": {
      "trust_remote_code": false
    }
  }
}
```

## Parâmetros de Configuração

### Parâmetros Principais

- `model`: Nome do modelo no HuggingFace Hub
- `model_path`: Caminho alternativo para o modelo (padrão: usa `model`)
- `device`: Dispositivo para execução (`auto`, `cpu`, `cuda`)
- `temperature`: Temperatura para geração (0.0-2.0)
- `max_tokens`: Número máximo de tokens para gerar

### Parâmetros de Loading (`load_config`)

#### Modelo (`load_config.model`)
- `trust_remote_code`: Se deve confiar em código remoto
- `low_cpu_mem_usage`: Otimização de memória CPU
- `torch_dtype`: Tipo de dados do PyTorch (`auto`, `float16`, `float32`)
- `device_map`: Mapeamento de dispositivos para modelos grandes

#### Tokenizer (`load_config.tokenizer`)
- `trust_remote_code`: Se deve confiar em código remoto

## Uso

### Uso Básico

```python
from plugins.models.hungguiface_model import HuggingfaceModel

config = {
    "provider": "huggingface",
    "model": "fdtn-ai/Foundation-Sec-8B",
    "temperature": 0.1,
    "max_tokens": 50
}

model = HuggingfaceModel(config)
response = model.send_prompt("Seu prompt aqui")
print(response)
```

### Uso com Parâmetros Personalizados

```python
response = model.send_prompt(
    "Seu prompt aqui",
    max_new_tokens=10,
    do_sample=True,
    temperature=0.2,
    top_p=0.95,
    top_k=40
)
```

## Parâmetros de Geração

O modelo suporta os seguintes parâmetros durante `send_prompt()`:

- `max_new_tokens`: Máximo de novos tokens a gerar
- `max_tokens`: Alias para `max_new_tokens`
- `do_sample`: Se deve usar amostragem (padrão: True)
- `temperature`: Temperatura da geração
- `top_p`: Nucleus sampling threshold
- `top_k`: Top-k sampling threshold

## Exemplo Completo

Baseado no código de exemplo fornecido:

```python
# Configuração equivalente ao exemplo original
config = {
    "provider": "huggingface",
    "model": "fdtn-ai/Foundation-Sec-8B",
    "temperature": 0.1,
    "max_tokens": 3,
    "device": "auto"
}

prompt = '''CVE-2021-44228 is a remote code execution flaw in Apache Log4j2 via unsafe JNDI lookups ("Log4Shell"). The CWE is CWE-502.

CVE-2017-0144 is a remote code execution vulnerability in Microsoft's SMBv1 server ("EternalBlue") due to a buffer overflow. The CWE is CWE-119.

CVE-2014-0160 is an information-disclosure bug in OpenSSL's heartbeat extension ("Heartbleed") causing out-of-bounds reads. The CWE is CWE-125.

CVE-2017-5638 is a remote code execution issue in Apache Struts 2's Jakarta Multipart parser stemming from improper input validation of the Content-Type header. The CWE is CWE-20.

CVE-2019-0708 is a remote code execution vulnerability in Microsoft's Remote Desktop Services ("BlueKeep") triggered by a use-after-free. The CWE is CWE-416.

CVE-2015-10011 is a vulnerability about OpenDNS OpenResolve improper log output neutralization. The CWE is'''

model = HuggingfaceModel(config)
response = model.send_prompt(
    prompt,
    max_new_tokens=3,
    do_sample=True,
    temperature=0.1,
    top_p=0.9
)

print(response)
```

## Requisitos

- PyTorch
- Transformers
- Espaço suficiente em disco para o modelo
- GPU recomendada para modelos grandes

## Notas Importantes

1. **Primeira execução**: O modelo será baixado automaticamente do HuggingFace Hub
2. **Uso de memória**: Modelos grandes podem requerer bastante RAM/VRAM
3. **Performance**: GPU é altamente recomendada para modelos grandes
4. **Cache**: Modelos ficam em cache local após o primeiro download

## Troubleshooting

### Erro de memória insuficiente
- Use `device: "cpu"` para forçar CPU
- Configure `low_cpu_mem_usage: true` em `load_config.model`

### Modelo não encontrado
- Verifique se o nome do modelo está correto
- Confirme conectividade com internet para download

### Problemas de CUDA
- Verifique instalação do PyTorch com suporte CUDA
- Use `device: "cpu"` como fallback