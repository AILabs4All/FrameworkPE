"""Testes para o CLI do Pangolin."""

import argparse
import shutil
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pangolin"))

from pangolin.cmd.init import cmd_init


@pytest.fixture
def tmp_project_dir(tmp_path, monkeypatch):
    """Muda o diretório de trabalho para um diretório temporário."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _make_args(name=None):
    """Cria um namespace simulando os argumentos do argparse."""
    return argparse.Namespace(name=name)


class TestCmdInit:

    def test_init_sem_nome_retorna_erro(self, capsys):
        args = _make_args(name=None)
        result = cmd_init(args)
        assert result == 1
        captured = capsys.readouterr()
        assert "obrigatório" in captured.out

    def test_init_cria_projeto_com_sucesso(self, tmp_project_dir, capsys):
        args = _make_args(name="meu_projeto")
        result = cmd_init(args)
        assert result == 0

        project_path = tmp_project_dir / "meu_projeto"
        assert project_path.exists()
        assert (project_path / "data").is_dir()
        assert (project_path / "schema").is_dir()
        assert (project_path / "model").is_dir()
        assert (project_path / "config.yaml").exists()

        captured = capsys.readouterr()
        assert "criado com sucesso" in captured.out

    def test_init_projeto_ja_existente_retorna_erro(self, tmp_project_dir, capsys):
        args = _make_args(name="duplicado")
        # Cria pela primeira vez
        cmd_init(args)
        # Tenta criar novamente
        result = cmd_init(args)
        assert result == 1
        captured = capsys.readouterr()
        assert "Erro" in captured.out

    def test_init_nome_vazio_retorna_erro(self, capsys):
        args = _make_args(name="")
        result = cmd_init(args)
        assert result == 1

    def test_init_exibe_proximos_passos(self, tmp_project_dir, capsys):
        args = _make_args(name="teste_passos")
        cmd_init(args)
        captured = capsys.readouterr()
        assert "Próximos passos" in captured.out
        assert "config.yaml" in captured.out


class TestPluginNamingHuggingface:

    def test_model_file_renomeado_para_huggingface(self):
        models_dir = Path(__file__).resolve().parent.parent / "pangolin" / "plugins" / "models"
        assert (models_dir / "huggingface_model.py").exists()
        assert not (models_dir / "hungguiface_model.py").exists()

    def test_nenhum_alias_typo_huggingface(self):
        root = Path(__file__).resolve().parent.parent
        for subdir in ("pangolin", "docs"):
            for py_file in (root / subdir).rglob("*.py"):
                content = py_file.read_text(encoding="utf-8")
                assert "hungguiface" not in content, f"typo em {py_file}"
                assert "hungifface" not in content, f"typo em {py_file}"

    def test_plugin_manager_registra_huggingface(self):
        from core.plugin_manager import PluginManager
        pm = PluginManager()
        assert "HuggingfaceModel" in pm.list_available_models()


class TestPluginResolution:

    def test_resolve_model_huggingface(self):
        from core.plugin_manager import PluginManager
        pm = PluginManager()
        cls = pm.resolve_model("huggingface")
        assert cls.__name__ == "HuggingfaceModel"

    def test_resolve_model_ollama(self):
        from core.plugin_manager import PluginManager
        pm = PluginManager()
        assert pm.resolve_model("ollama").__name__ == "LocalModel"

    def test_resolve_model_upper_case_ignorado(self):
        from core.plugin_manager import PluginManager
        pm = PluginManager()
        assert pm.resolve_model("OPENAI").__name__ == "APIModel"

    def test_resolve_model_desconhecido_sugere_correcao(self):
        from core.plugin_manager import PluginManager
        pm = PluginManager()
        with pytest.raises(ValueError) as exc:
            pm.resolve_model("hugginface")
        assert "não reconhecido" in str(exc.value)
        assert "Você quis dizer 'huggingface'" in str(exc.value)

    def test_resolve_schema_file_existente(self):
        from core.plugin_manager import PluginManager
        pm = PluginManager()
        path = pm.resolve_schema_file("zeroshot")
        assert path.exists()
        assert path.name == "zeroshot.yaml"

    def test_resolve_schema_file_desconhecido_sugere_correcao(self):
        from core.plugin_manager import PluginManager
        pm = PluginManager()
        with pytest.raises(ValueError) as exc:
            pm.resolve_schema_file("zero_shot")
        assert "Você quis dizer 'zeroshot'" in str(exc.value)

    def test_mapas_provider_consistentes(self):
        from core.plugin_manager import PROVIDER_TO_MODEL, MODEL_MODULE_FILES
        assert set(PROVIDER_TO_MODEL) == set(MODEL_MODULE_FILES)

    def test_tecnicas_disponiveis_igual_aos_schemas(self):
        from core.plugin_manager import PluginManager
        schemas_dir = (
            Path(__file__).resolve().parent.parent
            / "pangolin" / "schemas"
        )
        esperado = sorted(p.stem for p in schemas_dir.glob("*.yaml"))
        assert PluginManager().get_available_techniques() == esperado


class TestRunNoSilentFallback:

    def _criar_projeto(self, tmp_path, models=None):
        from core.project.pangolin_project import PangolinProject
        from core.project import scaffold
        models = models or [
            {"name": "meu_modelo", "provider": "ollama", "temperature": 0.2,
             "max_tokens": 2048}
        ]
        cfg = {
            "project": {"name": "proj", "description": "x", "created_at": "2026-01-01",
                        "version": "1.0.0"},
            "data": {"input_columns": ["description"], "required_columns": ["id", "target"]},
            "models": models,
            "prompt": {"technique": ["zeroshot"], "schema_dir": "schema"},
            "output": {"format": "json", "save_metrics": True, "save_logs": True},
        }
        p = PangolinProject("proj", base_dir=str(tmp_path))
        scaffold.create_project_structure(p)
        scaffold.write_config(p, cfg)
        (p.data_dir / "dados.csv").write_text(
            "id,target,description\n1,cat,item de teste\n", encoding="utf-8"
        )
        return p

    def test_run_model_inexistente_falha_com_lista(self, tmp_path, monkeypatch, capsys):
        from pangolin.cmd.run import run_command
        p = self._criar_projeto(tmp_path)
        monkeypatch.chdir(p.project_path)
        result = run_command(model="nao_existe")
        assert result == 1
        out = capsys.readouterr().out
        assert "não encontrado" in out
        assert "meu_modelo" in out
        assert "ollama" not in out

    def test_loader_yaml_invalido_levanta_erro(self, tmp_path):
        import yaml
        from core.config.loader import ConfigLoader
        bad = tmp_path / "config.yaml"
        bad.write_text("models: [arquivo quebrado\n", encoding="utf-8")
        with pytest.raises(yaml.YAMLError):
            ConfigLoader().load(str(bad))

    def test_loader_arquivo_ausente_usa_default(self, tmp_path):
        from core.config.loader import ConfigLoader
        cfg = ConfigLoader().load(str(tmp_path / "config.yaml"))
        assert "framework" in cfg


class TestFrameworkFailFast:

    def test_provider_desconhecido_nao_vira_api_model(self, tmp_path, monkeypatch):
        from core.framework import PangolinFramework
        from unittest.mock import patch, MagicMock
        project = MagicMock()
        project.logs_dir = tmp_path
        project.metrics_dir = tmp_path
        project.load_prompt_schema = MagicMock()

        import pandas as pd
        df = pd.DataFrame({"id": [1], "target": ["cat"], "description": ["x"]})

        framework = PangolinFramework(project=project)
        with patch("core.framework.load_data_files", return_value=[df]):
            with patch("core.framework.validate_columns", return_value=True):
                with pytest.raises(ValueError) as exc:
                    framework.process_incidents(
                        input_dir=str(tmp_path),
                        columns=["description"],
                        model_config={"name": "m", "provider": "hugginface"},
                        prompt_techniques=["zeroshot"],
                    )
        assert "não reconhecido" in str(exc.value)
        assert "Você quis dizer" in str(exc.value)


class TestDestroySecurity:

    def _criar_projeto_disk(self, tmp_path, name="proj"):
        from core.project.pangolin_project import PangolinProject
        from core.project import scaffold
        cfg = {
            "project": {"name": name, "description": "x", "created_at": "2026-01-01",
                        "version": "1.0.0"},
            "data": {"input_columns": ["description"], "required_columns": ["id", "target"]},
            "models": [{"name": "m", "provider": "ollama"}],
            "prompt": {"technique": ["zeroshot"], "schema_dir": "schema"},
            "output": {"format": "json", "save_metrics": True, "save_logs": True},
        }
        p = PangolinProject(name, base_dir=str(tmp_path))
        scaffold.create_project_structure(p)
        scaffold.write_config(p, cfg)
        return p

    def test_find_project_root_ignora_config_sem_secao_project(self, tmp_path, monkeypatch):
        (tmp_path / "config.yaml").write_text("foo: bar\n", encoding="utf-8")
        (tmp_path / "nested").mkdir()
        monkeypatch.chdir(tmp_path / "nested")
        from core.project.pangolin_project import PangolinProject
        assert PangolinProject.find_project_root() is None

    def test_find_project_root_aceita_config_com_secao_project(self, tmp_path, monkeypatch):
        (tmp_path / "config.yaml").write_text(
            "project:\n  name: x\n", encoding="utf-8"
        )
        (tmp_path / "nested").mkdir()
        monkeypatch.chdir(tmp_path / "nested")
        from core.project.pangolin_project import PangolinProject
        assert PangolinProject.find_project_root().resolve() == tmp_path.resolve()

    def test_find_project_root_ignora_config_yaml_quebrado(self, tmp_path, monkeypatch):
        (tmp_path / "config.yaml").write_text("a: [quebrado\n", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        from core.project.pangolin_project import PangolinProject
        assert PangolinProject.find_project_root() is None

    def test_destroy_recusa_remover_sem_config_yaml(self, tmp_path):
        from core.project.pangolin_project import PangolinProject
        p = PangolinProject("proj", base_dir=str(tmp_path))
        p.project_path.mkdir(parents=True)
        with pytest.raises(ValueError) as exc:
            p.destroy()
        assert "config.yaml ausente" in str(exc.value)
        assert p.project_path.exists()

    def test_destroy_chdir_para_parent(self, tmp_path, monkeypatch):
        p = self._criar_projeto_disk(tmp_path)
        (p.data_dir / "dados.csv").write_text("id,target\n1,cat\n", encoding="utf-8")
        (p.output_dir / "saida.json").write_text("[]", encoding="utf-8")
        monkeypatch.chdir(p.project_path)
        p.destroy()
        assert not p.project_path.exists()
        assert Path.cwd().resolve() == tmp_path.resolve()

    def test_destroy_conta_arquivos_antes_de_remover(self, tmp_path, monkeypatch):
        p = self._criar_projeto_disk(tmp_path)
        (p.data_dir / "dados.csv").write_text("id,target\n1,cat\n", encoding="utf-8")
        (p.output_dir / "saida.json").write_text("[]", encoding="utf-8")
        monkeypatch.chdir(p.project_path)
        p.destroy()
        assert not p.project_path.exists()
