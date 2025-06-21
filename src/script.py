# Author: Danilo Oliveira (https://github.com/Dann-Oliv)
# o intuito deste script é acessar databases diferentes mas com estruturas iguais
# e gerar de forma rápida planilhas com o resultado do SELECT inserido
# Compatível com MySql e PostgreSQL

import os
import yaml
import logging
import platform
import sqlalchemy
import urllib.parse
import pandas as pd

from sqlalchemy import text
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


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
        logging.error("Arquivo de conexão não encontrado!")
        raise SystemExit()

    with open(file_name, "r") as conn_file:
        credentials = yaml.safe_load(conn_file)

    if conn_name not in credentials["databases"]:
        logging.error("O nome da conexão inserida não foi encontrada!")
        raise SystemExit()

    logging.info("Arquivo de conexão carregado!")
    return credentials["databases"][conn_name]


def load_query(query_file_name) -> str:
    """
    Carrega a query inserida no arquivo desejado.

    Args:
        query_file (str): Nome do arquivo com a query

    Returns:
    str: String com a query que foi escrita no arquivo selecionado.
    """

    query_file_path = Path(f"{os.getcwd()}/queries/{query_file_name}")

    if not os.path.isfile(query_file_path):
        logging.error("Arquivo com a query não encontrado!")
        raise SystemExit

    with open(query_file_path, "r") as query_file:
        query = query_file.read()

    if not query:
        logging.warning("Arquivo de query está vazio!")

    logging.info("Query carregada com sucesso!")
    return query


def get_sqlalchemy_engine(
    credentials: dict, target_database=None
) -> sqlalchemy.engine.Engine:
    """
    Cria a engine de conexão do sqlalchemy.

    Args:
        credentials (dict): Dicionário com o host, username, password, port, database, engine.

    Returns:
        str: Engine de conexão de acordo com o tipo de banco de dados.


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
            logging.info("Erro ao criar engine!")
            return sqlalchemy.create_engine(conn_string)

        case "mysql":
            conn_string = f"mysql+pymysql://{username}:{urllib.parse.quote(password)}@{host}:{port}/{target_database or database}"
            logging.info("Erro ao criar engine!")
            return sqlalchemy.create_engine(conn_string)

        case "sqlserver":
            conn_string = f"mssql+pyodbc://{username}:{urllib.parse.quote(password)}@{host}:{port}/{target_database or database}?driver=ODBC Driver 18 for SQL Server&TrustServerCertificate=yes"
            logging.info("Erro ao criar engine!")
            return sqlalchemy.create_engine(conn_string)

    logging.warning("Erro ao criar engine!")
    return sqlalchemy.create_engine(conn_string)


def get_all_databases(engine: sqlalchemy.engine.Engine) -> list:
    # Query para pegar todos os bancos de produçãio ativos no integrador.
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
        logging.info(f"Conexão feita com sucesso em: {engine}")

    for result in results:
        all_databases.append(result)

    logging.info("Databases coletadas com sucesso!")
    return all_databases


def export_to_excel(dataframe: pd.DataFrame, sheet_name: str):
    sheet_folder = Path(f"{os.getcwd()}/out")
    full_path = f"{sheet_folder}/{sheet_name}_{datetime.now()}.xlsx"

    if not os.path.isdir(sheet_folder):
        os.mkdir(sheet_folder)
        logging.warning("Caminho para salvar planilhas não existe!")
        logging.info(f"Criando pasta para salvar planilhas: {sheet_folder}")

    dataframe.to_excel(
        excel_writer=full_path,
        sheet_name="Results",
        index=False,
    )
    logging.info(f"Planilha salva com sucesso em: {full_path}")


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
                    print(f"Nenhum resultado encontrado em: {database}")
                    continue

                export_to_excel(dataframe=results, sheet_name=database)

        keep_execution = input("Deseja continuar? (y/n)")

        if keep_execution.lower() == "n":
            print("Encerrando...")
            break


if __name__ == "__main__":
    main()
