"""Testes para o CLI do Pangolin."""

import argparse
import shutil
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pangolin_cli import cmd_init


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
        assert (project_path / "prompts").is_dir()
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
