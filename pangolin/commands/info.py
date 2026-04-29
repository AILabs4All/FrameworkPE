import typer
from pangolin.cmd.info import cmd_info

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main():
    """
    Ver informacoes do projeto atual
    """
    class Args:
        pass
    
    args = Args()
    
    exit_code = cmd_info(args)
    if exit_code and exit_code != 0:
        raise typer.Exit(code=exit_code)
