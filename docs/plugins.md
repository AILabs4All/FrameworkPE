# Sistema de Plugins

## Visão Geral

O **Sistema de Plugins** é o coração da extensibilidade do framework. Ele permite adicionar novos modelos de linguagem e técnicas de prompt sem modificar o código core, seguindo o princípio Open/Closed: aberto para extensão, fechado para modificação.

## Arquitetura de Plugins

### Tipos de Plugins

1. **Model Plugins** - Integração com diferentes provedores de LLM/SLM
2. **Prompt Plugins** - Técnicas de prompt engineering específicas

### Hierarquia de Classes

```
BaseModel (ABC)
├── APIModel
│   ├── OpenAI (GPT-3.5, GPT-4, etc.)
│   ├── HuggingFace (Transformers Hub)
│   ├── Anthropic (Claude)
│   └── Cohere (Command, Generate)
└── LocalModel
    └── Ollama (Llama, Mistral, DeepSeek, etc.)

BasePromptPlugin (ABC)
├── ProgressiveHintPlugin
├── SelfHintPlugin
├── ProgressiveRectificationPlugin
└── HypothesisTestingPlugin
```

## Plugins de Modelos

### BaseModel - Interface Base

Todos os plugins de modelo devem herdar de `BaseModel` e implementar os métodos abstratos.

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from plugins.models.base_model import BaseModel

class CustomModel(BaseModel):
    """Template para plugin de modelo personalizado."""
    
    def setup_model(self) -> None:
        """
        Configura dados específicos do modelo.
        
        Implementação obrigatória:
        - Configurar credenciais/endpoints
        - Inicializar cliente do provedor
        - Validar configurações
        """
        # Exemplo de implementação
        self.api_key = self.config.get("api_key")
        self.base_url = self.config.get("base_url", "https://api.example.com")
        self.custom_param = self.config.get("custom_param", "default")
        
        # Validação
        if not self.api_key:
            raise ValueError("API key é obrigatória")
            
        self.logger.info(
            "Modelo personalizado configurado: %s", 
            self.model_name
        )
    
    def send_prompt(self, prompt: str, **kwargs: Any) -> str:
        """
        Envia prompt e retorna resposta do modelo.
        
        Args:
            prompt: Texto do prompt
            **kwargs: Parâmetros opcionais (temperature, max_tokens, etc.)
            
        Returns:
            Resposta do modelo como string
        """
        mode = kwargs.get("mode", "default")
        
        try:
            # Aplica rate limiting se configurado
            self._apply_rate_limit(kwargs.get("rate_limit"))
            
            # Conta tokens de entrada
            input_tokens = self.count_tokens(prompt)
            
            # Chama API do modelo (implementação específica)
            response = self._call_model_api(prompt, **kwargs)
            
            # Conta tokens de saída
            output_tokens = self.count_tokens(response)
            
            # Registra métricas
            self._log_interaction(
                prompt, response, input_tokens, output_tokens, mode
            )
            
            return response
            
        except Exception as exc:
            self.logger.error("Erro ao chamar modelo: %s", exc)
            return f"Erro no modelo: {exc}"
    
    def _call_model_api(self, prompt: str, **kwargs) -> str:
        """Implementação específica da chamada à API."""
        # Implementar lógica específica do provedor
        # Exemplo usando requests:
        
        import requests
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {
            "prompt": prompt,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens)
        }
        
        response = requests.post(
            f"{self.base_url}/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()["text"]
```

### Exemplo: Plugin OpenAI Customizado

```python
# plugins/models/openai_custom.py
import openai
from .base_model import BaseModel

class OpenAICustomModel(BaseModel):
    """Plugin personalizado para OpenAI com configurações específicas."""
    
    def setup_model(self) -> None:
        self.api_key = self.config.get("api_key")
        if not self.api_key:
            raise ValueError("OpenAI API key é obrigatória")
            
        openai.api_key = self.api_key
        
        # Configurações específicas
        self.organization = self.config.get("organization")
        self.fine_tuned_model = self.config.get("fine_tuned_model")
        
        if self.organization:
            openai.organization = self.organization
            
        self.logger.info("OpenAI customizado configurado")
    
    def send_prompt(self, prompt: str, **kwargs: Any) -> str:
        mode = kwargs.get("mode", "default")
        
        try:
            self._apply_rate_limit()
            input_tokens = self.count_tokens(prompt)
            
            # Usa modelo fine-tuned se disponível
            model = self.fine_tuned_model or self.model_name
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                presence_penalty=kwargs.get("presence_penalty", 0),
                frequency_penalty=kwargs.get("frequency_penalty", 0)
            )
            
            content = response.choices[0].message.content
            output_tokens = self.count_tokens(content)
            
            self._log_interaction(
                prompt, content, input_tokens, output_tokens, mode
            )
            
            return content
            
        except Exception as exc:
            self.logger.error("Erro OpenAI: %s", exc)
            return f"Erro OpenAI: {exc}"
