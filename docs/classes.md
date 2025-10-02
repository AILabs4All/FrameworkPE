# Classes e Métodos Detalhados

## Visão Geral

Esta documentação detalha todas as classes principais do framework, suas responsabilidades, métodos, parâmetros e exemplos de uso. O framework está organizado em camadas bem definidas para facilitar manutenção e extensão.

## Índice de Classes

### Core (Núcleo)
- [SecurityIncidentFramework](#securityincidentframework) - Classe principal do framework
- [ConfigLoader](#configloader) - Gerenciamento de configurações
- [PluginManager](#pluginmanager) - Sistema de plugins

### Plugins de Modelos
- [BaseModel](#basemodel) - Interface base para modelos
- [APIModel](#apimodel) - Modelos via API (OpenAI, HuggingFace)
- [LocalModel](#localmodel) - Modelos locais (Ollama)

### Plugins de Prompts
- [BasePromptPlugin](#basepromptplugin) - Interface base para técnicas
- [ProgressiveHintPlugin](#progressivehintplugin) - Progressive Hint Prompting
- [SelfHintPlugin](#selfhintplugin) - Self Hint Prompting
- [ProgressiveRectificationPlugin](#progressiverectificationplugin) - Progressive Rectification
- [HypothesisTestingPlugin](#hypothesistestingplugin) - Hypothesis Testing

### Utilitários
- [FileHandlers](#filehandlers) - Manipulação de arquivos
- [Logger](#logger) - Sistema de logging
- [MetricsCollector](#metricscollector) - Coleta de métricas
- [SecurityExtractor](#securityextractor) - Extração de categorias NIST

---

## Core Classes

### SecurityIncidentFramework

**Localização:** `core/framework.py`

**Responsabilidade:** Classe principal que orquestra todo o fluxo de classificação de incidentes de segurança.

#### Inicialização

```python
def __init__(self, config_path: str = "config.json"):
    """
    Inicializa o framework principal.
    
    Args:
        config_path: Caminho para arquivo de configuração (JSON/YAML)
    
    Raises:
        ValueError: Se configuração for inválida
    """
    self.logger = setup_logger("SecurityIncidentFramework")
    self.config = ConfigLoader.load(config_path)
    self.plugin_manager = PluginManager()
    self.metrics_collector = MetricsCollector()
```

#### Métodos Principais

##### process_incidents()

```python
def process_incidents(
    self, 
    input_dir: str, 
    columns: List[str], 
    model_name: str, 
    prompt_technique: str, 
    output_format: str = "csv", 
    **kwargs
) -> Dict[str, Any]:
    """
    Processa incidentes de segurança usando modelo e técnica especificados.
    
    Args:
        input_dir: Diretório com arquivos de incidentes (CSV, JSON, XLSX)
        columns: Lista de colunas para usar como entrada do prompt
        model_name: Nome do modelo configurado no arquivo de config
        prompt_technique: Técnica de prompt a usar
        output_format: Formato de saída ("csv", "json", "xlsx")
        **kwargs: Parâmetros adicionais para a técnica de prompt
        
    Returns:
        Dict com resultados da classificação e métricas de execução
        
    Raises:
        ValueError: Se parâmetros forem inválidos
        FileNotFoundError: Se diretório de entrada não existir
    """
```

**Exemplo de Uso:**
```python
framework = SecurityIncidentFramework("config/default_config.json")

results = framework.process_incidents(
    input_dir="data/",
    columns=["Pedido", "Descrição"],
    model_name="ollama_deepseek_15b",
    prompt_technique="progressive_hint",
    output_format="csv",
    max_hints=3,
    limite_rouge=0.9
)

print(f"Processados {results['total_incidents']} incidentes")
print(f"Tempo total: {results['execution_time']:.2f}s")
```

##### Métodos de Consulta

```python
def list_available_models(self) -> List[str]:
    """Lista modelos disponíveis na configuração."""
    
def list_available_prompts(self) -> List[str]:
    """Lista técnicas de prompt disponíveis."""
    
def get_framework_info(self) -> Dict[str, Any]:
    """Retorna informações completas sobre o framework."""
```

#### Métodos Internos

##### _build_prompt()

```python
def _build_prompt(self, row: pd.Series, columns: List[str]) -> str:
    """
    Constrói prompt base para classificação NIST.
    
    Args:
        row: Linha do DataFrame com dados do incidente
        columns: Colunas a incluir no prompt
        
    Returns:
        String com prompt formatado incluindo categorias NIST
    """
```

##### _process_all_incidents()

```python
def _process_all_incidents(
    self,
    dataframes: List[pd.DataFrame], 
    columns: List[str], 
    prompt_instance: Any,
    prompt_config: Dict[str, Any],
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Processa todos os incidentes dos DataFrames com barra de progresso.
    
    Args:
        dataframes: Lista de DataFrames com dados
        columns: Colunas a processar
        prompt_instance: Instância da técnica de prompt
        prompt_config: Configuração da técnica
        **kwargs: Parâmetros adicionais
        
    Returns:
        Lista de resultados da classificação
    """
```

---

### ConfigLoader

**Localização:** `core/config_loader.py`

**Responsabilidade:** Carrega, valida e resolve configurações do framework.

#### Métodos Estáticos

##### load()

```python
@staticmethod
def load(config_path: str = "config.json") -> Dict[str, Any]:
    """
    Carrega configuração de arquivo JSON ou YAML.
    
    Args:
        config_path: Caminho para arquivo de configuração
        
    Returns:
        Dict com configurações carregadas e validadas
        
    Raises:
        FileNotFoundError: Se arquivo não existir
        ValueError: Se configuração for inválida
    """
```

**Exemplo de Uso:**
```python
# Carrega configuração padrão
config = ConfigLoader.load("config/default_config.json")

# Carrega configuração personalizada
config = ConfigLoader.load("custom_config.yaml")

# Acessa configurações
models = config["models"]
logging_config = config["logging"]
```

#### Métodos de Instância

##### validate_config()

```python
def validate_config(self, config: Dict[str, Any]) -> bool:
    """
    Valida se configuração tem campos obrigatórios.
    
    Args:
        config: Dicionário com configuração
        
    Returns:
        True se válida, False caso contrário
        
    Validações:
        - Campos obrigatórios: framework, models, prompt_techniques
        - Pelo menos um modelo configurado
        - Pelo menos uma técnica de prompt configurada
    """
```

##### _resolve_env_variables()

```python
def _resolve_env_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolve variáveis de ambiente na configuração.
    
    Sintaxe: ${VARIABLE_NAME}
    
    Args:
        config: Configuração com possíveis variáveis de ambiente
        
    Returns:
        Configuração com variáveis resolvidas
    """
```

**Exemplo de Configuração:**
```json
{
  "models": {
    "openai_gpt4": {
      "plugin": "APIModel",
      "provider": "openai",
      "model": "gpt-4",
      "api_key": "${OPENAI_API_KEY}",
      "temperature": 0.7
    }
  }
}
```

---

### PluginManager

**Localização:** `core/plugin_manager.py`

**Responsabilidade:** Gerencia registro, descoberta e instanciação de plugins.

#### Inicialização

```python
def __init__(self):
    """
    Inicializa gerenciador e registra plugins padrão.
    
    Plugins Registrados Automaticamente:
        Modelos: APIModel, LocalModel
        Prompts: ProgressiveHintPlugin, SelfHintPlugin,
                ProgressiveRectificationPlugin, HypothesisTestingPlugin
    """
    self.prompt_plugins: Dict[str, Type] = {}
    self.model_plugins: Dict[str, Type] = {}
    self.logger = setup_logger("PluginManager")
    self._register_default_plugins()
```

#### Métodos de Registro

```python
def register_model_plugin(self, name: str, plugin_class: Type):
    """Registra plugin de modelo."""
    
def register_prompt_plugin(self, name: str, plugin_class: Type):
    """Registra plugin de técnica de prompt."""
```

**Exemplo de Extensão:**
```python
from plugins.models.custom_model import CustomModel
from plugins.prompts.custom_prompt import CustomPrompt

plugin_manager = PluginManager()

# Registra plugins personalizados
plugin_manager.register_model_plugin("CustomModel", CustomModel)
plugin_manager.register_prompt_plugin("CustomPrompt", CustomPrompt)
```

#### Métodos de Instanciação

##### create_model_instance()

```python
def create_model_instance(
    self, 
    plugin_name: str, 
    config: Dict[str, Any]
) -> Optional[Any]:
    """
    Cria instância de plugin de modelo.
    
    Args:
        plugin_name: Nome do plugin registrado
        config: Configuração específica do modelo
        
    Returns:
        Instância do modelo ou None se falhar
    """
```

##### create_prompt_instance()

```python
def create_prompt_instance(
    self, 
    plugin_name: str, 
    model_instance: Any
) -> Optional[Any]:
    """
    Cria instância de plugin de prompt.
    
    Args:
        plugin_name: Nome do plugin registrado
        model_instance: Instância do modelo a usar
        
    Returns:
        Instância da técnica de prompt ou None se falhar
    """
```

#### Métodos de Consulta

```python
def list_available_models(self) -> List[str]:
    """Lista plugins de modelo disponíveis."""
    
def list_available_prompts(self) -> List[str]:
    """Lista plugins de prompt disponíveis."""
    
def get_plugin_info(self) -> Dict[str, Any]:
    """Retorna informações detalhadas sobre plugins carregados."""
```

---

## Plugin Classes - Modelos

### BaseModel

**Localização:** `plugins/models/base_model.py`

**Responsabilidade:** Classe abstrata base para todos os modelos, fornece funcionalidades compartilhadas.

#### Interface Abstrata

```python
from abc import ABC, abstractmethod

class BaseModel(ABC):
    """Classe base com funcionalidades compartilhadas entre modelos."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa modelo base.
        
        Args:
            config: Configuração do modelo contendo:
                - provider: Nome do provedor
                - model: Nome do modelo
                - temperature: Temperatura de geração
                - max_tokens: Máximo de tokens
                - rate_limit: Limitação de requisições
        """
        self.config = config
        self.logger = setup_logger(self.__class__.__name__)
        self.token_metrics = TokenMetrics()
        self.provider = config.get("provider", "unknown")
        self.model_name = config.get("model", "")
        self.temperature = float(config.get("temperature", 0.7))
        self.max_tokens = int(config.get("max_tokens", 2048))
        self.rate_limit = float(config.get("rate_limit", 0.0))
        self.setup_model()
    
    @abstractmethod
    def setup_model(self) -> None:
        """Configura dados específicos do modelo. Deve ser implementado."""
    
    @abstractmethod
    def send_prompt(self, prompt: str, **kwargs: Any) -> str:
        """Envia prompt e retorna resposta. Deve ser implementado."""
```

#### Métodos Utilitários

##### count_tokens()

```python
def count_tokens(self, text: str) -> int:
    """
    Conta tokens usando tiktoken com fallback seguro.
    
    Args:
        text: Texto para contar tokens
        
    Returns:
        Número de tokens no texto
        
    Fallbacks:
        1. Encoding específico configurado
        2. Encoding para o modelo
        3. Encoding padrão cl100k_base
    """
```

##### get_model_info()

```python
def get_model_info(self) -> Dict[str, Any]:
    """
    Retorna informações básicas do modelo.
    
    Returns:
        Dict com name, provider, temperature, max_tokens, rate_limit
    """
```

##### _log_interaction()

```python
def _log_interaction(
    self,
    prompt: str,
    response: str,
    input_tokens: int,
    output_tokens: int,
    mode: str,
) -> None:
    """
    Registra métricas de interação para auditoria.
    
    Args:
        prompt: Prompt enviado
        response: Resposta recebida
        input_tokens: Tokens de entrada
        output_tokens: Tokens de saída
        mode: Modo de execução
    """
```

---

### APIModel

**Localização:** `plugins/models/api_model.py`

**Responsabilidade:** Implementação para modelos acessados via API (OpenAI, HuggingFace, etc.)

#### Configuração de Provedores

```python
class APIModel(BaseModel):
    """Modelo para provedores acessados via API."""
    
    # Mapeamento de variáveis de ambiente
    PROVIDER_ENV_MAP = {
        "openai": "OPENAI_API_KEY",
        "azure_openai": "AZURE_OPENAI_API_KEY", 
        "huggingface": "HUGGINGFACE_API_KEY",
        "cohere": "COHERE_API_KEY",
    }
    
    # Prefixos para identificadores de modelo
    PROVIDER_PREFIX = {
        "huggingface": "huggingface/",
    }
```

#### Implementação

##### setup_model()

```python
def setup_model(self) -> None:
    """
    Configura modelo API com credenciais e endpoints.
    
    Resolve:
        - API keys de variáveis de ambiente
        - Base URLs personalizadas
        - Deployment IDs (Azure)
        - Parâmetros extras
    """
```

##### send_prompt()

```python
def send_prompt(self, prompt: str, **kwargs: Any) -> str:
    """
    Envia prompt para API externa usando LiteLLM.
    
    Args:
        prompt: Texto do prompt
        **kwargs: Parâmetros opcionais:
            - temperature: Sobrescrever temperatura
            - max_tokens: Sobrescrever max_tokens
            - messages: Formato de mensagens personalizado
            - mode: Modo para métricas
            - rate_limit: Sobrescrever rate limit
            
    Returns:
        Resposta do modelo como string
        
    Raises:
        Exception: Se chamada à API falhar
    """
```

**Exemplo de Uso:**
```python
# Configuração no JSON
config = {
    "plugin": "APIModel",
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.3,
    "max_tokens": 1500,
    "api_key": "${OPENAI_API_KEY}"
}

# Instanciação e uso
model = APIModel(config)
response = model.send_prompt(
    "Classifique este incidente: Tentativa de login suspeita",
    temperature=0.1,
    mode="classification"
)
```

---

### LocalModel

**Localização:** `plugins/models/local_model.py`

**Responsabilidade:** Implementação para modelos locais via Ollama.

#### Configuração

```python
def setup_model(self) -> None:
    """
    Configura modelo local Ollama.
    
    Configurações:
        - base_url: Endpoint do servidor Ollama
        - healthcheck: Habilita verificação de saúde
        - extra_params: Parâmetros adicionais
        
    Environment:
        Define OLLAMA_API_BASE automaticamente
    """
    self.api_base = self.config.get("base_url", "http://localhost:11434")
    self.healthcheck_enabled = bool(self.config.get("healthcheck", True))
    self.extra_params = self.config.get("extra_params", {})
```

#### Métodos Específicos

##### health_check()

```python
def health_check(self) -> bool:
    """
    Verifica se servidor Ollama está respondendo.
    
    Returns:
        True se servidor estiver ativo, False caso contrário
        
    Endpoint: GET {api_base}/api/version
    Timeout: 5 segundos
    """
```

##### send_prompt()

```python
def send_prompt(self, prompt: str, **kwargs: Any) -> str:
    """
    Envia prompt para modelo local via Ollama.
    
    Args:
        prompt: Texto do prompt
        **kwargs: Parâmetros similares ao APIModel
        
    Returns:
        Resposta do modelo local
        
    Rate Limit Default: 0.5 segundos entre requisições
    """
```

**Exemplo de Configuração:**
```json
{
  "ollama_deepseek": {
    "plugin": "LocalModel",
    "provider": "ollama",
    "model": "deepseek-r1:1.5b",
    "base_url": "http://localhost:11434",
    "temperature": 0.7,
    "max_tokens": 2000,
    "healthcheck": true,
    "extra_params": {
      "num_predict": 2000,
      "num_ctx": 4096
    }
  }
}
```

---

## Plugin Classes - Técnicas de Prompt

### BasePromptPlugin

**Localização:** `plugins/prompts/base_prompt.py`

**Responsabilidade:** Interface base para todas as técnicas de prompt.

#### Interface Abstrata

```python
from abc import ABC, abstractmethod

class BasePromptPlugin(ABC):
    """Classe base para todos os plugins de técnicas de prompt."""
    
    def __init__(self, model_plugin):
        """
        Inicializa técnica de prompt.
        
        Args:
            model_plugin: Instância do modelo a usar
        """
        self.model_plugin = model_plugin
        self.logger = setup_logger(self.__class__.__name__)
    
    @abstractmethod
    def execute(
        self, 
        prompt: str, 
        data_row: pd.Series, 
        columns: List[str], 
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Executa a técnica de prompt específica.
        
        Args:
            prompt: Prompt base construído pelo framework
            data_row: Linha de dados do incidente
            columns: Colunas sendo processadas
            **kwargs: Parâmetros específicos da técnica
            
        Returns:
            Lista de resultados da classificação
        """
        
    @abstractmethod
    def get_name(self) -> str:
        """Retorna nome da técnica de prompt."""
```

#### Métodos Utilitários

```python
def build_incident_info(self, row: pd.Series, columns: List[str]) -> str:
    """
    Constrói string com informações do incidente.
    
    Args:
        row: Linha do DataFrame
        columns: Colunas a incluir
        
    Returns:
        String formatada: "coluna1: valor1 / coluna2: valor2"
    """
```

---

### ProgressiveHintPlugin

**Localização:** `plugins/prompts/progressive_hint.py`

**Responsabilidade:** Implementa Progressive Hint Prompting - gera dicas progressivas para melhorar classificação.

#### Parâmetros

```python
# Parâmetros padrão configuráveis
default_params = {
    "max_hints": 4,        # Máximo de dicas a gerar
    "limite_rouge": 0.9    # Limite ROUGE para parar iterações
}
```

#### Implementação

```python
def execute(
    self,
    prompt: str,
    data_row: pd.Series,
    columns: List[str],
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Executa Progressive Hint Prompting.
    
    Fluxo:
        1. Classificação inicial
        2. Análise da resposta
        3. Geração de dicas específicas
        4. Refinamento iterativo
        5. Classificação final
        
    Args:
        max_hints: Número máximo de dicas (default: 4)
        limite_rouge: Limite de similaridade ROUGE (default: 0.9)
        
    Returns:
        Lista com resultado final da classificação
    """
```

**Exemplo de Uso:**
```python
# Na configuração
"progressive_hint": {
    "plugin": "ProgressiveHintPlugin",
    "description": "Progressive Hint Prompting",
    "default_params": {
        "max_hints": 3,
        "limite_rouge": 0.85
    }
}

# Na execução
framework.process_incidents(
    input_dir="data/",
    columns=["description"],
    model_name="openai_gpt4",
    prompt_technique="progressive_hint",
    max_hints=5,
    limite_rouge=0.95
)
```

---

### SelfHintPlugin

**Localização:** `plugins/prompts/self_hint.py`

**Responsabilidade:** Self Hint Prompting - o modelo gera seu próprio plano e se auto-refina.

#### Características

- **Auto-planejamento:** Modelo cria estratégia de análise
- **Auto-refinamento:** Melhora resposta iterativamente
- **Metacognição:** Modelo avalia próprio desempenho

#### Parâmetros

```python
default_params = {
    "max_iter": 4,           # Máximo de iterações
    "limite_qualidade": 0.9  # Limite de qualidade para parar
}
```

---

### ProgressiveRectificationPlugin

**Localização:** `plugins/prompts/progressive_rectification.py`

**Responsabilidade:** Progressive Rectification Prompting - valida e retifica respostas usando mascaramento.

#### Características

- **Validação:** Verifica consistência da classificação
- **Retificação:** Corrige inconsistências detectadas
- **Mascaramento:** Oculta partes da resposta para validação

#### Parâmetros

```python
default_params = {
    "max_iter": 4,           # Máximo de iterações
    "limite_qualidade": 0.9  # Limite de qualidade
}
```

---

### HypothesisTestingPlugin

**Localização:** `plugins/prompts/hypothesis_testing.py`

**Responsabilidade:** Hypothesis Testing Prompting - testa hipóteses para cada categoria NIST sistematicamente.

#### Características

- **Teste Sistemático:** Avalia cada categoria NIST
- **Evidências:** Coleta evidências para cada hipótese
- **Ranking:** Ordena categorias por evidências

#### Parâmetros

```python
default_params = {
    "max_iter": 12,          # Máximo de iterações (uma por categoria)
    "limite_qualidade": 0.9  # Limite de qualidade
}
```

---

## Utilitários

### FileHandlers

**Localização:** `utils/file_handlers.py`

**Responsabilidade:** Manipulação de arquivos de entrada e saída.

#### Funções Principais

##### load_data_files()

```python
def load_data_files(directory: str) -> List[pd.DataFrame]:
    """
    Carrega todos os arquivos de dados de um diretório.
    
    Formatos Suportados:
        - CSV (encoding automático)
        - JSON (objetos e arrays)
        - XLSX (múltiplas abas)
        
    Args:
        directory: Caminho para diretório com arquivos
        
    Returns:
        Lista de DataFrames carregados
        
    Raises:
        FileNotFoundError: Se diretório não existir
        ValueError: Se nenhum arquivo válido for encontrado
    """
```

##### save_results()

```python
def save_results(
    results: List[Dict[str, Any]], 
    output_format: str,
    output_path: str = None
) -> str:
    """
    Salva resultados no formato especificado.
    
    Args:
        results: Lista de resultados da classificação
        output_format: "csv", "json", ou "xlsx"
        output_path: Caminho de saída (opcional)
        
    Returns:
        Caminho do arquivo salvo
        
    Características:
        - Timestamps automáticos
        - Metadados inclusos
        - Formatação consistente
    """
```

##### validate_columns()

```python
def validate_columns(
    dataframes: List[pd.DataFrame], 
    required_columns: List[str]
) -> bool:
    """
    Valida se colunas obrigatórias estão presentes.
    
    Args:
        dataframes: Lista de DataFrames
        required_columns: Colunas obrigatórias
        
    Returns:
        True se todas as colunas estiverem presentes
    """
```

---

### Logger

**Localização:** `utils/logger.py`

**Responsabilidade:** Sistema de logging estruturado e configurável.

#### Configuração

```python
def setup_logger(
    name: str,
    level: str = "INFO",
    log_dir: str = "logs",
    enable_console: bool = True,
    enable_file: bool = True
) -> logging.Logger:
    """
    Configura logger com formatação padrão.
    
    Args:
        name: Nome do logger
        level: Nível de log (DEBUG, INFO, WARNING, ERROR)
        log_dir: Diretório para arquivos de log
        enable_console: Habilita output no console
        enable_file: Habilita output em arquivo
        
    Returns:
        Logger configurado
        
    Formato:
        YYYY-MM-DD HH:MM:SS - nome - LEVEL - mensagem
    """
```

**Exemplo de Uso:**
```python
from utils.logger import setup_logger

logger = setup_logger("MeuComponente")
logger.info("Processamento iniciado")
logger.warning("Modelo não encontrado, usando fallback")
logger.error("Falhas na validação: %s", errors)
```

---

### MetricsCollector

**Localização:** `utils/metrics.py`

**Responsabilidade:** Coleta e reporta métricas de execução.

#### Métricas Coletadas

- **Performance:** Tempo de execução, memória usada
- **Tokens:** Entrada, saída, custos estimados
- **Qualidade:** Taxa de erro, distribuição de categorias
- **Throughput:** Incidentes por segundo

#### Métodos

```python
class MetricsCollector:
    def start_collection(self):
        """Inicia coleta de métricas."""
        
    def record_incident_processed(self, incident_data: Dict):
        """Registra processamento de incidente."""
        
    def record_model_interaction(self, model_data: Dict):
        """Registra interação com modelo."""
        
    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório final de métricas."""
```

---

Esta documentação fornece uma visão completa de todas as classes e métodos do framework, facilitando tanto o uso quanto a extensão do sistema.