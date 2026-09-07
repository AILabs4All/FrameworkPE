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
