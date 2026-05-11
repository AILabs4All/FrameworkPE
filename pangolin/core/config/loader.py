import json
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from ..observability.logger import setup_logger


class ConfigLoader:
    """Carrega arquivos de configuração JSON ou YAML com suporte a variáveis de ambiente."""

    def __init__(self):
        self.logger = setup_logger("ConfigLoader")

    @staticmethod
    def load(config_path: str = "config.json") -> Dict[str, Any]:
        """
        Carrega configuração de arquivo JSON ou YAML.

        Args:
            config_path: Caminho para o arquivo de configuração

        Returns:
            Dict com configurações carregadas
        """
        loader = ConfigLoader()
        return loader._load_config(config_path)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Carrega configuração de arquivo."""
        if not os.path.exists(config_path):
            self.logger.warning(
                f"Arquivo de configuração '{config_path}' não encontrado. "
                "Usando configuração padrão."
            )
            return self._load_default_config()

        try:
            path = Path(config_path)
            if path.suffix.lower() in {'.yaml', '.yml'}:
                return self._load_yaml(config_path)
            return self._load_json(config_path)
        except Exception as e:
            self.logger.error(f"Erro ao carregar configuração de '{config_path}': {e}")
            self.logger.info("Usando configuração padrão.")
            return self._load_default_config()

    def _load_json(self, config_path: str) -> Dict[str, Any]:
        """Carrega configuração de arquivo JSON."""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.logger.info(f"Configuração carregada de: {config_path}")
        return self._resolve_env_variables(config)

    def _load_yaml(self, config_path: str) -> Dict[str, Any]:
        """Carrega configuração de arquivo YAML."""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        self.logger.info(f"Configuração YAML carregada de: {config_path}")
        return self._resolve_env_variables(config)

    def _load_default_config(self) -> Dict[str, Any]:
        """Carrega configuração padrão."""
        default_path = Path(__file__).resolve().parent.parent.parent / "config" / "default_config.json"
        if default_path.exists():
            return self._load_json(str(default_path))
        return {
            "framework": {"name": "Security Incident Framework", "version": "2.0.0"},
            "models": {},
            "prompt_techniques": {},
            "logging": {"level": "INFO", "log_dir": "logs"},
        }

    def _resolve_env_variables(self, config: Any) -> Any:
        """Resolve referências ${VAR} e ${VAR:-default} na configuração."""
        if isinstance(config, dict):
            return {k: self._resolve_env_variables(v) for k, v in config.items()}
        if isinstance(config, list):
            return [self._resolve_env_variables(item) for item in config]
        if isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            env_var = config[2:-1]
            default_value = None
            if ":-" in env_var:
                env_var, default_value = env_var.split(":-", 1)
            return os.getenv(env_var, default_value)
        return config

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida se a configuração contém os campos obrigatórios."""
        required_fields = ["framework", "models", "prompt_techniques"]

        for field in required_fields:
            if field not in config:
                self.logger.error(f"Campo obrigatório '{field}' não encontrado na configuração")
                return False

        if not config["models"]:
            self.logger.error("Nenhum modelo configurado")
            return False

        if not config["prompt_techniques"]:
            self.logger.error("Nenhuma técnica de prompt configurada")
            return False

        self.logger.info("Configuração válida")
        return True

    def get_model_config(self, config: Dict[str, Any], model_name: str) -> Optional[Dict[str, Any]]:
        """Retorna configuração de um modelo específico."""
        return config.get("models", {}).get(model_name)

    def get_prompt_config(self, config: Dict[str, Any], prompt_name: str) -> Optional[Dict[str, Any]]:
        """Retorna configuração de uma técnica de prompt específica."""
        return config.get("prompt_techniques", {}).get(prompt_name)

    def list_available_models(self, config: Dict[str, Any]) -> list:
        """Lista modelos disponíveis na configuração."""
        return list(config.get("models", {}).keys())

    def list_available_prompts(self, config: Dict[str, Any]) -> list:
        """Lista técnicas de prompt disponíveis na configuração."""
        return list(config.get("prompt_techniques", {}).keys())
