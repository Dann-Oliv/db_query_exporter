# Author: Danilo Oliveira (https://github.com/Dann-Oliv)
# o intuito deste script é acessar databases diferentes mas com estruturas iguais
# e gerar de forma rápida planilhas com o resultado do SELECT inserido
# Compatível com MySql e PostgreSQL

import os
import yaml
import platform
import sqlalchemy
import urllib.parse
import pandas as pd

from sqlalchemy import text
from pathlib import Path
from datetime import date


def load_credentials(file_name, conn_name: str) -> dict:
    """
    Carrega as credenciais que serão usadas para acessar o banco de dados.

    Args:
        file_name (str): Nome do arquivo yaml com as credencias.
        conn_name (str): Nome da conexão no arquivo yaml, ex: "AWS","Banco_Teste"


    Returns:
        dict: Dicionário com as credencias de acesso ao banco de dados.
    """

    if not os.path.isfile(file_name):
        raise Exception("Arquivo de conexão não encontrado!")

    with open(file_name, "r") as conn_file:
        credentials = yaml.safe_load(conn_file)

    if conn_name not in credentials["databases"]:
        raise Exception("O nome da conexão inserida não foi encontrada!")

    return credentials["databases"][conn_name]


def load_query(query_file_name) -> str:
    """
    Carrega a query inserida no arquivo desejado.

    Args:
        query_file (str): Nome do arquivo com a query

    Returns:
    str: String com a query que foi escrita no arquivo selecionado.
    """

    query_file_path = Path(f"{os.getcwd()}/sql/{query_file_name}")

    if not os.path.isfile(query_file_path):
        raise Exception("Arquivo com a query não encontrado!")

    with open(query_file_path, "r") as query_file:
        query = query_file.read()

    if not query:
        raise Exception("Arquivo de query está vazio!")

    return query


def get_sqlalchemy_engine(
    credentials: dict, target_database=None
) -> sqlalchemy.engine.Engine:
    """
    Cria a string de conexão do sqlalchemy.

    Args:
        credentials (dict): Dicionário com o host, username, password, port, engine.

    Returns:
        str: String de conexão de acordo com o tipo de banco de dados.


    """
    host = credentials["host"]
    port = credentials["port"]
    database = credentials["database"]
    username = credentials["username"]
    password = credentials["password"]

    conn_string = ""

    match credentials["engine"]:
        case "postgres":
            conn_string = f"postgresql://{username}:{urllib.parse.quote(password)}@{host}:{port}/{target_database or database}"
            return sqlalchemy.create_engine(conn_string)

        case "mysql":
            conn_string = f"mysql+pymysql://{username}:{urllib.parse.quote(password)}@{host}:{port}/{target_database or database}"
            return sqlalchemy.create_engine(conn_string)

        case "sqlserver":
            conn_string = f"mssql+pyodbc://{username}:{urllib.parse.quote(password)}@{host}:{port}/{target_database or database}?driver=ODBC Driver 18 for SQL Server&TrustServerCertificate=yes"
            return sqlalchemy.create_engine(conn_string)

    return sqlalchemy.create_engine(conn_string)


def get_all_databases(engine: sqlalchemy.engine.Engine) -> list:
    query = """
    SELECT  (regexp_match("CTE_STRINGPGSQL",'Database=(.*);Pooling'))[1] AS nome_databases
    FROM "CONTROLE_EMPRESAS"
    WHERE "CTE_COD_SIS" IN (3,10) 
    AND "CTE_DT_LIMITE" > NOW() 
    AND "CTE_STRINGPGSQL" IS NOT NULL
    AND (regexp_match("CTE_STRINGPGSQL",'Database=(.*);Pooling'))[1] != 'teste'
    ORDER BY (regexp_match("CTE_STRINGPGSQL",'Database=(.*);Pooling'))[1]
    LIMIT 1
    """
    all_databases = []

    with engine.connect() as conn:
        results = conn.execute(text(query))

    for result in results:
        all_databases.append(result)

    return all_databases


def main():
    while True:
        # Limpa o terminal ao executar o script.
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

        target_database = input("Informe a database: ")

        query_file = input("Informe o nome do arquivo com a query: ")

        credentials = load_credentials("conn.yaml", target_database)

        query = load_query(query_file)

        engine = get_sqlalchemy_engine(credentials)

        all_databases = get_all_databases(engine)

        for database in all_databases:
            engine = get_sqlalchemy_engine(credentials, database)

            with engine.connect() as conn:
                results = pd.read_sql(query, conn)

                if results.empty:
                    print("Dataframe vazio")

        keep_execution = input("Deseja continuar? (y/n)")

        if keep_execution.lower() == "n":
            print("Encerrando...")
            break


if __name__ == "__main__":
    main()
