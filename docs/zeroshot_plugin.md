# ZeroShot Plugin

## Descrição

O **ZeroShotPlugin** implementa a técnica de **Zero-Shot Prompting** para classificação de incidentes de segurança cibernética.

### O que é Zero-Shot Prompting?

Zero-Shot Prompting é uma técnica onde o modelo é solicitado a realizar uma tarefa sem receber exemplos específicos (zero shots). O modelo recebe apenas:

1. **Definições claras das categorias** NIST (CAT1 a CAT12)
2. **Exemplos gerais** de cada categoria
3. **Termos de busca** associados a cada categoria
4. **Instruções claras** sobre o formato de saída esperado

### Características

- ✅ **Simples e direto**: Não requer múltiplas iterações
- ✅ **Eficiente**: Uma única chamada ao modelo
- ✅ **Escalável**: Funciona bem com diferentes tamanhos de modelos
- ✅ **Baseline**: Ideal para comparação com técnicas mais avançadas

### Estrutura do Prompt

```
1. Contexto: "You are a cybersecurity expert"
2. Tarefa: Classificar incidentes em categorias NIST
3. Categorias: Descrições detalhadas de CAT1-CAT12 com:
   - Nome da categoria
   - Descrição
   - Exemplos
   - Termos de busca
4. Incidente: Descrição do incidente a classificar
5. Formato de saída: Estrutura esperada (Category + Explanation)
```

### Uso

#### Via Linha de Comando

```bash
python main.py data/10_incidentes.xlsx \
  --columns "target" \
  --model ollama_deepseek_15b \
  --technique zeroshot \
  --output xlsx
```

#### Via API Python

```python
from core.plugin_manager import PluginManager
import pandas as pd

# Criar plugin manager
plugin_manager = PluginManager()

# Criar instância do modelo
model_config = {
    "provider": "ollama",
    "model": "deepseek-r1:1.5b",
    "temperature": 0.9,
    "max_tokens": 2000,
    "base_url": "http://localhost:11434"
}
model_instance = plugin_manager.create_model_instance("LocalModel", model_config)

# Criar instância do ZeroShotPlugin
zeroshot = plugin_manager.create_prompt_instance("ZeroShotPlugin", model_instance)

# Classificar incidente
data = pd.Series({
    'id': 'TEST-001',
    'target': 'Multiple failed SSH login attempts detected'
})

result = zeroshot.execute(
    prompt="",
    data_row=data,
    columns=['target'],
    incident_id='TEST-001'
)

print(f"Category: {result[0]['Category']}")
print(f"Explanation: {result[0]['Explanation']}")
```

### Configuração

No arquivo `config/default_config.json`:

```json
{
  "prompt_techniques": {
    "zeroshot": {
      "plugin": "ZeroShotPlugin",
      "description": "Zero-Shot Prompting - Técnica de prompt direto sem exemplos",
      "default_params": {}
    }
  }
}
```

### Comparação com Outras Técnicas

| Técnica | Iterações | Exemplos | Complexidade | Use Case |
|---------|-----------|----------|--------------|----------|
| **ZeroShot** | 1 | Não | Baixa | Baseline, testes rápidos |
| Free Prompt | 1 | Opcional | Baixa | Flexibilidade |
| Progressive Hint | 4+ | Sim | Média | Melhoria iterativa |
| Self Hint | 4+ | Não | Média | Auto-refinamento |
| Hypothesis Testing | 12+ | Não | Alta | Análise sistemática |

### Vantagens

✅ **Rápido**: Uma única chamada ao modelo  
✅ **Simples**: Fácil de entender e implementar  
✅ **Consistente**: Sempre usa o mesmo formato de prompt  
✅ **Baseline**: Ótimo ponto de partida para comparações  

### Desvantagens

❌ **Sem exemplos específicos**: Pode ter menor precisão em casos complexos  
❌ **Sem refinamento**: Não há oportunidade de melhorar a resposta iterativamente  
❌ **Dependente do modelo**: Requer modelos com boa capacidade de generalização  

### Testes

Execute o script de teste:

```bash
cd /home/magalu/Área\ de\ Trabalho/unipampa/security-incident/FrameworkPE
python test_zeroshot.py
```

### Exemplo de Saída

```
Input:
"Multiple failed SSH login attempts detected from external IP 192.168.1.100"

Output:
Category: CAT12
Explanation: This incident describes multiple failed SSH login attempts, which 
represents an intrusion attempt that was detected but not successful. The failed 
attempts indicate reconnaissance or brute force activity that was blocked, 
characteristic of CAT12 (Intrusion Attempt).
```

### Arquivos

- **Plugin**: `plugins/prompts/zeroshot_b.py`
- **Registro**: `core/plugin_manager.py`
- **Configuração**: `config/default_config.json`
- **Teste**: `test_zeroshot.py`
- **Documentação**: `docs/zeroshot_plugin.md`

### Autor

Desenvolvido como parte do Framework de Classificação de Incidentes de Segurança.

### Licença

Mesma licença do projeto principal.
