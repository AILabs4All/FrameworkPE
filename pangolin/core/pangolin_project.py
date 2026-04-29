"""
Gerenciador de projetos Pangolin para classificação de incidentes.
Estrutura simplificada para projetos isolados.
"""

import json
import yaml
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logger import setup_logger


class PangolinProject:
    """
    Representa um projeto Pangolin isolado.
    
    Estrutura do projeto:
    - .env: Chave de API dos providers
    - data/: Base de dados
    - prompts/: Arquivos de prompts
    - model/: Diretório do modelo
    - config.yaml: Configurações do projeto
    """
    
    def __init__(self, project_name: str, base_dir: str = "."):
        """
        Inicializa um projeto Pangolin.
        
        Args:
            project_name: Nome do projeto
            base_dir: Diretório base onde o projeto será criado
        """
        self.project_name = project_name
        self.base_dir = Path(base_dir)
        
        # Define estrutura de diretórios
        self.project_path = self.base_dir / project_name
        self.env_path = self.project_path / ".env"
        self.data_dir = self.project_path / "data"
        self.prompts_dir = self.project_path / "prompts"
        self.logs_dir = self.project_path / "logs"
        self.metrics_dir = self.project_path / "logs"
        self.model_dir = self.project_path / "model"
        self.output_dir = self.project_path / "output"
        self.config_file = self.project_path / "config.yaml"

        self.logger = setup_logger(f"Pangolin-{self.project_name}")

    def create(self, config: Optional[Dict[str, Any]] = None):
        """
        Cria a estrutura do projeto.
        
        Args:
            config: Configuração inicial do projeto
        """
        try:
            # Verifica se já existe
            if self.project_path.exists():
                raise ValueError(f"Projeto '{self.project_name}' já existe em {self.project_path}")
            
            # Cria diretórios
            self.project_path.mkdir(parents=True, exist_ok=False)
            self.data_dir.mkdir(exist_ok=False)
            self.prompts_dir.mkdir(exist_ok=False)
            self.model_dir.mkdir(exist_ok=False)
            self.logs_dir.mkdir(exist_ok=False)
            self.output_dir.mkdir(exist_ok=False)
            
            # Cria arquivos __init__.py para tornar diretórios módulos Python
            (self.prompts_dir / "__init__.py").touch()
            (self.model_dir / "__init__.py").touch()
            
            # Cria config.yaml padrão
            default_config = config or self._get_default_config()
            self._save_config(default_config)
            
            # Cria README no diretório
            self._create_readme()
            
            self.logger.info(f"Projeto '{self.project_name}' criado em: {self.project_path}")
            
        except Exception as e:
            # Limpa se houver erro
            if self.project_path.exists():
                shutil.rmtree(self.project_path)
            raise RuntimeError(f"Erro ao criar projeto: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão do projeto."""
        return {
            "project": {
                "name": self.project_name,
                "description": "Projeto de teste e comparacao de prompts",
                "created_at": datetime.now().isoformat(),
                "version": "1.0.0"
            },
            "data": {
                "input_columns": ["description"],
                "required_columns": ["id", "target"]
            },
            "models": [
                {
                    "name": "ollama_gemma2:9b",
                    "provider": "ollama",
                    "temperature": 0.2,
                    "max_tokens": 2048
                }
            ],
            "prompt": {
                "technique": ["progressive_hint"],
                "custom_prompts_dir": "prompts",
                "available_techniques": [
                    "self_hint",
                    "zeroshot"
                ]
            },
            "output": {
                "format": "json",
                "save_metrics": True,
                "save_logs": True
            }
        }
    
    def _save_config(self, config: Dict[str, Any]):
        """Salva configuração em config.yaml."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, 
                      f, 
                      default_flow_style=False, 
                      allow_unicode=True, 
                      sort_keys=False
            )
    
    def _create_readme(self):
        """Cria README no diretório do projeto."""
        readme_content = f"""# {self.project_name}

Projeto de teste e comparacao de prompts.

## Estrutura do Projeto

```
{self.project_name}/
├── data/           # Base de dados (coloque seus arquivos CSV/JSON/XLSX aqui)
├── prompts/        # Arquivos de prompts customizados
├── model/          # Diretorio do modelo
├── logs/           # Logs de execucao
├── output/         # Resultados das execucoes
├── config.yaml     # Configuracoes do projeto
└── README.md       # Este arquivo
```

## Como Usar

1. **Adicionar dados**: Coloque seus arquivos de dados em `data/`
   ```bash
   cp seus_dados.csv data/
   ```

2. **Configurar**: Edite `config.yaml` conforme necessario
   ```bash
   nano config.yaml
   ```

3. **Aplicar configuracoes**: Execute dentro do diretorio do projeto
   ```bash
   # Se instalado via pip
   pg apply
   
   # OU se usando o wrapper (caminhos com espacos)
   ../run_pg.sh apply
   
   # OU chamando Python diretamente
   python3 ../pangolin_cli.py apply
   ```

4. **Executar processamento**:
   ```bash
   # Usando config.yaml
   ../run_pg.sh run
   
   # Ou sobrescrevendo parametros
   ../run_pg.sh run --columns descricao --model ollama_gemma2:9b --technique progressive_hint --output csv
   ```

5. **Ver resultados**:
   ```bash
   ls output/           # Arquivos de resultados
   ls logs/             # Logs e metricas
   cat logs/performance_*.json
   ```

## Exemplos de Comandos

```bash
# Ver informacoes do projeto
../run_pg.sh info

# Executar com verbose
../run_pg.sh run --verbose

# Testar diferentes tecnicas
../run_pg.sh run --technique progressive_hint
../run_pg.sh run --technique self_hint
../run_pg.sh run --technique hypothesis_testing

# Testar diferentes modelos
../run_pg.sh run --model ollama_llama3:8b
../run_pg.sh run --model ollama_gemma2:9b
```

## Configuracao

Veja `config.yaml` para todas as opcoes disponiveis.

Tecnicas disponiveis:
- progressive_hint
- progressive_rectification
- self_hint
- hypothesis_testing
- free_prompt
- zeroshot

---

Criado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        readme_file = self.project_path / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def load_config(self) -> Dict[str, Any]:
        """
        Carrega configuração do projeto.
        
        Returns:
            Dict com configurações do projeto
        """
        if not self.config_file.exists():
            raise FileNotFoundError(f"Arquivo config.yaml não encontrado em {self.project_path}")
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Valida estrutura e campos obrigatórios do config.yaml.
        
        Args:
            config: Configuração a ser validada
            
        Returns:
            Tupla (válido, lista_de_erros)
        """
        errors = []
        
        # Valida seções obrigatórias
        required_sections = ["project", "data", "models", "prompt", "output"]
        for section in required_sections:
            if section not in config:
                errors.append(f"Seção obrigatória ausente: {section}")
        
        # Valida campos do projeto
        if "project" in config:
            if "name" not in config["project"]:
                errors.append("Campo 'project.name' é obrigatório")
        
        # Valida dados
        if "data" in config:
            if "input_columns" not in config["data"]:
                errors.append("Campo 'data.input_columns' é obrigatório")
            elif not isinstance(config["data"]["input_columns"], list):
                errors.append("Campo 'data.input_columns' deve ser uma lista")
        # Valida modelos
        if "models" not in config:
            errors.append("Campo 'models' é obrigatório")
        elif not isinstance(config["models"], list) or len(config["models"]) == 0:
            errors.append("Campo 'models' deve ser uma lista com pelo menos um modelo")
        else:
            for i, mb in enumerate(config["models"]):
                if "name" not in mb:
                    errors.append(f"Campo 'name' é obrigatório no modelo[{i}]")
                if "provider" not in mb:
                    errors.append(f"Campo 'provider' é obrigatório no modelo[{i}]")
        
        # Valida prompt
        if "prompt" in config:
            if "technique" not in config["prompt"]:
                errors.append("Campo 'prompt.technique' é obrigatório")
        
        # Valida output
        if "output" in config:
            if "format" in config["output"]:
                valid_formats = ["json", "csv", "xlsx"]
                if config["output"]["format"] not in valid_formats:
                    errors.append(f"Formato de saída inválido. Use: {', '.join(valid_formats)}")
        
        return len(errors) == 0, errors
    
    def apply(self) -> Dict[str, Any]:
        """
        Aplica configurações do config.yaml ao projeto.
        
        Returns:
            Dict com status da aplicação
        """
        try:
            # Carrega configuração
            config = self.load_config()
            
            # Valida configuração
            is_valid, errors = self.validate_config(config)
            if not is_valid:
                raise ValueError(f"Configuração inválida:\n" + "\n".join(f"  - {e}" for e in errors))
            
            # Importa plugins de modelos especificados
            model_files = self._import_model_plugins(config)
            
            # Importa plugins de prompts especificados
            prompt_files = self._import_prompt_plugins(config)
            
            # Atualiza metadados
            config["project"]["last_applied"] = datetime.now().isoformat()
            self._save_config(config)
            
            self.logger.info(f"Configurações aplicadas ao projeto '{self.project_name}'")
            
            return {
                "status": "success",
                "message": f"Configurações aplicadas com sucesso",
                "config": config,
                "imported_files": {
                    "models": model_files,
                    "prompts": prompt_files
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao aplicar configurações: {e}")
            raise
    
    def _import_model_plugins(self, config: Dict[str, Any]) -> list[str]:
        """
        Importa arquivos de plugins de modelos para o projeto.
        
        Args:
            config: Configuração do projeto
            
        Returns:
            Lista de arquivos importados
        """
        imported = set()
        models = config.get('models', [])
        
        if not models:
            return list(imported)
        
        for model in models:
            provider = model.get('provider', 'ollama').lower()
            
            provider_map = {
                'ollama': 'local_model.py',
                'local': 'local_model.py',
                'huggingface': 'hungguiface_model.py',
                'hungifface': 'hungguiface_model.py',
                'openai': 'api_model.py',
                'anthropic': 'api_model.py',
                'gemini': 'api_model.py',
                'google': 'api_model.py',
                'cohere': 'api_model.py',
                'azure': 'api_model.py',
                'bedrock': 'api_model.py',
                'vertex': 'api_model.py',
                'palm': 'api_model.py'
            }
            
            plugin_file = provider_map.get(provider, 'api_model.py')
            framework_plugins = Path(__file__).resolve().parent.parent / "plugins" / "models"
            source_file = framework_plugins / plugin_file
            
            if source_file.exists():
                dest_file = self.model_dir / plugin_file
                if not dest_file.exists():
                    shutil.copy2(source_file, dest_file)
                    imported.add(plugin_file)
                    self.logger.info(f"Plugin de modelo importado: {plugin_file} (provider: {provider})")
                
                base_source = framework_plugins / "base_model.py"
                base_dest = self.model_dir / "base_model.py"
                if base_source.exists() and not base_dest.exists():
                    shutil.copy2(base_source, base_dest)
                    imported.add("base_model.py")
                    self.logger.info(f"Base model importado: base_model.py")
            else:
                self.logger.warning(f"Arquivo de plugin não encontrado: {source_file}")
            
        return list(imported)
    
    def _import_prompt_plugins(self, config: Dict[str, Any]) -> list[str]:
        """
        Importa arquivos de plugins de prompts para o projeto.
        
        Args:
            config: Configuração do projeto
            
        Returns:
            Lista de arquivos importados
        """
        imported = []
        technique = config.get('prompt', {}).get('technique', '')
        
        if not technique:
            return imported
        
        # Se technique é uma lista, pega o primeiro
        if isinstance(technique, list):
            techniques = technique
        else:
            techniques = [technique]
        
        # Mapeia técnicas para arquivos
        technique_map = {
            'progressive_hint': 'progressive_hint.py',
            'progressive_rectification': 'progressive_rectification.py',
            'self_hint': 'self_hint.py',
            'hypothesis_testing': 'hypothesis_testing.py',
            'free_prompt': 'free_prompt.py',
            'zeroshot': 'zeroshot_b.py'
        }
        
        # Caminho fonte (plugins do framework)
        framework_plugins = Path(__file__).resolve().parent.parent / "plugins" / "prompts"
        
        for tech in techniques:
            plugin_file = technique_map.get(tech)
            if not plugin_file:
                continue
                
            source_file = framework_plugins / plugin_file
            
            if source_file.exists():
                # Copia para o diretório prompts/ do projeto
                dest_file = self.prompts_dir / plugin_file
                if not dest_file.exists():
                    shutil.copy2(source_file, dest_file)
                    imported.append(plugin_file)
                    self.logger.info(f"Plugin de prompt importado: {plugin_file}")
        
        # Sempre importa base_prompt.py
        base_source = framework_plugins / "base_prompt.py"
        base_dest = self.prompts_dir / "base_prompt.py"
        if base_source.exists() and not base_dest.exists():
            shutil.copy2(base_source, base_dest)
            imported.append("base_prompt.py")
            self.logger.info(f"Base prompt importado: base_prompt.py")
        
        return imported
    
    def destroy(self):
        """Remove completamente o projeto."""
        try:
            if not self.project_path.exists():
                raise ValueError(f"Projeto '{self.project_name}' não existe")
            
            shutil.rmtree(self.project_path)
            self.logger.info(f"Projeto '{self.project_name}' removido")
            
        except Exception as e:
            self.logger.error(f"Erro ao remover projeto: {e}")
            raise
    
    def get_info(self) -> Dict[str, Any]:
        """
        Retorna informações do projeto.
        
        Returns:
            Dict com informações do projeto
        """
        config = self.load_config()
        
        return {
            "name": self.project_name,
            "path": str(self.project_path),
            "config": config,
            "directories": {
                "data": str(self.data_dir),
                "prompts": str(self.prompts_dir),
                "model": str(self.model_dir),
                "logs": str(self.logs_dir),
                "output": str(self.output_dir)
            },
            "file_counts": {
                "data": len(list(self.data_dir.glob("*"))) if self.data_dir.exists() else 0,
                "prompts": len(list(self.prompts_dir.glob("*"))) if self.prompts_dir.exists() else 0,
                "model": len(list(self.model_dir.glob("*"))) if self.model_dir.exists() else 0,
                "logs": len(list(self.logs_dir.glob("*"))) if self.logs_dir.exists() else 0,
                "output": len(list(self.output_dir.glob("*"))) if self.output_dir.exists() else 0
            }
        }
    
    def get_results_path(self, filename: str) -> Path:
        """
        Retorna caminho completo para arquivo de resultado.
        
        Args:
            filename: Nome do arquivo de resultado
            
        Returns:
            Path completo para o arquivo
        """
        return self.output_dir / filename
    
    def get_metrics_path(self, filename: str) -> Path:
        """
        Retorna caminho completo para arquivo de métricas.
        
        Args:
            filename: Nome do arquivo de métricas
            
        Returns:
            Path completo para o arquivo
        """
        return self.logs_dir / filename
    
    def get_log_path(self, filename: str) -> Path:
        """
        Retorna caminho completo para arquivo de log.
        
        Args:
            filename: Nome do arquivo de log
            
        Returns:
            Path completo para o arquivo
        """
        return self.logs_dir / filename
    
    @staticmethod
    def find_project_root(start_path: Path = None) -> Optional[Path]:
        """
        Encontra o diretório raiz do projeto procurando config.yaml.
        
        Args:
            start_path: Caminho inicial da busca (padrão: diretório atual)
            
        Returns:
            Path do projeto ou None se não encontrado
        """
        if start_path is None:
            start_path = Path.cwd()
        
        current = start_path.resolve()
        
        # Procura config.yaml no diretório atual e nos pais
        while current != current.parent:
            config_file = current / "config.yaml"
            if config_file.exists():
                return current
            current = current.parent
        
        return None
    
    @staticmethod
    def list_projects(base_dir: str = ".") -> list:
        """
        Lista todos os projetos Pangolin em um diretório.
        
        Args:
            base_dir: Diretório base para buscar projetos
            
        Returns:
            Lista de informações dos projetos
        """
        base_path = Path(base_dir)
        projects = []
        
        if not base_path.exists():
            return []
        
        for item in base_path.iterdir():
            if item.is_dir():
                config_file = item / "config.yaml"
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = yaml.safe_load(f)
                        
                        projects.append({
                            "name": item.name,
                            "path": str(item),
                            "description": config.get("project", {}).get("description", ""),
                            "created_at": config.get("project", {}).get("created_at", ""),
                            "version": config.get("project", {}).get("version", "")
                        })
                    except Exception:
                        continue
        
        return projects
    
    @staticmethod
    def load_from_current_dir() -> Optional['PangolinProject']:
        """
        Carrega projeto do diretório atual.
        
        Returns:
            Instância do projeto ou None se não estiver em um projeto
        """
        project_root = PangolinProject.find_project_root()
        
        if project_root is None:
            return None
        
        project_name = project_root.name
        parent_dir = project_root.parent
        
        project = PangolinProject(project_name, str(parent_dir))
        
        # Verifica se a estrutura existe
        if not project.config_file.exists():
            return None
        
        return project
    
    def __str__(self):
        return f"PangolinProject(name='{self.project_name}', path='{self.project_path}')"
    
    def __repr__(self):
        return self.__str__()
