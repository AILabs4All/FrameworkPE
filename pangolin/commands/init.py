import typer
from typing import Optional
from pangolin.cmd.init import cmd_init

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main(
    name: str = typer.Option(..., "--name", help="Nome do projeto"),
):
    """
    Cria um novo projeto Pangolin
    """
    class Args:
        pass
    
    args = Args()
    args.name = name
    
    exit_code = cmd_init(args)
    if exit_code and exit_code != 0:
        raise typer.Exit(code=exit_code)
