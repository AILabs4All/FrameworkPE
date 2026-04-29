import typer
from typing import Optional
from pangolin.cmd.run import run_command

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main(
    columns: Optional[str] = typer.Option(None, help="Colunas separadas por virgula"),
    model: Optional[str] = typer.Option(None, help="Modelo LLM"),
    technique: Optional[str] = typer.Option(None, help="Tecnica de prompt"),
    output: Optional[str] = typer.Option(None, help="Formato de saida"),
    max_iterations: Optional[int] = typer.Option(None, help="Numero maximo de iteracoes"),
    temperature: Optional[float] = typer.Option(None, help="Temperatura do LLM"),
    max_tokens: Optional[int] = typer.Option(None, help="Maximo de tokens de resposta"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Saida detalhada"),
):
    """
    Executa um experimento Pangolin
    """

    cols = columns.split(",") if columns else None

    exit_code = run_command(
        columns=cols,
        model=model,
        technique=technique,
        output=output,
        max_iterations=max_iterations,
        temperature=temperature,
        max_tokens=max_tokens,
        verbose=verbose,
    )

    if exit_code and exit_code != 0:
        raise typer.Exit(code=exit_code)