"""
Funções puras de scaffolding: criação da estrutura de diretórios, configuração
padrão e importação de plugins para um projeto Pangolin.

Estas funções recebem o objeto PangolinProject como primeiro argumento para
acessar seus atributos de caminho sem criar dependência circular.
"""

import shutil
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


_PROVIDER_TO_PLUGIN_FILE = {
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
    'palm': 'api_model.py',
}


def get_default_config(project_name: str) -> Dict[str, Any]:
    """Retorna a configuração padrão para um novo projeto."""
    return {
        "project": {
            "name": project_name,
            "description": "Projeto de teste e comparacao de prompts",
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
        },
        "data": {
            "input_columns": ["description"],
            "required_columns": ["id", "target"],
        },
        "models": [
            {
                "name": "ollama_gemma2:9b",
                "provider": "ollama",
                "temperature": 0.2,
                "max_tokens": 2048,
            }
        ],
        "prompt": {
            "technique": ["progressive_hint"],
            "schema_dir": "schema",
        },
        "output": {
            "format": "json",
            "save_metrics": True,
            "save_logs": True,
        },
    }


def create_project_structure(project) -> None:
    """Cria a árvore de diretórios e arquivos iniciais do projeto."""
    project.project_path.mkdir(parents=True, exist_ok=False)
    project.data_dir.mkdir(exist_ok=False)
    project.schema_dir.mkdir(exist_ok=False)
    project.model_dir.mkdir(exist_ok=False)
    project.logs_dir.mkdir(exist_ok=False)
    project.output_dir.mkdir(exist_ok=False)
    (project.model_dir / "__init__.py").touch()
    (project.schema_dir / ".gitkeep").touch()


def write_config(project, config: Dict[str, Any]) -> None:
    """Serializa e salva a configuração em config.yaml."""
    with open(project.config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def write_readme(project) -> None:
    """Gera e escreve o README.md padrão no diretório do projeto."""
    name = project.project_name
    content = f"""# {name}

Projeto de teste e comparacao de prompts.

## Estrutura do Projeto

```
{name}/
├── data/           # Base de dados (coloque seus arquivos CSV/JSON/XLSX aqui)
├── schema/         # Definições de técnicas de prompt em YAML
├── model/          # Diretorio do modelo
├── logs/           # Logs de execucao
├── output/         # Resultados das execucoes
├── config.yaml     # Configuracoes do projeto
└── README.md       # Este arquivo
```

## Como Usar

1. **Adicionar dados**: Coloque seus arquivos de dados em `data/`
2. **Configurar**: Edite `config.yaml` conforme necessario
3. **Aplicar configuracoes**: `pg apply`
4. **Executar**: `pg run`
5. **Ver resultados**: `ls output/`

---

Criado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    (project.project_path / "README.md").write_text(content, encoding='utf-8')


def import_model_plugins(project, config: Dict[str, Any]) -> List[str]:
    """
    Copia os arquivos de plugin de modelo do framework para o diretório model/ do projeto.

    Returns:
        Lista de nomes de arquivos importados.
    """
    imported: set = set()
    framework_plugins = Path(__file__).resolve().parent.parent.parent / "plugins" / "models"

    for model in config.get('models', []):
        provider = model.get('provider', 'ollama').lower()
        plugin_file = _PROVIDER_TO_PLUGIN_FILE.get(provider, 'api_model.py')
        source_file = framework_plugins / plugin_file

        if not source_file.exists():
            project.logger.warning(f"Arquivo de plugin não encontrado: {source_file}")
            continue

        dest_file = project.model_dir / plugin_file
        if not dest_file.exists():
            shutil.copy2(source_file, dest_file)
            imported.add(plugin_file)
            project.logger.info(f"Plugin de modelo importado: {plugin_file} (provider: {provider})")

        base_source = framework_plugins / "base_model.py"
        base_dest = project.model_dir / "base_model.py"
        if base_source.exists() and not base_dest.exists():
            shutil.copy2(base_source, base_dest)
            imported.add("base_model.py")
            project.logger.info("Base model importado: base_model.py")

    return list(imported)


def import_prompt_plugins(project, config: Dict[str, Any]) -> List[str]:
    """
    Copia para o projeto os schemas das técnicas declaradas em prompt.technique.

    Returns:
        Lista de nomes de schemas importados.
    """
    imported = []
    project.schema_dir.mkdir(exist_ok=True)

    prompt_cfg = config.get("prompt", {})
    all_techniques = prompt_cfg.get("technique", [])
    if isinstance(all_techniques, str):
        all_techniques = [all_techniques]

    if not all_techniques:
        return imported

    framework_schemas = Path(__file__).resolve().parent.parent.parent / "schemas"
    if not framework_schemas.exists():
        return imported

    for technique in all_techniques:
        schema_file = framework_schemas / f"{technique}.yaml"
        if not schema_file.exists():
            project.logger.warning("Schema não encontrado no framework: %s.yaml", technique)
            continue
        dest_file = project.schema_dir / schema_file.name
        if not dest_file.exists():
            shutil.copy2(schema_file, dest_file)
            imported.append(schema_file.name)
            project.logger.info("Schema de prompt importado: %s", schema_file.name)

    return imported
