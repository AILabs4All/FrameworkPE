import typer
from pangolin.cmd.list import cmd_list

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main():
    """
    Listar todos os projetos
    """
    class Args:
        pass
    
    args = Args()
    
    exit_code = cmd_list(args)
    if exit_code and exit_code != 0:
        raise typer.Exit(code=exit_code)