```

### Exemplo: Plugin para Provedor Local

```python
# plugins/models/local_custom.py
import requests
from .base_model import BaseModel

class LocalCustomModel(BaseModel):
    """Plugin para modelo rodando localmente."""
    
    def setup_model(self) -> None:
        self.endpoint = self.config.get("endpoint", "http://localhost:8000")
        self.model_path = self.config.get("model_path")
        
        # Testa conectividade
        try:
            response = requests.get(f"{self.endpoint}/health", timeout=5)
            response.raise_for_status()
            self.logger.info("Conexão com servidor local OK")
        except Exception as exc:
            self.logger.warning("Servidor local não disponível: %s", exc)
    
    def send_prompt(self, prompt: str, **kwargs: Any) -> str:
        try:
            self._apply_rate_limit(0.1)  # Rate limit baixo para local
            
            payload = {
                "prompt": prompt,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_length": kwargs.get("max_tokens", self.max_tokens)
            }
            
            response = requests.post(
                f"{self.endpoint}/generate",
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result.get("generated_text", "")
            
        except Exception as exc:
            self.logger.error("Erro modelo local: %s", exc)
            return f"Erro: {exc}"
```

## Plugins de Técnicas de Prompt

### BasePromptPlugin - Interface Base

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import pandas as pd
from plugins.prompts.base_prompt import BasePromptPlugin

class CustomPromptPlugin(BasePromptPlugin):
    """Template para plugin de técnica de prompt personalizada."""
    
    def get_name(self) -> str:
        """Retorna nome da técnica."""
        return "custom_technique"
    
    def execute(
        self,
        prompt: str,
        data_row: pd.Series,
        columns: List[str],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Executa técnica de prompt personalizada.
        
        Args:
            prompt: Prompt base construído pelo framework
            data_row: Linha de dados do incidente
            columns: Colunas sendo processadas
            **kwargs: Parâmetros específicos da técnica
            
        Returns:
            Lista de resultados da classificação
        """
        # Parâmetros configuráveis
        max_iterations = kwargs.get("max_iterations", 3)
        confidence_threshold = kwargs.get("confidence_threshold", 0.8)
        
        # Constrói informações do incidente
        incident_info = self.build_incident_info(data_row, columns)
        
        results = []
        
        try:
            # Executa lógica específica da técnica
            for iteration in range(max_iterations):
                # Modifica prompt para iteração atual
                iteration_prompt = self._build_iteration_prompt(
                    prompt, incident_info, iteration
                )
                
                # Chama modelo
                response = self.model_plugin.send_prompt(
                    iteration_prompt,
                    mode=f"custom_iteration_{iteration}"
                )
                
                # Processa resposta
                parsed_result = self._parse_response(response)
                
                # Verifica critério de parada
                if parsed_result.get("confidence", 0) >= confidence_threshold:
                    break
                    
                self.logger.debug(
                    "Iteração %d: confiança %.2f", 
                    iteration, 
                    parsed_result.get("confidence", 0)
                )
            
            # Resultado final
            final_result = {
                "informacoes_das_colunas": incident_info,
                "categoria": parsed_result.get("categoria", "UNKNOWN"),
                "explicacao": parsed_result.get("explicacao", "Sem explicação"),
                "confianca": parsed_result.get("confidence", 0.0),
                "iteracoes": iteration + 1,
                "tecnica": self.get_name(),
                "erro": False
            }
            
            results.append(final_result)
            
        except Exception as exc:
            self.logger.error("Erro na técnica personalizada: %s", exc)
            
            # Resultado de erro
            error_result = {
                "informacoes_das_colunas": incident_info,
                "categoria": "ERROR",
                "explicacao": f"Erro na execução: {str(exc)}",
                "erro": True
            }
            results.append(error_result)
        
        return results
    
    def _build_iteration_prompt(
        self, 
        base_prompt: str, 
        incident_info: str, 
        iteration: int
    ) -> str:
        """Constrói prompt específico para iteração."""
        if iteration == 0:
            return f"{base_prompt}\n\nIncidente: {incident_info}"
        else:
            return f"""
{base_prompt}

Incidente: {incident_info}

Esta é a iteração {iteration + 1}. Refine sua análise anterior 
considerando detalhes que podem ter sido perdidos.
"""
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parseia resposta do modelo."""
        # Implementar parsing específico
        # Exemplo simples usando regex ou NLP
        
        import re
        
        # Extrai categoria
        categoria_match = re.search(r'CAT(\d+)', response, re.IGNORECASE)
        categoria = f"CAT{categoria_match.group(1)}" if categoria_match else "UNKNOWN"
        
        # Extrai confiança (se presente)
        conf_match = re.search(r'confiança:?\s*(\d+\.?\d*)%?', response, re.IGNORECASE)
        confidence = float(conf_match.group(1)) / 100 if conf_match else 0.5
        
        return {
            "categoria": categoria,
            "explicacao": response,
            "confidence": confidence
        }
```

### Exemplo: Técnica de Validação por Consenso

```python
# plugins/prompts/consensus_validation.py
from .base_prompt import BasePromptPlugin
import random

class ConsensusValidationPlugin(BasePromptPlugin):
    """Valida classificação através de múltiplas execuções."""
    
    def get_name(self) -> str:
        return "consensus_validation"
    
    def execute(self, prompt: str, data_row: pd.Series, columns: List[str], **kwargs):
        num_runs = kwargs.get("num_runs", 3)
        consensus_threshold = kwargs.get("consensus_threshold", 0.6)
        
        incident_info = self.build_incident_info(data_row, columns)
        
        # Múltiplas execuções com variação
        classifications = []
        
        for run in range(num_runs):
            # Varia temperatura para obter diversidade
            temperature = 0.3 + (run * 0.2)
            
            response = self.model_plugin.send_prompt(
                f"{prompt}\n\nIncidente: {incident_info}",
                temperature=temperature,
                mode=f"consensus_run_{run}"
            )
            
            parsed = self._extract_category(response)
            classifications.append(parsed)
        
        # Calcula consenso
        category_counts = {}
        for classification in classifications:
            cat = classification["categoria"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # Encontra categoria mais votada
        most_voted = max(category_counts.items(), key=lambda x: x[1])
        consensus_ratio = most_voted[1] / num_runs
        
        # Determina resultado final
        if consensus_ratio >= consensus_threshold:
            final_category = most_voted[0]
            explanation = f"Consenso atingido ({consensus_ratio:.1%}): {final_category}"
        else:
            final_category = "UNCERTAIN"
            explanation = f"Sem consenso claro. Distribuição: {category_counts}"
        
        return [{
            "informacoes_das_colunas": incident_info,
            "categoria": final_category,
            "explicacao": explanation,
            "consenso": consensus_ratio,
            "distribuicao": category_counts,
            "execucoes": num_runs,
            "erro": False
        }]
    
    def _extract_category(self, response: str) -> Dict[str, Any]:
        """Extrai categoria da resposta."""
        import re
        match = re.search(r'CAT(\d+)', response, re.IGNORECASE)
        categoria = f"CAT{match.group(1)}" if match else "UNKNOWN"
        
        return {
            "categoria": categoria,
            "resposta": response
        }
```

## Registro e Descoberta de Plugins

### Registro Manual

```python
from core.plugin_manager import PluginManager
from plugins.models.custom_model import CustomModel
from plugins.prompts.custom_prompt import CustomPromptPlugin

# Inicializa gerenciador
plugin_manager = PluginManager()

# Registra plugins personalizados
plugin_manager.register_model_plugin("CustomModel", CustomModel)
plugin_manager.register_prompt_plugin("CustomPromptPlugin", CustomPromptPlugin)

# Lista plugins disponíveis
print("Modelos:", plugin_manager.list_available_models())
print("Prompts:", plugin_manager.list_available_prompts())
```

### Registro Automático

Para registro automático, você pode modificar o `PluginManager`:

```python
# core/plugin_manager.py
import importlib
import os
from pathlib import Path

class PluginManager:
    def __init__(self):
        # ... código existente ...
        self._discover_plugins()
    
    def _discover_plugins(self):
        """Descobre plugins automaticamente."""
        
        # Descobre plugins de modelo
        models_dir = Path("plugins/models")
        for file_path in models_dir.glob("*.py"):
            if file_path.stem not in ["__init__", "base_model"]:
                self._load_model_plugin(file_path)
        
        # Descobre plugins de prompt
        prompts_dir = Path("plugins/prompts")
        for file_path in prompts_dir.glob("*.py"):
            if file_path.stem not in ["__init__", "base_prompt"]:
                self._load_prompt_plugin(file_path)
    
    def _load_model_plugin(self, file_path: Path):
        """Carrega plugin de modelo automaticamente."""
        try:
            module_name = f"plugins.models.{file_path.stem}"
            module = importlib.import_module(module_name)
            
            # Procura classes que herdam de BaseModel
            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, type) and 
                    issubclass(obj, BaseModel) and 
                    obj != BaseModel):
                    
                    self.register_model_plugin(name, obj)
                    self.logger.info(f"Plugin descoberto: {name}")
                    
        except Exception as exc:
            self.logger.warning(f"Erro ao carregar plugin {file_path}: {exc}")
```

## Configuração de Plugins

### Estrutura de Configuração

```json
{
  "models": {
    "custom_openai": {
      "plugin": "OpenAICustomModel",
      "provider": "openai",
      "model": "gpt-4",
      "api_key": "${OPENAI_API_KEY}",
      "organization": "${OPENAI_ORG}",
      "fine_tuned_model": "ft:gpt-3.5-turbo:company:model:id",
      "temperature": 0.3,
      "max_tokens": 2000,
      "presence_penalty": 0.1,
      "frequency_penalty": 0.1
    },
    "local_custom": {
      "plugin": "LocalCustomModel",
      "provider": "local",
      "model": "custom-model-v1",
      "endpoint": "http://localhost:8000",
      "model_path": "/models/custom-model",
      "temperature": 0.7,
      "max_tokens": 1500
    }
  },
  "prompt_techniques": {
    "custom_technique": {
      "plugin": "CustomPromptPlugin",
      "description": "Técnica personalizada",
      "default_params": {
        "max_iterations": 5,
        "confidence_threshold": 0.85
      }
    },
    "consensus_validation": {
      "plugin": "ConsensusValidationPlugin",
      "description": "Validação por consenso",
      "default_params": {
        "num_runs": 3,
        "consensus_threshold": 0.67
      }
    }
  }
}
```

## Boas Práticas para Desenvolvimento de Plugins

### 1. Estrutura de Arquivos

```
plugins/
├── models/
│   ├── __init__.py
│   ├── base_model.py
│   ├── api_model.py
│   ├── local_model.py
│   └── custom_model.py       # Novo plugin
└── prompts/
    ├── __init__.py
    ├── base_prompt.py
    ├── progressive_hint.py
    └── custom_prompt.py       # Novo plugin
```

### 2. Nomenclatura

- **Classes:** `PascalCase` terminado em `Model` ou `Plugin`
- **Arquivos:** `snake_case.py`
- **Métodos:** `snake_case()`
- **Configuração:** `snake_case` nas chaves JSON

### 3. Logging e Métricas

```python
class CustomModel(BaseModel):
    def send_prompt(self, prompt: str, **kwargs) -> str:
        # SEMPRE registrar início
        self.logger.info("Processando prompt de %d caracteres", len(prompt))
        
        try:
            # Lógica do modelo
            response = self._process_prompt(prompt, **kwargs)
            
            # SEMPRE registrar sucesso
            self.logger.info("Resposta gerada: %d caracteres", len(response))
            return response
            
        except Exception as exc:
            # SEMPRE registrar erros
            self.logger.error("Falha no processamento: %s", exc)
            raise
```

### 4. Tratamento de Erros

```python
def send_prompt(self, prompt: str, **kwargs) -> str:
    try:
        # Validação de entrada
        if not prompt or not prompt.strip():
            raise ValueError("Prompt não pode ser vazio")
        
        # Processamento
        result = self._call_api(prompt, **kwargs)
        
        # Validação de saída
        if not result:
            self.logger.warning("Resposta vazia do modelo")
            return "Resposta não disponível"
            
        return result
        
    except requests.Timeout:
        return "Erro: Timeout na requisição"
    except requests.ConnectionError:
        return "Erro: Falha de conexão"
    except Exception as exc:
        self.logger.error("Erro inesperado: %s", exc)
        return f"Erro interno: {type(exc).__name__}"
```

### 5. Testes de Plugin

```python
# tests/test_custom_model.py
import pytest
from plugins.models.custom_model import CustomModel

class TestCustomModel:
    
    @pytest.fixture
    def model_config(self):
        return {
            "provider": "custom",
            "model": "test-model",
            "api_key": "test-key",
            "base_url": "http://localhost:8000"
        }
    
    @pytest.fixture
    def model(self, model_config):
        return CustomModel(model_config)
    
    def test_initialization(self, model):
        assert model.provider == "custom"
        assert model.model_name == "test-model"
    
    def test_send_prompt_success(self, model, monkeypatch):
        # Mock da API
        def mock_api_call(*args, **kwargs):
            return "Resposta do teste"
        
        monkeypatch.setattr(model, "_call_model_api", mock_api_call)
        
        result = model.send_prompt("Prompt de teste")
        assert result == "Resposta do teste"
    
    def test_send_prompt_error(self, model, monkeypatch):
        # Mock de erro
        def mock_api_error(*args, **kwargs):
            raise Exception("Erro simulado")
        
        monkeypatch.setattr(model, "_call_model_api", mock_api_error)
        
        result = model.send_prompt("Prompt de teste")
        assert "Erro no modelo" in result
```

## Exemplos de Integração

### Integração com Azure OpenAI

```python
# plugins/models/azure_openai.py
from .base_model import BaseModel
import openai

class AzureOpenAIModel(BaseModel):
    def setup_model(self) -> None:
        openai.api_type = "azure"
        openai.api_base = self.config.get("api_base")
        openai.api_version = self.config.get("api_version", "2023-05-15")
        openai.api_key = self.config.get("api_key")
        
        self.deployment_name = self.config.get("deployment_name")
        
        if not all([openai.api_base, openai.api_key, self.deployment_name]):
            raise ValueError("Configuração Azure incompleta")
    
    def send_prompt(self, prompt: str, **kwargs) -> str:
        try:
            response = openai.ChatCompletion.create(
                engine=self.deployment_name,  # Azure usa engine
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens)
            )
            
            return response.choices[0].message.content
            
        except openai.error.RateLimitError:
            return "Erro: Limite de taxa excedido"
        except openai.error.InvalidRequestError as exc:
            return f"Erro: Requisição inválida - {exc}"
```

### Integração com Anthropic Claude

```python
# plugins/models/anthropic_claude.py
import anthropic
from .base_model import BaseModel

class AnthropicClaudeModel(BaseModel):
    def setup_model(self) -> None:
        self.client = anthropic.Anthropic(
            api_key=self.config.get("api_key")
        )
        
    def send_prompt(self, prompt: str, **kwargs) -> str:
        try:
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text
            
        except Exception as exc:
            self.logger.error("Erro Anthropic: %s", exc)
            return f"Erro Anthropic: {exc}"
```

## Validação e Deploy de Plugins

### Script de Validação

```bash
#!/bin/bash
# scripts/validate_plugin.sh

PLUGIN_TYPE=$1  # model ou prompt
PLUGIN_NAME=$2

echo "Validando plugin $PLUGIN_TYPE/$PLUGIN_NAME..."

# Testa sintaxe Python
python -m py_compile plugins/${PLUGIN_TYPE}s/${PLUGIN_NAME}.py

# Executa testes específicos
python -m pytest tests/test_${PLUGIN_NAME}.py -v

# Valida contra interface
python scripts/validate_plugin_interface.py $PLUGIN_TYPE $PLUGIN_NAME

echo "Validação concluída!"
```

### Checklist de Plugin

- [ ] Herda da classe base apropriada
- [ ] Implementa todos os métodos abstratos
- [ ] Inclui tratamento de erro robusto
- [ ] Usa sistema de logging do framework
- [ ] Registra métricas apropriadas
- [ ] Inclui testes unitários
- [ ] Documentação no código
- [ ] Configuração de exemplo no JSON
- [ ] Validação de parâmetros de entrada

O sistema de plugins torna o framework extremamente flexível e extensível, permitindo integração com qualquer provedor de LLM e implementação de novas técnicas de prompt engineering de forma modular e mantível.