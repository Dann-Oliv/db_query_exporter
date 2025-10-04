# Author: Danilo Oliveira (https://github.com/Dann-Oliv)
# Database operations module

import logging
import urllib.parse
from typing import Dict, List, Optional

import pandas as pd
import sqlalchemy
from sqlalchemy import text


def create_engine(
    credentials: Dict, target_database: Optional[str] = None
) -> sqlalchemy.engine.Engine:
    """
    Cria a engine de conexão do sqlalchemy.

    Args:
        credentials (dict): Dicionário com o host, username, password, port, database, engine.
        target_database (str, optional): Nome do banco de dados alvo. Se não fornecido, usa o banco de dados padrão das credenciais.

    Returns:
        sqlalchemy.engine.Engine: Engine de conexão de acordo com o tipo de banco de dados.
    """
    host = credentials["host"]
    port = credentials["port"]
    database = credentials["database"]
    username = credentials["username"]
    password = credentials["password"]

    db_name = target_database or database

    match credentials["engine"]:
        case "postgres":
            conn_string = f"postgresql://{username}:{urllib.parse.quote(password)}@{host}:{port}/{db_name}"
            logging.info(f"Criando engine Postgres para: {db_name}")
            return sqlalchemy.create_engine(conn_string)

        case "mysql":
            conn_string = f"mysql+pymysql://{username}:{urllib.parse.quote(password)}@{host}:{port}/{db_name}"
            logging.info(f"Criando engine MySQL para: {db_name}")
            return sqlalchemy.create_engine(conn_string)

    raise SystemExit(f"Tipo de engine não reconhecido: {credentials['engine']}")


def get_all_databases(engine: sqlalchemy.engine.Engine) -> List[str]:
    """
    Obtém lista de todos os bancos de dados disponíveis.

    Args:
        engine (sqlalchemy.engine.Engine): Engine de conexão

    Returns:
        list: Lista com nomes das databases
    """
    # Insira a query para pegar o nome das databases com as suas condições.
    query = """
    SELECT datname 
    FROM pg_database
    """
    all_databases = []

    try:
        with engine.connect() as conn:
            results = conn.execute(text(query))
            logging.info(f"Conexão feita com sucesso em: {engine}")

            for result in results:
                all_databases.append(result[0])

        logging.info("Databases coletadas com sucesso!")

    except Exception as e:
        logging.error(f"Erro ao coletar databases: {e}")

    return all_databases


def query_database(engine: sqlalchemy.engine.Engine, query: str) -> pd.DataFrame:
    """
    Executa query no banco de dados e retorna os resultados.

    Args:
        engine (sqlalchemy.engine.Engine): Engine de conexão
        query (str): Query SQL a ser executada

    Returns:
        pd.DataFrame: DataFrame com os resultados da query
    """
    try:
        with engine.connect() as conn:
            results = pd.read_sql(query, conn)

            if results.empty:
                logging.warning("Nenhum resultado encontrado para a query.")
                return pd.DataFrame()

            return results

    except Exception as e:
        logging.error(f"Erro ao consultar dados: {e}")
        return pd.DataFrame()
