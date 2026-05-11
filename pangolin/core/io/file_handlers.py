import os
import json
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

from ..observability.logger import setup_logger


def load_data_files(data_dir: str) -> List[pd.DataFrame]:
    """
    Carrega arquivos de dados do diretório especificado.

    Suporta CSV, JSON, XLSX e XLS. Valida a presença das colunas obrigatórias
    'id' e 'target' em cada arquivo carregado.

    Args:
        data_dir: Diretório contendo os arquivos de dados

    Returns:
        Lista de DataFrames carregados

    Raises:
        FileNotFoundError: Se o diretório não existir
        ValueError: Se as colunas obrigatórias não forem encontradas
    """
    logger = setup_logger("FileHandler")
    logger.info(f"Carregando arquivos de dados de: {data_dir}")

    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Diretório não encontrado: {data_dir}")

    dataframes = []
    supported_extensions = {'.csv', '.json', '.xlsx', '.xls'}

    for file_path in Path(data_dir).rglob("*"):
        if not (file_path.is_file() and file_path.suffix.lower() in supported_extensions):
            continue

        try:
            logger.info(f"Processando arquivo: {file_path}")

            suffix = file_path.suffix.lower()
            if suffix == '.csv':
                df = pd.read_csv(file_path)
            elif suffix == '.json':
                df = pd.read_json(file_path)
            else:
                df = pd.read_excel(file_path)

            if df.empty:
                logger.warning(f"Arquivo vazio ignorado: {file_path}")
                continue

            required_columns = ['id', 'target']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                available_columns = sorted(df.columns.tolist())
                logger.error(f"Arquivo {file_path.name}: colunas obrigatórias ausentes: {missing_columns}")
                raise ValueError(
                    f"Arquivo '{file_path.name}' deve conter as colunas obrigatórias: {required_columns}. "
                    f"Colunas faltando: {missing_columns}. "
                    f"Colunas disponíveis: {available_columns}"
                )

            logger.info(f"Arquivo carregado: {len(df)} linhas, {len(df.columns)} colunas")
            dataframes.append(df)

        except Exception as e:
            logger.error(f"Erro ao carregar arquivo {file_path}: {e}")
            raise

    if not dataframes:
        raise ValueError(f"Nenhum arquivo válido encontrado em: {data_dir}")

    logger.info(f"Total de arquivos carregados: {len(dataframes)}")
    return dataframes


def save_results(results: List[Dict[str, Any]], output_path: str,
                 format: str = 'csv', **kwargs) -> None:
    """
    Salva resultados em arquivo no formato especificado.

    Args:
        results: Lista de dicionários com os resultados
        output_path: Caminho do arquivo de saída (sem extensão)
        format: Formato de saída ('csv', 'json', 'xlsx')
    """
    logger = setup_logger("FileHandler")

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    if not results:
        logger.warning("Nenhum resultado para salvar.")
        return

    full_path = f"{output_path}.{format}"

    try:
        if format.lower() == 'csv':
            save_csv(results, full_path, **kwargs)
        elif format.lower() == 'json':
            save_json(results, full_path, **kwargs)
        elif format.lower() == 'xlsx':
            save_xlsx(results, full_path, **kwargs)
        else:
            raise ValueError(f"Formato não suportado: {format}")

        logger.info(f"Resultados salvos: {full_path} ({len(results)} registros)")

    except Exception as e:
        logger.error(f"Erro ao salvar resultados: {e}")
        raise


def save_csv(results: List[Dict[str, Any]], file_path: str, **kwargs) -> None:
    """Salva resultados em formato CSV."""
    pd.DataFrame(results).to_csv(file_path, index=False, encoding='utf-8', **kwargs)


def save_json(results: List[Dict[str, Any]], file_path: str, **kwargs) -> None:
    """Salva resultados em formato JSON."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, **kwargs)


def save_xlsx(results: List[Dict[str, Any]], file_path: str, **kwargs) -> None:
    """Salva resultados em formato XLSX."""
    pd.DataFrame(results).to_excel(file_path, index=False, engine='openpyxl', **kwargs)


def validate_columns(dataframes: List[pd.DataFrame], required_columns: List[str]) -> bool:
    """
    Verifica se todas as colunas obrigatórias estão presentes no conjunto de DataFrames.

    Returns:
        True se todas as colunas existem em pelo menos um DataFrame
    """
    logger = setup_logger("FileHandler")

    all_columns = set()
    for df in dataframes:
        all_columns.update(df.columns)

    missing = set(required_columns) - all_columns

    if missing:
        logger.error(f"Colunas obrigatórias não encontradas: {missing}")
        logger.info(f"Colunas disponíveis: {sorted(all_columns)}")
        return False

    logger.info(f"Colunas obrigatórias validadas: {required_columns}")
    return True


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Retorna metadados de um arquivo."""
    if not os.path.exists(file_path):
        return {"exists": False}

    stat = os.stat(file_path)
    return {
        "exists": True,
        "size_bytes": stat.st_size,
        "size_mb": stat.st_size / (1024 * 1024),
        "modified": stat.st_mtime,
        "extension": Path(file_path).suffix.lower(),
    }
