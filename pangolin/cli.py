"""Interface de linha de comando do Pangolin."""

from types import SimpleNamespace
from typing import Optional

import typer

from pangolin.cmd.apply import cmd_apply
from pangolin.cmd.destroy import cmd_destroy
from pangolin.cmd.info import cmd_info
from pangolin.cmd.init import cmd_init
from pangolin.cmd.list import cmd_list
from pangolin.cmd.run import run_command

app = typer.Typer(
    name="pg",
    help="Gerencie projetos e execute experimentos de prompt engineering.",
    no_args_is_help=True,
)


def _exit_on_error(exit_code: int) -> None:
    if exit_code:
        raise typer.Exit(code=exit_code)


@app.command()
def init(name: str = typer.Option(..., "--name", help="Nome do projeto novo.")) -> None:
    """Cria a estrutura de um projeto Pangolin."""
    _exit_on_error(cmd_init(SimpleNamespace(name=name)))


@app.command()
def apply(
    debug: bool = typer.Option(False, "--debug", help="Mostra detalhes em caso de erro."),
) -> None:
    """Valida a configuração e importa schemas do projeto atual."""
    _exit_on_error(cmd_apply(SimpleNamespace(debug=debug)))


@app.command()
def run(
    columns: Optional[str] = typer.Option(
        None, "--columns", help="Colunas de entrada separadas por vírgula."
    ),
    model: Optional[str] = typer.Option(
        None, "--model", help="Nome de um modelo definido em config.yaml."
    ),
    technique: Optional[str] = typer.Option(
        None, "--technique", help="Sobrescreve a técnica definida em config.yaml."
    ),
    output: Optional[str] = typer.Option(
        None, "--output", help="Formato de saída: csv, json ou xlsx."
    ),
    max_iterations: Optional[int] = typer.Option(
        None, "--max-iterations", min=1, help="Limite de iterações da técnica."
    ),
    temperature: Optional[float] = typer.Option(
        None, "--temperature", min=0.0, max=2.0, help="Temperatura do modelo."
    ),
    max_tokens: Optional[int] = typer.Option(
        None, "--max-tokens", min=1, help="Limite de tokens da resposta."
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Mostra o traceback completo."),
) -> None:
    """Executa as técnicas configuradas no projeto atual."""
    if output is not None and output.lower() not in {"csv", "json", "xlsx"}:
        raise typer.BadParameter("use csv, json ou xlsx", param_hint="--output")
    if columns is not None and not any(column.strip() for column in columns.split(",")):
        raise typer.BadParameter("informe ao menos uma coluna", param_hint="--columns")

    exit_code = run_command(
        columns=[column.strip() for column in columns.split(",") if column.strip()]
        if columns
        else None,
        model=model,
        technique=technique,
        output=output.lower() if output else None,
        max_iterations=max_iterations,
        temperature=temperature,
        max_tokens=max_tokens,
        verbose=verbose,
    )
    _exit_on_error(exit_code)


@app.command("list")
def list_projects() -> None:
    """Lista projetos encontrados no diretório atual."""
    _exit_on_error(cmd_list(SimpleNamespace()))


@app.command()
def info() -> None:
    """Exibe caminhos e configuração do projeto atual."""
    _exit_on_error(cmd_info(SimpleNamespace()))


@app.command()
def destroy(
    name: str = typer.Option(..., "--name", help="Nome do projeto a remover."),
    force: bool = typer.Option(False, "--force", "-f", help="Remove sem pedir confirmação."),
) -> None:
    """Remove o projeto atual e todos os seus arquivos."""
    _exit_on_error(cmd_destroy(SimpleNamespace(name=name, force=force)))


def main() -> None:
    """Ponto de entrada registrado pelo executável `pg`."""
    app()


if __name__ == "__main__":
    main()
