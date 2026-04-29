import sys
from pathlib import Path

# Adiciona o diretório base para importações funcionarem como esperado (ex: 'import core...')
sys.path.insert(0, str(Path(__file__).resolve().parent))

import typer
from pangolin.commands import run, init, apply, destroy, list_cmd, info

app = typer.Typer(help="Pangolin CLI", no_args_is_help=True)

app.add_typer(init.app, name="init")
app.add_typer(run.app, name="run")
app.add_typer(apply.app, name="apply")
app.add_typer(destroy.app, name="destroy")
app.add_typer(list_cmd.app, name="list")
app.add_typer(info.app, name="info")

def main():
    app()

if __name__ == "__main__":
    main()