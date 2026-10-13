from typing import Dict, Any, Optional, Type, List
from pathlib import Path
import difflib

from .observability.logger import setup_logger

# Importa os plugins de modelo
from pangolin.plugins.models.api_model import APIModel
from pangolin.plugins.models.local_model import LocalModel
from pangolin.plugins.models.huggingface_model import HuggingfaceModel
from pangolin.plugins.models.openrouter_model import OpenRouterModel
try:
    from pangolin.plugins.models.mock_model import MockModel
    MOCK_AVAILABLE = True
except ImportError:
    MOCK_AVAILABLE = False

# Nota: Plugins de prompt agora são gerenciados via schemas YAML
# e execução genérica através do SchemaPromptPlugin

# Única tabela de providers: plugin em memória e arquivo de projeto ficam
# vinculados na mesma entrada, evitando mapas que possam divergir.
_PROVIDER_SPECS = {
    'ollama': ('LocalModel', 'local_model.py', ()),
    'local': ('LocalModel', 'local_model.py', ()),
    'huggingface': ('HuggingfaceModel', 'huggingface_model.py', ()),
    'openai': ('APIModel', 'api_model.py', ()),
    'anthropic': ('APIModel', 'api_model.py', ()),
    'gemini': ('APIModel', 'api_model.py', ()),
    'google': ('APIModel', 'api_model.py', ()),
    'cohere': ('APIModel', 'api_model.py', ()),
    'deepseek': ('APIModel', 'api_model.py', ()),
    'groq': ('APIModel', 'api_model.py', ()),
    'openrouter': ('OpenRouterModel', 'openrouter_model.py', ('api_model.py',)),
    'azure': ('APIModel', 'api_model.py', ()),
    'bedrock': ('APIModel', 'api_model.py', ()),
    'vertex': ('APIModel', 'api_model.py', ()),
    'palm': ('APIModel', 'api_model.py', ()),
}

# Aliases mantidos para consumidores que importam esses mapas.
PROVIDER_TO_MODEL = {name: spec[0] for name, spec in _PROVIDER_SPECS.items()}
MODEL_MODULE_FILES = {name: spec[1] for name, spec in _PROVIDER_SPECS.items()}
MODEL_MODULE_DEPENDENCIES = {name: spec[2] for name, spec in _PROVIDER_SPECS.items()}

_SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"


def _suggestion(term: str, choices) -> str:
    """Retorna uma sugestão de correção, se houver, para um termo desconhecido."""
    matches = difflib.get_close_matches(term, choices, n=1)
    if matches:
        return f" Você quis dizer '{matches[0]}'?"
    return ""


def available_techniques() -> List[str]:
    """Retorna as técnicas conhecidas (schemas do diretório de schemas)."""
    if not _SCHEMAS_DIR.exists():
        return []
    return sorted(p.stem for p in _SCHEMAS_DIR.glob("*.yaml"))


class PluginManager:
    """Gerenciador de plugins do framework."""
    
    def __init__(self):
        self.model_plugins: Dict[str, Type] = {}
        self.logger = setup_logger("PluginManager")
        self._register_default_plugins()
    
    def _register_default_plugins(self):
        """Registra plugins padrão do framework."""
        # Registra plugins de modelo
        self.register_model_plugin("APIModel", APIModel)
        self.register_model_plugin("OpenRouterModel", OpenRouterModel)
        self.register_model_plugin("LocalModel", LocalModel)
        self.register_model_plugin("HuggingfaceModel", HuggingfaceModel)
        if MOCK_AVAILABLE:
            self.register_model_plugin("MockModel", MockModel)
        
        self.logger.info(
            "Plugins de modelo registrados: %d",
            len(self.model_plugins),
        )
    
    def register_model_plugin(self, name: str, plugin_class: Type):
        """Registra um plugin de modelo."""
        self.model_plugins[name] = plugin_class
        self.logger.debug("Plugin de modelo registrado: %s", name)
    
    def get_model_plugin(self, name: str) -> Optional[Type]:
        """Obtém classe de plugin de modelo pelo nome."""
        return self.model_plugins.get(name)
    
    def resolve_model(self, provider: str) -> Type:
        """
        Resolve a classe de plugin de modelo a partir do provider.

        Raises:
            ValueError: Se o provider for desconhecido (com sugestão de correção).
        """
        provider = (provider or '').strip().lower()
        plugin_name = PROVIDER_TO_MODEL.get(provider)
        if plugin_name is None:
            raise ValueError(
                f"Provider '{provider}' não reconhecido."
                f"{_suggestion(provider, PROVIDER_TO_MODEL.keys())}"
                f" Providers disponíveis: {', '.join(sorted(PROVIDER_TO_MODEL))}"
            )

        plugin_class = self.get_model_plugin(plugin_name)
        if plugin_class is None:
            raise ValueError(
                f"Plugin de modelo '{plugin_name}' (provider '{provider}') "
                "não está registrado"
            )
        return plugin_class

    def resolve_model_plugin_file(self, provider: str) -> str:
        """
        Resolve o arquivo de plugin copiado para o diretório model/ do projeto.

        Raises:
            ValueError: Se o provider for desconhecido.
        """
        provider = (provider or '').strip().lower()
        plugin_file = MODEL_MODULE_FILES.get(provider)
        if plugin_file is None:
            raise ValueError(
                f"Provider '{provider}' não reconhecido."
                f"{_suggestion(provider, MODEL_MODULE_FILES.keys())}"
            )
        return plugin_file

    def resolve_model_plugin_files(self, provider: str) -> List[str]:
        """Retorna o plugin e seus módulos locais necessários para vendorização."""
        normalized_provider = (provider or '').strip().lower()
        plugin_file = self.resolve_model_plugin_file(normalized_provider)
        dependencies = MODEL_MODULE_DEPENDENCIES[normalized_provider]
        return [plugin_file, *dependencies]

    def resolve_schema_file(self, technique: str) -> Path:
        """
        Resolve o caminho do schema YAML de uma técnica.

        Raises:
            ValueError: Se a técnica for desconhecida (com sugestão de correção).
        """
        technique = (technique or '').strip().lower()
        schema_file = _SCHEMAS_DIR / f"{technique}.yaml"
        if not schema_file.exists():
            techniques = available_techniques()
            raise ValueError(
                f"Técnica '{technique}' não reconhecida."
                f"{_suggestion(technique, techniques)}"
                f" Técnicas disponíveis: {', '.join(techniques)}"
            )
        return schema_file

    def get_available_techniques(self) -> List[str]:
        """Retorna as técnicas conhecidas pelo framework."""
        return available_techniques()

    def create_model_instance(self, plugin_name: str, config: Dict[str, Any]) -> Optional[Any]:
        """Cria instância de plugin de modelo."""
        plugin_class = self.get_model_plugin(plugin_name)
        if plugin_class is None:
            self.logger.error("Plugin de modelo não encontrado: %s", plugin_name)
            return None

        instance = plugin_class(config)
        self.logger.info("Instância de modelo criada: %s", plugin_name)
        return instance
    
    def list_available_models(self) -> list:
        """Lista plugins de modelo disponíveis."""
        return list(self.model_plugins.keys())
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """Retorna informações sobre plugins carregados."""
        return {
            "model_plugins": {
                name: plugin_class.__doc__ or "Sem descrição"
                for name, plugin_class in self.model_plugins.items()
            },
            "total_model_plugins": len(self.model_plugins),
            "prompt_plugins_note": "Agora gerenciados via schemas YAML e SchemaPromptPlugin"
        }
