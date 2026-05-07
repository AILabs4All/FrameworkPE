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

# Nota: Plugins de prompt agora são gerenciados via schemas YAML
# e execução genérica através do SchemaPromptPlugin

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