"""
PangolinProject — representa e gerencia o ciclo de vida de um projeto isolado.
"""

import shutil
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..observability.logger import setup_logger
from .scaffold import (
    create_project_structure,
    get_default_config,
    import_model_plugins,
    import_prompt_plugins,
    write_config,
    write_readme,
)


class PangolinProject:
    """
    Representa um projeto Pangolin isolado.

    Estrutura criada pelo projeto:
        project_name/
        ├── data/        — arquivos de entrada (CSV/JSON/XLSX)
        ├── schema/      — schemas YAML de técnicas de prompt
        ├── model/       — plugins de modelo copiados do framework
        ├── logs/        — logs e métricas de execução
        ├── output/      — resultados gerados
        └── config.yaml  — configuração do projeto
    """

    def __init__(self, project_name: str, base_dir: str = "."):
        self.project_name = project_name
        self.base_dir = Path(base_dir)

        self.project_path = self.base_dir / project_name
        self.env_path = self.project_path / ".env"
        self.data_dir = self.project_path / "data"
        self.schema_dir = self.project_path / "schema"
        self.logs_dir = self.project_path / "logs"
        self.metrics_dir = self.project_path / "logs"
        self.model_dir = self.project_path / "model"
        self.output_dir = self.project_path / "output"
        self.config_file = self.project_path / "config.yaml"

        self.logger = setup_logger(f"Pangolin-{self.project_name}")

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def create(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Cria a estrutura do projeto em disco.

        Args:
            config: Configuração inicial; usa padrão se None.

        Raises:
            ValueError: Se o projeto já existir.
            RuntimeError: Se a criação falhar (a estrutura parcial é removida).
        """
        if self.project_path.exists():
            raise ValueError(f"Projeto '{self.project_name}' já existe em {self.project_path}")

        try:
            create_project_structure(self)
            write_config(self, config or get_default_config(self.project_name))
            write_readme(self)
            self.logger.info(f"Projeto '{self.project_name}' criado em: {self.project_path}")
        except Exception as e:
            if self.project_path.exists():
                shutil.rmtree(self.project_path)
            raise RuntimeError(f"Erro ao criar projeto: {e}")

    def apply(self) -> Dict[str, Any]:
        """
        Aplica o config.yaml ao projeto: valida, importa plugins e schemas.

        Returns:
            Dict com status, config aplicado e arquivos importados.
        """
        config = self.load_config()

        is_valid, errors = self.validate_config(config)
        if not is_valid:
            raise ValueError("Configuração inválida:\n" + "\n".join(f"  - {e}" for e in errors))

        model_files = import_model_plugins(self, config)
        schema_files = import_prompt_plugins(self, config)

        config["project"]["last_applied"] = datetime.now().isoformat()
        write_config(self, config)

        self.logger.info(f"Configurações aplicadas ao projeto '{self.project_name}'")
        return {
            "status": "success",
            "message": "Configurações aplicadas com sucesso",
            "config": config,
            "imported_files": {"models": model_files, "schemas": schema_files},
        }

    def destroy(self) -> None:
        """Remove completamente o projeto do disco."""
        if not self.project_path.exists():
            raise ValueError(f"Projeto '{self.project_name}' não existe")
        shutil.rmtree(self.project_path)
        self.logger.info(f"Projeto '{self.project_name}' removido")

    # ------------------------------------------------------------------
    # Configuração
    # ------------------------------------------------------------------

    def load_config(self) -> Dict[str, Any]:
        """Carrega e retorna o config.yaml do projeto."""
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"Arquivo config.yaml não encontrado em {self.project_path}"
            )
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida estrutura e campos obrigatórios do config.yaml.

        Returns:
            Tupla (válido, lista_de_erros)
        """
        errors = []

        for section in ("project", "data", "models", "prompt", "output"):
            if section not in config:
                errors.append(f"Seção obrigatória ausente: {section}")

        if "project" in config and "name" not in config["project"]:
            errors.append("Campo 'project.name' é obrigatório")

        if "data" in config:
            if "input_columns" not in config["data"]:
                errors.append("Campo 'data.input_columns' é obrigatório")
            elif not isinstance(config["data"]["input_columns"], list):
                errors.append("Campo 'data.input_columns' deve ser uma lista")

        if "models" not in config:
            errors.append("Campo 'models' é obrigatório")
        elif not isinstance(config["models"], list) or not config["models"]:
            errors.append("Campo 'models' deve ser uma lista com pelo menos um modelo")
        else:
            for i, mb in enumerate(config["models"]):
                if "name" not in mb:
                    errors.append(f"Campo 'name' é obrigatório no modelo[{i}]")
                if "provider" not in mb:
                    errors.append(f"Campo 'provider' é obrigatório no modelo[{i}]")

        if "prompt" in config:
            if "technique" not in config["prompt"]:
                errors.append("Campo 'prompt.technique' é obrigatório")
            schema_dir = config["prompt"].get("schema_dir")
            if schema_dir is not None and not isinstance(schema_dir, str):
                errors.append("Campo 'prompt.schema_dir' deve ser uma string")

        if "output" in config:
            fmt = config["output"].get("format")
            if fmt and fmt not in {"json", "csv", "xlsx"}:
                errors.append("Formato de saída inválido. Use: json, csv ou xlsx")

        return len(errors) == 0, errors

    # ------------------------------------------------------------------
    # Caminhos
    # ------------------------------------------------------------------

    def get_results_path(self, filename: str) -> Path:
        """Retorna caminho completo para um arquivo de resultado."""
        return self.output_dir / filename

    def get_prompt_schema_path(self, prompt_name: str) -> Path:
        """
        Retorna o caminho para o schema YAML de uma técnica de prompt.
        Prioriza o schema local do projeto; fallback para schemas internos do framework.
        """
        local = self.schema_dir / f"{prompt_name}.yaml"
        if local.exists():
            return local
        return Path(__file__).resolve().parent.parent.parent / "schemas" / f"{prompt_name}.yaml"

    def load_prompt_schema(self, prompt_name: str) -> Dict[str, Any]:
        """Carrega e retorna o schema YAML de uma técnica de prompt."""
        schema_path = self.get_prompt_schema_path(prompt_name)
        if not schema_path.exists():
            raise FileNotFoundError(
                f"Schema de prompt não encontrado: {prompt_name} ({schema_path})"
            )
        with open(schema_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError(f"Schema de prompt inválido ou vazio: {schema_path}")
        return data

    def get_metrics_path(self, filename: str) -> Path:
        """Retorna caminho completo para um arquivo de métricas."""
        return self.logs_dir / filename

    def get_log_path(self, filename: str) -> Path:
        """Retorna caminho completo para um arquivo de log."""
        return self.logs_dir / filename

    # ------------------------------------------------------------------
    # Informações
    # ------------------------------------------------------------------

    def get_info(self) -> Dict[str, Any]:
        """Retorna metadados e estatísticas do projeto."""
        config = self.load_config()
        return {
            "name": self.project_name,
            "path": str(self.project_path),
            "config": config,
            "directories": {
                "data": str(self.data_dir),
                "schema": str(self.schema_dir),
                "model": str(self.model_dir),
                "logs": str(self.logs_dir),
                "output": str(self.output_dir),
            },
            "file_counts": {
                "data": len(list(self.data_dir.glob("*"))) if self.data_dir.exists() else 0,
                "model": len(list(self.model_dir.glob("*"))) if self.model_dir.exists() else 0,
                "logs": len(list(self.logs_dir.glob("*"))) if self.logs_dir.exists() else 0,
                "output": len(list(self.output_dir.glob("*"))) if self.output_dir.exists() else 0,
            },
        }

    # ------------------------------------------------------------------
    # Helpers estáticos
    # ------------------------------------------------------------------

    @staticmethod
    def find_project_root(start_path: Optional[Path] = None) -> Optional[Path]:
        """
        Sobe na hierarquia de diretórios procurando config.yaml.

        Returns:
            Path do diretório contendo config.yaml, ou None se não encontrado.
        """
        current = (start_path or Path.cwd()).resolve()
        while current != current.parent:
            if (current / "config.yaml").exists():
                return current
            current = current.parent
        return None

    @staticmethod
    def list_projects(base_dir: str = ".") -> List[Dict[str, Any]]:
        """Lista todos os projetos Pangolin encontrados em base_dir."""
        base_path = Path(base_dir)
        if not base_path.exists():
            return []

        projects = []
        for item in base_path.iterdir():
            if not item.is_dir():
                continue
            config_file = item / "config.yaml"
            if not config_file.exists():
                continue
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                projects.append({
                    "name": item.name,
                    "path": str(item),
                    "description": config.get("project", {}).get("description", ""),
                    "created_at": config.get("project", {}).get("created_at", ""),
                    "version": config.get("project", {}).get("version", ""),
                })
            except Exception:
                continue

        return projects

    @staticmethod
    def load_from_current_dir() -> Optional["PangolinProject"]:
        """
        Carrega o projeto a partir do diretório de trabalho atual.

        Returns:
            Instância de PangolinProject, ou None se não estiver em um projeto.
        """
        project_root = PangolinProject.find_project_root()
        if project_root is None:
            return None

        project = PangolinProject(project_root.name, str(project_root.parent))
        if not project.config_file.exists():
            return None

        return project

    def __str__(self) -> str:
        return f"PangolinProject(name='{self.project_name}', path='{self.project_path}')"

    def __repr__(self) -> str:
        return self.__str__()
