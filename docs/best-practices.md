# Boas Práticas de Desenvolvimento

## Introdução

Este documento estabelece as melhores práticas para desenvolvimento, extensão e manutenção do Security Incident Classification Framework. Seguir essas diretrizes garante qualidade, performance, manutenibilidade e consistência no código.

## Estrutura de Código

### 1. Organização de Arquivos

#### Estrutura Recomendada
```
project/
├── core/                     # Funcionalidades principais
│   ├── __init__.py
│   ├── framework.py         # Classe principal
│   ├── plugin_manager.py    # Gerenciador de plugins
│   └── config_loader.py     # Carregamento de configurações
├── plugins/                 # Sistema de plugins
│   ├── models/             # Plugins de modelos
│   ├── prompts/            # Plugins de técnicas de prompt
│   └── __init__.py
├── utils/                  # Utilitários
│   ├── logger.py          # Sistema de logging
│   ├── metrics.py         # Métricas e monitoramento
│   └── file_handlers.py   # Manipulação de arquivos
├── config/                # Configurações
│   └── default_config.json
├── tests/                 # Testes
│   ├── unit/
│   ├── integration/  
│   └── fixtures/
├── docs/                  # Documentação
└── scripts/               # Scripts de automação
```

#### Convenções de Nomenclatura

**Arquivos Python:**
```python
# ✅ Correto
security_incident_framework.py
progressive_hint_plugin.py
file_handlers.py

# ❌ Incorreto  
SecurityIncidentFramework.py
progressive-hint-plugin.py
fileHandlers.py
```

**Classes:**
```python
# ✅ Correto
class SecurityIncidentFramework:
class ProgressiveHintPlugin:
class APIModel:

# ❌ Incorreto
class security_incident_framework:
class progressiveHintPlugin:
class Api_Model:
```

**Métodos e Variáveis:**
```python
# ✅ Correto
def load_configuration(self):
def classify_incident(self, text: str):
max_tokens = 2000
api_key = "sk-..."

# ❌ Incorreto
def LoadConfiguration(self):
def classifyIncident(self, text: str):
MaxTokens = 2000
API_KEY = "sk-..."
```

### 2. Documentação de Código

#### Docstrings Padrão
```python
def classify_incident(self, incident_text: str, technique: str = "progressive_hint") -> dict:
    """
    Classifica um incidente de segurança usando técnica especificada.
    
    Args:
        incident_text (str): Texto descritivo do incidente a ser classificado
        technique (str, optional): Técnica de prompt a usar. Defaults to "progressive_hint".
            Opções: 'progressive_hint', 'self_hint', 'progressive_rectification',
                   'hypothesis_testing'
    
    Returns:
        dict: Resultado da classificação contendo:
            - categoria (str): Categoria NIST identificada (ex: 'CAT1', 'CAT2')
            - explicacao (str): Justificativa detalhada da classificação
            - confianca (float): Nível de confiança 0.0-1.0
            - tecnica (str): Técnica de prompt utilizada
            - timestamp (str): Timestamp da classificação
            - erro (bool): Indica se houve erro no processamento
    
    Raises:
        PluginNotFoundError: Quando a técnica especificada não está disponível
        APIError: Quando há erro na comunicação com API do modelo
        ValidationError: Quando o texto de entrada é inválido
    
    Example:
        >>> framework = SecurityIncidentFramework()
        >>> resultado = framework.classify_incident(
        ...     "Malware detected on workstation", 
        ...     technique="progressive_hint"
        ... )
        >>> print(resultado['categoria'])
        'CAT2'
    """
```

#### Comentários Inline
```python
# ✅ Correto - Explicam o "por quê"
def preprocess_text(self, text: str) -> str:
    # Remove caracteres especiais que podem interferir na tokenização
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Normaliza espaços múltiplos para melhor consistência
    text = ' '.join(text.split())
    
    return text

# ❌ Incorreto - Explicam o "o quê" (óbvio)
def preprocess_text(self, text: str) -> str:
    # Remove caracteres especiais
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Divide e junta o texto
    text = ' '.join(text.split())
    
    return text
```

### 3. Type Hints

