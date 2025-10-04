# Author: Danilo Oliveira (https://github.com/Dann-Oliv)
# Query processor module with threading support

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List

import pandas as pd

from .database import create_engine, query_database
from .exporter import export_to_excel


def process_single_database(
    credentials: Dict, database: str, query: str
) -> tuple[str, pd.DataFrame]:
    """
    Processa uma única database (thread-safe).

    Args:
        credentials (dict): Credenciais de conexão
        database (str): Nome do banco de dados
        query (str): Query SQL a executar

    Returns:
        tuple: (database_name, dataframe)
    """
    try:
        engine = create_engine(credentials, database)
        results = query_database(engine, query)

        if not results.empty:
            results["database"] = database
            return database, results
        else:
            logging.info(f"Nenhum resultado encontrado em: {database}")
            return database, pd.DataFrame()

    except Exception as e:
        logging.error(f"Erro ao consultar dados da database {database}: {e}")
        return database, pd.DataFrame()


def process_databases_unified(
    credentials: Dict, databases: List[str], query: str, max_workers: int = 5
) -> None:
    """
    Processa múltiplas databases em paralelo e unifica os resultados.

    Args:
        credentials (dict): Credenciais de conexão
        databases (list): Lista de bancos de dados
        query (str): Query SQL a executar
        max_workers (int): Número máximo de threads paralelas
    """
    dataframes = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submete todas as tarefas
        future_to_db = {
            executor.submit(process_single_database, credentials, db, query): db
            for db in databases
        }

        # Processa os resultados conforme são completados
        for future in as_completed(future_to_db):
            db_name = future_to_db[future]
            try:
                database, df = future.result()
                if not df.empty:
                    dataframes.append(df)
                    logging.info(f"Database {database} processada com sucesso!")
            except Exception as e:
                logging.error(f"Erro ao processar database {db_name}: {e}")

    if dataframes:
        final_df = pd.concat(dataframes, ignore_index=True)
        export_to_excel(dataframe=final_df, sheet_name="Resultados_Agrupados")
    else:
        print("Nenhum resultado encontrado em nenhuma database.")


def process_databases_separate(
    credentials: Dict, databases: List[str], query: str, max_workers: int = 5
) -> None:
    """
    Processa múltiplas databases em paralelo e salva resultados separadamente.

    Args:
        credentials (dict): Credenciais de conexão
        databases (list): Lista de bancos de dados
        query (str): Query SQL a executar
        max_workers (int): Número máximo de threads paralelas
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submete todas as tarefas
        future_to_db = {
            executor.submit(process_single_database, credentials, db, query): db
            for db in databases
        }

        # Processa os resultados conforme são completados
        for future in as_completed(future_to_db):
            db_name = future_to_db[future]
            try:
                database, df = future.result()
                if not df.empty:
                    export_to_excel(dataframe=df, sheet_name=database)
                    logging.info(f"Database {database} exportada com sucesso!")
                else:
                    print(f"Nenhum resultado encontrado em: {database}")
            except Exception as e:
                logging.error(
                    f"Erro ao consultar ou exportar dados da database {db_name}: {e}"
                )
