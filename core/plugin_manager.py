from typing import Dict, Any, Optional, Type
from utils.logger import setup_logger

# Importa os plugins de modelo
from plugins.models.api_model import APIModel
from plugins.models.local_model import LocalModel
from plugins.models.hungguiface_model import HuggingfaceModel
try:
    from plugins.models.mock_model import MockModel
    MOCK_AVAILABLE = True
except ImportError:
    MOCK_AVAILABLE = False

# Importa os plugins de prompt
from plugins.prompts.progressive_hint import ProgressiveHintPlugin
from plugins.prompts.self_hint import SelfHintPlugin
from plugins.prompts.progressive_rectification import ProgressiveRectificationPlugin
from plugins.prompts.hypothesis_testing import HypothesisTestingPlugin

class PluginManager:
    """Gerenciador de plugins do framework."""
    
    def __init__(self):
        self.prompt_plugins: Dict[str, Type] = {}
        self.model_plugins: Dict[str, Type] = {}
        self.logger = setup_logger("PluginManager")
        self._register_default_plugins()
    
    def _register_default_plugins(self):
        """Registra plugins padrão do framework."""
        # Registra plugins de modelo
        self.register_model_plugin("APIModel", APIModel)
        self.register_model_plugin("LocalModel", LocalModel)
        self.register_model_plugin("HuggingfaceModel", HuggingfaceModel)
        if MOCK_AVAILABLE:
            self.register_model_plugin("MockModel", MockModel)
        
        # Registra plugins de prompt
        self.register_prompt_plugin("ProgressiveHintPlugin", ProgressiveHintPlugin)
        self.register_prompt_plugin("SelfHintPlugin", SelfHintPlugin)
        self.register_prompt_plugin("ProgressiveRectificationPlugin", ProgressiveRectificationPlugin)
        self.register_prompt_plugin("HypothesisTestingPlugin", HypothesisTestingPlugin)
        
        self.logger.info(
            "Plugins registrados: %d modelos, %d técnicas de prompt",
            len(self.model_plugins),
            len(self.prompt_plugins),
        )
    
    def register_prompt_plugin(self, name: str, plugin_class: Type):
        """Registra um plugin de técnica de prompt."""
        self.prompt_plugins[name] = plugin_class
        self.logger.debug("Plugin de prompt registrado: %s", name)
    
    def register_model_plugin(self, name: str, plugin_class: Type):
        """Registra um plugin de modelo."""
        self.model_plugins[name] = plugin_class
        self.logger.debug("Plugin de modelo registrado: %s", name)
    
    def get_prompt_plugin(self, name: str) -> Optional[Type]:
        """Obtém classe de plugin de prompt pelo nome."""
        return self.prompt_plugins.get(name)
    
    def get_model_plugin(self, name: str) -> Optional[Type]:
        """Obtém classe de plugin de modelo pelo nome."""
        return self.model_plugins.get(name)
    
    def create_model_instance(self, plugin_name: str, config: Dict[str, Any]) -> Optional[Any]:
        """Cria instância de plugin de modelo."""
        plugin_class = self.get_model_plugin(plugin_name)
        if plugin_class is None:
            self.logger.error("Plugin de modelo não encontrado: %s", plugin_name)
            return None

        instance = plugin_class(config)
        self.logger.info("Instância de modelo criada: %s", plugin_name)
        return instance
    
    def create_prompt_instance(self, plugin_name: str, model_instance: Any) -> Optional[Any]:
        """Cria instância de plugin de prompt."""
        plugin_class = self.get_prompt_plugin(plugin_name)
        if plugin_class is None:
            self.logger.error("Plugin de prompt não encontrado: %s", plugin_name)
            return None

        instance = plugin_class(model_instance)
        self.logger.info("Instância de prompt criada: %s", plugin_name)
        return instance
    
    def list_available_models(self) -> list:
        """Lista plugins de modelo disponíveis."""
        return list(self.model_plugins.keys())
    
    def list_available_prompts(self) -> list:
        """Lista plugins de prompt disponíveis."""
        return list(self.prompt_plugins.keys())
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """Retorna informações sobre plugins carregados."""
        return {
            "model_plugins": {
                name: plugin_class.__doc__ or "Sem descrição"
                for name, plugin_class in self.model_plugins.items()
            },
            "prompt_plugins": {
                name: plugin_class.__doc__ or "Sem descrição"
                for name, plugin_class in self.prompt_plugins.items()
            },
            "total_plugins": len(self.model_plugins) + len(self.prompt_plugins)
        }