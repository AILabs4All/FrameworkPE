import typer
from pangolin.cmd.destroy import cmd_destroy

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main(
    name: str = typer.Option(..., "--name", help="Nome do projeto"),
    force: bool = typer.Option(False, "--force", help="Pular confirmacao")
):
    """
    Remover projeto (dentro do diretorio do projeto)
    """
    class Args:
        pass
    
    args = Args()
    args.name = name
    args.force = force
    
    exit_code = cmd_destroy(args)
    if exit_code and exit_code != 0:
        raise typer.Exit(code=exit_code)
