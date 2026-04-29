import typer
from pangolin.cmd.apply import cmd_apply

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main(
    debug: bool = typer.Option(False, "--debug", help="Modo debug")
):
    """
    Aplicar configuracoes
    """
    class Args:
        pass
    
    args = Args()
    args.debug = debug
    
    exit_code = cmd_apply(args)
    if exit_code and exit_code != 0:
        raise typer.Exit(code=exit_code)