#### Uso Correto de Tipos
```python
from typing import Dict, List, Optional, Union, Tuple, Any
from pathlib import Path

# ✅ Correto - Tipos específicos
def load_config(self, config_path: Path) -> Dict[str, Any]:
    """Carrega configuração do arquivo especificado."""
    pass

def classify_batch(
    self, 
    incidents: List[str], 
    technique: str = "progressive_hint"
) -> List[Dict[str, Union[str, float, bool]]]:
    """Classifica múltiplos incidentes."""
    pass

def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
    """Retorna configuração do modelo ou None se não encontrado."""
    pass

# ❌ Incorreto - Tipos genéricos demais
def load_config(self, config_path) -> dict:
    pass

def classify_batch(self, incidents: list) -> list:
    pass
```

## Sistema de Plugins

### 1. Criação de Plugins

#### Interface Base Obrigatória
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BasePlugin(ABC):
    """Interface base para todos os plugins do framework."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa plugin com configuração.
        
        Args:
            config: Dicionário com configurações específicas do plugin
        """
        self.config = config
        self.name = self.__class__.__name__
        self.validate_config()
    
    @abstractmethod
    def validate_config(self) -> None:
        """Valida configuração do plugin. Deve levantar exceção se inválida."""
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Método principal de execução do plugin."""
        pass
    
    def get_info(self) -> Dict[str, str]:
        """Retorna informações básicas do plugin."""
        return {
            "name": self.name,
            "description": self.__doc__ or "Sem descrição",
            "version": getattr(self, 'VERSION', '1.0.0')
        }
```

#### Implementação de Plugin de Modelo
```python
class CustomAPIModel(BaseModel):
    """Plugin para modelo personalizado via API."""
    
    VERSION = "1.0.0"
    
    def validate_config(self) -> None:
        """Valida configuração específica do modelo."""
        required_fields = ['api_endpoint', 'api_key', 'model_name']
        
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Campo obrigatório ausente: {field}")
        
        # Validação adicional
        if not self.config['api_endpoint'].startswith(('http://', 'https://')):
            raise ValueError("API endpoint deve ser uma URL válida")
    
    def execute(self, prompt: str, **kwargs) -> str:
        """Executa chamada para o modelo."""
        try:
            response = self._make_api_call(prompt, **kwargs)
            return self._parse_response(response)
        except Exception as e:
            self.logger.error(f"Erro na execução do modelo {self.name}: {e}")
            raise
    
    def _make_api_call(self, prompt: str, **kwargs) -> dict:
        """Realiza chamada HTTP para a API."""
        # Implementação específica da API
        pass
    
    def _parse_response(self, response: dict) -> str:
        """Processa resposta da API."""
        # Implementação específica do parsing
        pass
```

### 2. Registro de Plugins

#### Sistema de Auto-descoberta
```python
import importlib
import pkgutil
from pathlib import Path

class PluginManager:
    """Gerenciador de plugins com auto-descoberta."""
    
    def discover_plugins(self, plugin_dirs: List[Path]) -> None:
        """Descobre automaticamente plugins nos diretórios especificados."""
        
        for plugin_dir in plugin_dirs:
            if not plugin_dir.exists():
                continue
                
            # Adiciona diretório ao sys.path temporariamente
            sys.path.insert(0, str(plugin_dir))
            
            try:
                # Descobre módulos no diretório
                for finder, name, ispkg in pkgutil.iter_modules([str(plugin_dir)]):
                    try:
                        module = importlib.import_module(name)
                        self._register_plugins_from_module(module)
                    except ImportError as e:
                        self.logger.warning(f"Erro ao importar plugin {name}: {e}")
            finally:
                # Remove diretório do sys.path
                sys.path.remove(str(plugin_dir))
    
    def _register_plugins_from_module(self, module) -> None:
        """Registra plugins encontrados em um módulo."""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            # Verifica se é uma classe plugin válida
            if (isinstance(attr, type) and 
                issubclass(attr, BasePlugin) and 
                attr != BasePlugin):
                    
                self.register_plugin(attr_name, attr)
                self.logger.info(f"Plugin registrado: {attr_name}")
```

### 3. Configuração de Plugins

#### Configuração Flexível
```python
# config/plugins.json
{
  "models": {
    "custom_api": {
      "plugin": "CustomAPIModel",
      "config": {
        "api_endpoint": "https://api.example.com/v1/completions",
        "api_key": "${CUSTOM_API_KEY}",
        "model_name": "custom-model-v1",
        "temperature": 0.7,
        "max_tokens": 2000,
        "timeout": 30,
        "retry_attempts": 3,
        "rate_limit": 1.0
      }
    }
  },
  "prompt_techniques": {
    "custom_technique": {
      "plugin": "CustomTechniquePlugin", 
      "config": {
        "max_iterations": 5,
        "confidence_threshold": 0.8,
        "fallback_technique": "progressive_hint"
      }
    }
  }
}
```

## Performance e Otimização

### 1. Gestão de Recursos

#### Pool de Conexões
```python
import asyncio
import aiohttp
from typing import AsyncGenerator

class AsyncAPIModel(BaseModel):
    """Modelo com suporte assíncrono e pool de conexões."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(
            config.get('max_concurrent_requests', 5)
        )
    
    async def __aenter__(self):
        """Context manager para gerenciar sessão HTTP."""
        connector = aiohttp.TCPConnector(
            limit=self.config.get('connection_pool_size', 10),
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        
        timeout = aiohttp.ClientTimeout(
            total=self.config.get('timeout', 30)
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup da sessão HTTP."""
        if self.session:
            await self.session.close()
    
    async def execute_batch(
        self, 
        prompts: List[str]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Executa múltiplos prompts de forma assíncrona."""
        
        tasks = []
        for prompt in prompts:
            task = self._execute_single_with_semaphore(prompt)
            tasks.append(task)
        
        # Processa em lotes para evitar sobrecarga
        batch_size = self.config.get('batch_size', 10)
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            results = await asyncio.gather(*batch, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    yield {"error": str(result)}
                else:
                    yield result
    
    async def _execute_single_with_semaphore(self, prompt: str) -> Dict[str, Any]:
        """Executa um prompt com controle de concorrência."""
        async with self.semaphore:
            return await self._execute_single(prompt)
```

#### Cache Inteligente
```python
import hashlib
import pickle
from functools import wraps
from pathlib import Path
from typing import Callable, Any

class CacheManager:
    """Gerenciador de cache com diferentes estratégias."""
    
    def __init__(self, cache_dir: Path, max_size_mb: int = 500):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
    
    def cached(self, ttl_hours: int = 24):
        """Decorator para cachear resultados de métodos."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                # Gera chave única baseada na função e argumentos
                cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                cache_file = self.cache_dir / f"{cache_key}.cache"
                
                # Verifica se cache existe e é válido
                if self._is_cache_valid(cache_file, ttl_hours):
                    try:
                        with open(cache_file, 'rb') as f:
                            return pickle.load(f)
                    except Exception:
                        # Cache corrompido, remove
                        cache_file.unlink(missing_ok=True)
                
                # Executa função e salva resultado
                result = func(self, *args, **kwargs)
                
                try:
                    with open(cache_file, 'wb') as f:
                        pickle.dump(result, f)
                    
                    # Limpa cache se necessário
                    self._cleanup_cache()
                    
                except Exception as e:
                    self.logger.warning(f"Erro ao salvar cache: {e}")
                
                return result
            return wrapper
        return decorator
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Gera chave única para cache."""
        key_data = {
            'function': func_name,
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = str(key_data).encode('utf-8')
        return hashlib.sha256(key_str).hexdigest()[:16]
```

### 2. Monitoramento de Performance

#### Métricas Detalhadas
```python
import time
import psutil
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class PerformanceMetrics:
    """Container para métricas de performance."""
    operation: str
    duration_seconds: float
    memory_usage_mb: float
    cpu_usage_percent: float
    tokens_processed: Optional[int] = None
    api_calls: Optional[int] = None
    errors: int = 0

class PerformanceMonitor:
    """Monitor de performance com coleta de métricas."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.process = psutil.Process()
    
    @contextmanager
    def measure(self, operation: str):
        """Context manager para medir performance de operações."""
        # Métricas iniciais
        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024
        start_cpu = self.process.cpu_percent()
        
        try:
            yield self
        finally:
            # Métricas finais
            end_time = time.time()
            end_memory = self.process.memory_info().rss / 1024 / 1024
            end_cpu = self.process.cpu_percent()
            
            metrics = PerformanceMetrics(
                operation=operation,
                duration_seconds=end_time - start_time,
                memory_usage_mb=end_memory - start_memory,
                cpu_usage_percent=(start_cpu + end_cpu) / 2
            )
            
            self.metrics.append(metrics)
    
    def get_report(self) -> Dict[str, Any]:
        """Gera relatório de performance."""
        if not self.metrics:
            return {"message": "Nenhuma métrica coletada"}
        
        operations = {}
        for metric in self.metrics:
            if metric.operation not in operations:
                operations[metric.operation] = []
            operations[metric.operation].append(metric)
        
        report = {}
        for operation, metrics_list in operations.items():
            durations = [m.duration_seconds for m in metrics_list]
            memories = [m.memory_usage_mb for m in metrics_list]
            
            report[operation] = {
                "total_executions": len(metrics_list),
                "avg_duration": sum(durations) / len(durations),
                "max_duration": max(durations),
                "min_duration": min(durations),
                "avg_memory_usage": sum(memories) / len(memories),
                "total_errors": sum(m.errors for m in metrics_list)
            }
        
        return report
```

### 3. Rate Limiting

#### Controle de Taxa Adaptivo
```python
import asyncio
import time
from collections import defaultdict, deque
from typing import Dict, Deque

class AdaptiveRateLimiter:
    """Rate limiter adaptivo baseado em resposta da API."""
    
    def __init__(self, initial_rate: float = 1.0):
        self.rates: Dict[str, float] = defaultdict(lambda: initial_rate)
        self.last_requests: Dict[str, Deque[float]] = defaultdict(lambda: deque())
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.success_counts: Dict[str, int] = defaultdict(int)
    
    async def acquire(self, provider: str) -> None:
        """Aguarda permissão para fazer requisição."""
        current_rate = self.rates[provider]
        
        # Limpa requests antigos (última hora)
        cutoff_time = time.time() - 3600
        requests_queue = self.last_requests[provider]
        
        while requests_queue and requests_queue[0] < cutoff_time:
            requests_queue.popleft()
        
        # Verifica se precisa aguardar
        if len(requests_queue) >= current_rate * 3600:  # requests/hour
            sleep_time = (requests_queue[0] + 3600/current_rate) - time.time()
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        # Registra request
        requests_queue.append(time.time())
    
    def report_success(self, provider: str) -> None:
        """Reporta sucesso na requisição."""
        self.success_counts[provider] += 1
        
        # Aumenta taxa gradualmente se há muitos sucessos
        if self.success_counts[provider] % 10 == 0:
            self.rates[provider] *= 1.1  # Aumento de 10%
    
    def report_error(self, provider: str, error_type: str = "rate_limit") -> None:
        """Reporta erro na requisição."""
        self.error_counts[provider] += 1
        
        if error_type == "rate_limit":
            # Reduz taxa agressivamente para rate limit
            self.rates[provider] *= 0.5
        else:
            # Reduz taxa moderadamente para outros erros
            self.rates[provider] *= 0.9
        
        # Garante taxa mínima
        self.rates[provider] = max(0.1, self.rates[provider])
```

## Testes e Qualidade

### 1. Estratégia de Testes

#### Estrutura de Testes
```
tests/
├── unit/                    # Testes unitários
│   ├── test_framework.py
│   ├── test_plugins.py
│   └── test_utils.py
├── integration/            # Testes de integração
│   ├── test_api_models.py
│   ├── test_ollama_integration.py
│   └── test_workflow.py
├── fixtures/               # Dados de teste
│   ├── sample_incidents.json
│   ├── config_test.json
│   └── mock_responses/
├── conftest.py            # Configuração pytest
└── performance/           # Testes de performance
    ├── test_load.py
    └── test_memory.py
```

#### Testes Unitários Exemplares
```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from core.framework import SecurityIncidentFramework
from plugins.models.openai_model import OpenAIModel

class TestSecurityIncidentFramework:
    """Testes unitários para classe principal."""
    
    @pytest.fixture
    def framework(self):
        """Fixture com framework configurado para testes."""
        config = {
            "models": {
                "test_model": {
                    "plugin": "MockModel",
                    "provider": "test",
                    "model": "test-model"
                }
            },
            "prompt_techniques": {
                "test_technique": {
                    "plugin": "MockTechnique"
                }
            }
        }
        return SecurityIncidentFramework(config)
    
    def test_classify_incident_success(self, framework):
        """Testa classificação bem-sucedida."""
        # Arrange
        incident_text = "Malware detected on workstation"
        expected_result = {
            "categoria": "CAT2",
            "explicacao": "Malware infection detected",
            "confianca": 0.95,
            "erro": False
        }
        
        # Mock do modelo
        mock_model = Mock()
        mock_model.execute.return_value = "CAT2: Malware infection detected (confidence: 0.95)"
        framework.plugin_manager.get_plugin.return_value = mock_model
        
        # Act
        result = framework.classify_incident(incident_text, "test_technique")
        
        # Assert
        assert result["categoria"] == expected_result["categoria"]
        assert result["confianca"] == expected_result["confianca"]
        assert result["erro"] == expected_result["erro"]
        mock_model.execute.assert_called_once()
    
    def test_classify_incident_api_error(self, framework):
        """Testa comportamento com erro de API."""
        # Arrange
        incident_text = "Test incident"
        
        mock_model = Mock()
        mock_model.execute.side_effect = Exception("API Error")
        framework.plugin_manager.get_plugin.return_value = mock_model
        
        # Act
        result = framework.classify_incident(incident_text, "test_technique")
        
        # Assert
        assert result["erro"] == True
        assert "API Error" in result["explicacao"]
    
    @pytest.mark.parametrize("input_text,expected_category", [
        ("Malware detected", "CAT2"),
        ("Failed login attempts", "CAT1"), 
        ("DDoS attack detected", "CAT3"),
        ("Data breach occurred", "CAT4")
    ])
    def test_classify_different_incident_types(self, framework, input_text, expected_category):
        """Testa classificação de diferentes tipos de incidente."""
        # Mock configurado para retornar categoria esperada
        mock_model = Mock()
        mock_model.execute.return_value = f"{expected_category}: Test classification"
        framework.plugin_manager.get_plugin.return_value = mock_model
        
        result = framework.classify_incident(input_text, "test_technique")
        
        assert result["categoria"] == expected_category
```

#### Testes de Integração
```python
import pytest
import requests_mock
from plugins.models.openai_model import OpenAIModel

class TestOpenAIIntegration:
    """Testes de integração com API OpenAI."""
    
    @pytest.fixture
    def openai_model(self):
        """Fixture com modelo OpenAI configurado."""
        config = {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "api_key": "test-key",
            "temperature": 0.7
        }
        return OpenAIModel(config)
    
    @requests_mock.Mocker()
    def test_successful_api_call(self, m, openai_model):
        """Testa chamada bem-sucedida para API OpenAI."""
        # Mock da resposta da API
        mock_response = {
            "choices": [{
                "message": {
                    "content": "CAT2: Malware infection detected on workstation"
                }
            }],
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 25
            }
        }
        
        m.post("https://api.openai.com/v1/chat/completions", json=mock_response)
        
        # Executa classificação
        result = openai_model.execute("Test prompt")
        
        # Verifica resultado
        assert "CAT2" in result
        assert "Malware infection" in result
    
    @requests_mock.Mocker() 
    def test_rate_limit_handling(self, m, openai_model):
        """Testa tratamento de rate limit."""
        # Mock de resposta de rate limit
        m.post(
            "https://api.openai.com/v1/chat/completions",
            status_code=429,
            json={"error": {"message": "Rate limit exceeded"}}
        )
        
        # Verifica se exceção apropriada é levantada
        with pytest.raises(Exception) as exc_info:
            openai_model.execute("Test prompt")
        
        assert "Rate limit" in str(exc_info.value)
```

### 2. Coverage e Qualidade

#### Configuração de Coverage
```python
# .coveragerc
[run]
source = core, plugins, utils
omit = 
    tests/*
    venv/*
    */__pycache__/*
    */migrations/*
    manage.py
    setup.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    class .*\(Protocol\):
    @(abc\.)?abstractmethod

precision = 2
show_missing = True

[html]
directory = htmlcov
```

#### Scripts de Qualidade
```bash
#!/bin/bash
# scripts/quality_check.sh

set -euo pipefail

echo "=== Executando verificações de qualidade ==="

# Testes com coverage
echo "1. Executando testes com coverage..."
pytest tests/ \
    --cov=core \
    --cov=plugins \
    --cov=utils \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-fail-under=80

# Verificação de código com flake8
echo "2. Verificando estilo de código..."
flake8 core/ plugins/ utils/ \
    --max-line-length=88 \
    --ignore=E203,W503 \
    --exclude=__pycache__,venv

# Type checking com mypy
echo "3. Verificando tipos..."
mypy core/ plugins/ utils/ \
    --ignore-missing-imports \
    --strict-optional \
    --warn-redundant-casts

# Verificação de segurança
echo "4. Verificando vulnerabilidades..."
bandit -r core/ plugins/ utils/ \
    -f json \
    -o security_report.json

# Verificação de complexidade
echo "5. Verificando complexidade..."
radon cc core/ plugins/ utils/ \
    --min=B \
    --show-complexity

echo "=== Verificações concluídas ==="
```

## Segurança

### 1. Validação de Entrada

#### Sanitização de Dados
```python
import re
import html
from typing import Any, Dict, Union

class InputValidator:
    """Validador e sanitizador de entrada."""
    
    # Padrões de segurança
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)",
        r"(--|#|/\*|\*/)",
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bOR\b.*=.*\bOR\b)",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>.*?</iframe>",
    ]
    
    def validate_text_input(self, text: str, max_length: int = 10000) -> str:
        """Valida e sanitiza entrada de texto."""
        if not isinstance(text, str):
            raise ValueError("Entrada deve ser uma string")
        
        if len(text) > max_length:
            raise ValueError(f"Texto muito longo (máximo: {max_length} caracteres)")
        
        # Remove/escapa caracteres perigosos
        text = html.escape(text)
        
        # Verifica padrões de SQL injection
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValueError("Padrão suspeito detectado na entrada")
        
        # Verifica padrões de XSS
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValueError("Padrão XSS detectado na entrada")
        
        return text.strip()
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Valida configuração do usuário."""
        validated_config = {}
        
        for key, value in config.items():
            # Lista de chaves permitidas
            if key not in self.ALLOWED_CONFIG_KEYS:
                continue
            
            # Validação específica por tipo
            if key.endswith('_key') or key.endswith('_token'):
                # Validação de API keys
                if not self._is_valid_api_key(value):
                    raise ValueError(f"API key inválida: {key}")
            
            elif key.endswith('_url') or key.endswith('_endpoint'):
                # Validação de URLs
                if not self._is_valid_url(value):
                    raise ValueError(f"URL inválida: {key}")
            
            validated_config[key] = value
        
        return validated_config
    
    def _is_valid_api_key(self, key: str) -> bool:
        """Verifica se API key tem formato válido."""
        if not isinstance(key, str):
            return False
        
        # Padrões comuns de API keys
        patterns = [
            r"^sk-[a-zA-Z0-9]{48}$",  # OpenAI
            r"^hf_[a-zA-Z0-9]{34}$",  # HuggingFace
            r"^[a-zA-Z0-9]{32,}$",    # Genérico
        ]
        
        return any(re.match(pattern, key) for pattern in patterns)
    
    def _is_valid_url(self, url: str) -> bool:
        """Verifica se URL é válida e segura."""
        if not isinstance(url, str):
            return False
        
        # Deve começar com https (segurança)
        if not url.startswith('https://'):
            return False
        
        # Verifica domínios maliciosos conhecidos
        malicious_domains = [
            'malicious-site.com',
            'phishing-example.org'
        ]
        
        for domain in malicious_domains:
            if domain in url:
                return False
        
        return True
```

### 2. Gestão de Secrets

#### Secret Manager
```python
import os
import keyring
from cryptography.fernet import Fernet
from typing import Optional, Dict

class SecretManager:
    """Gerenciador seguro de secrets e API keys."""
    
    def __init__(self, service_name: str = "security_framework"):
        self.service_name = service_name
        self._cipher_suite: Optional[Fernet] = None
        self._init_encryption()
    
    def _init_encryption(self) -> None:
        """Inicializa sistema de criptografia."""
        key = os.environ.get('FRAMEWORK_ENCRYPTION_KEY')
        if not key:
            # Gera nova chave se não existir
            key = Fernet.generate_key().decode()
            print(f"⚠️  Nova chave de criptografia gerada. "
                  f"Defina FRAMEWORK_ENCRYPTION_KEY={key}")
        
        self._cipher_suite = Fernet(key.encode() if isinstance(key, str) else key)
    
    def store_secret(self, key: str, value: str, encrypt: bool = True) -> None:
        """Armazena secret de forma segura."""
        if encrypt and self._cipher_suite:
            value = self._cipher_suite.encrypt(value.encode()).decode()
        
        try:
            # Tenta usar keyring do sistema
            keyring.set_password(self.service_name, key, value)
        except Exception:
            # Fallback para variável de ambiente
            os.environ[f"FRAMEWORK_{key.upper()}"] = value
    
    def get_secret(self, key: str, decrypt: bool = True) -> Optional[str]:
        """Recupera secret de forma segura."""
        value = None
        
        try:
            # Tenta keyring primeiro
            value = keyring.get_password(self.service_name, key)
        except Exception:
            pass
        
        if not value:
            # Fallback para variável de ambiente
            value = os.environ.get(f"FRAMEWORK_{key.upper()}")
        
        if not value:
            return None
        
        if decrypt and self._cipher_suite:
            try:
                value = self._cipher_suite.decrypt(value.encode()).decode()
            except Exception:
                # Pode não estar criptografado
                pass
        
        return value
    
    def list_secrets(self) -> Dict[str, bool]:
        """Lista secrets disponíveis (sem mostrar valores)."""
        secrets = {}
        
        # Verifica variáveis de ambiente
        for env_var in os.environ:
            if env_var.startswith('FRAMEWORK_'):
                key = env_var.replace('FRAMEWORK_', '').lower()
                secrets[key] = True
        
        return secrets
```

### 3. Auditoria e Logging

#### Sistema de Auditoria
```python
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class AuditLogger:
    """Sistema de auditoria para operações sensíveis."""
    
    def __init__(self, audit_dir: Path):
        self.audit_dir = audit_dir
        self.audit_dir.mkdir(exist_ok=True)
        self.audit_file = audit_dir / f"audit_{datetime.now().strftime('%Y%m')}.log"
    
    def log_classification(
        self, 
        incident_text: str,
        result: Dict[str, Any],
        user_id: str = "system",
        session_id: Optional[str] = None
    ) -> None:
        """Registra classificação para auditoria."""
        
        # Hash do texto para privacidade
        text_hash = hashlib.sha256(incident_text.encode()).hexdigest()[:16]
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "classification",
            "user_id": user_id,
            "session_id": session_id,
            "text_hash": text_hash,
            "text_length": len(incident_text),
            "result": {
                "categoria": result.get("categoria"),
                "confianca": result.get("confianca"),
                "tecnica": result.get("tecnica"),
                "erro": result.get("erro", False)
            },
            "metadata": {
                "model_used": result.get("modelo"),
                "processing_time": result.get("tempo_processamento")
            }
        }
        
        # Escreve no arquivo de auditoria
        with open(self.audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")
    
    def log_config_change(
        self,
        old_config: Dict[str, Any],
        new_config: Dict[str, Any], 
        user_id: str = "system"
    ) -> None:
        """Registra mudanças de configuração."""
        
        changes = self._detect_config_changes(old_config, new_config)
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "config_change",
            "user_id": user_id,
            "changes": changes,
            "config_hash_before": self._hash_config(old_config),
            "config_hash_after": self._hash_config(new_config)
        }
        
        with open(self.audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")
    
    def _detect_config_changes(
        self, 
        old_config: Dict[str, Any], 
        new_config: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Detecta mudanças entre configurações."""
        changes = {}
        
        all_keys = set(old_config.keys()) | set(new_config.keys())
        
        for key in all_keys:
            old_value = old_config.get(key)
            new_value = new_config.get(key)
            
            if old_value != new_value:
                changes[key] = {
                    "before": old_value,
                    "after": new_value,
                    "action": "added" if key not in old_config else 
                             "removed" if key not in new_config else 
                             "modified"
                }
        
        return changes
    
    def _hash_config(self, config: Dict[str, Any]) -> str:
        """Gera hash da configuração para integridade."""
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]
```

## Deployment e Produção

### 1. Containerização

#### Dockerfile Otimizado
```dockerfile
# Dockerfile.production
FROM python:3.11-slim as builder

# Instalar dependências de build
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Criar e ativar virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage final
FROM python:3.11-slim

# Copiar virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Criar usuário não-root
RUN groupadd -r framework && useradd -r -g framework framework

# Criar diretórios
RUN mkdir -p /app/logs /app/data /app/output && \
    chown -R framework:framework /app

# Copiar código
COPY --chown=framework:framework . /app
WORKDIR /app

# Mudar para usuário não-root
USER framework

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import core.framework; print('OK')" || exit 1

# Expor porta
EXPOSE 8000

# Comando padrão
CMD ["python", "-m", "core.framework"]
```

#### Docker Compose para Produção
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  security-framework:
    build:
      context: .
      dockerfile: Dockerfile.production
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=WARNING
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - FRAMEWORK_ENCRYPTION_KEY=${FRAMEWORK_ENCRYPTION_KEY}
    volumes:
      - ./data:/app/data:ro
      - ./output:/app/output
      - ./logs:/app/logs
      - ./config/production.json:/app/config/config.json:ro
    networks:
      - framework-network
    restart: unless-stopped
    depends_on:
      - redis
      - monitoring
    
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - framework-network
    restart: unless-stopped
  
  monitoring:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - framework-network
    restart: unless-stopped

volumes:
  redis-data:
  prometheus-data:

networks:
  framework-network:
    driver: bridge
```

### 2. CI/CD Pipeline

#### GitHub Actions
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  PYTHON_VERSION: '3.11'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run quality checks
      run: |
        # Linting
        flake8 core/ plugins/ utils/
        
        # Type checking
        mypy core/ plugins/ utils/
        
        # Security scanning
        bandit -r core/ plugins/ utils/
    
    - name: Run tests with coverage
      run: |
        pytest tests/ \
          --cov=core \
          --cov=plugins \
          --cov=utils \
          --cov-report=xml \
          --cov-fail-under=80
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
  
  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    
    permissions:
      contents: read
      packages: write
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: Dockerfile.production
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    environment: production
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to production
      run: |
        # Script de deploy personalizado
        ./scripts/deploy.sh ${{ github.sha }}
```

### 3. Monitoramento

#### Métricas com Prometheus
```python
# utils/prometheus_metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
from functools import wraps

# Métricas definidas
CLASSIFICATION_REQUESTS = Counter(
    'classification_requests_total',
    'Total classification requests',
    ['model', 'technique', 'status']
)

CLASSIFICATION_DURATION = Histogram(
    'classification_duration_seconds',
    'Time spent classifying incidents',
    ['model', 'technique']
)

ACTIVE_CLASSIFICATIONS = Gauge(
    'active_classifications',
    'Number of classifications in progress'
)

API_ERRORS = Counter(
    'api_errors_total',
    'Total API errors',
    ['provider', 'error_type']
)

def monitor_classification(model: str, technique: str):
    """Decorator para monitorar classificações."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ACTIVE_CLASSIFICATIONS.inc()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Métricas de sucesso
                CLASSIFICATION_REQUESTS.labels(
                    model=model, 
                    technique=technique, 
                    status='success'
                ).inc()
                
                return result
                
            except Exception as e:
                # Métricas de erro
                CLASSIFICATION_REQUESTS.labels(
                    model=model,
                    technique=technique, 
                    status='error'
                ).inc()
                
                API_ERRORS.labels(
                    provider=model.split('_')[0],
                    error_type=type(e).__name__
                ).inc()
                
                raise
                
            finally:
                # Duração e limpeza
                duration = time.time() - start_time
                CLASSIFICATION_DURATION.labels(
                    model=model,
                    technique=technique
                ).observe(duration)
                
                ACTIVE_CLASSIFICATIONS.dec()
        
        return wrapper
    return decorator

def start_metrics_server(port: int = 8000):
    """Inicia servidor de métricas Prometheus."""
    start_http_server(port)
    print(f"Métricas disponíveis em http://localhost:{port}/metrics")
```

Este documento estabelece as bases sólidas para um desenvolvimento de qualidade, garantindo que o framework seja robusto, seguro e facilmente mantível.