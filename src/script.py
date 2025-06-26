# Author: Danilo Oliveira (https://github.com/Dann-Oliv)
# o intuito deste script é acessar databases diferentes mas com estruturas iguais
# e gerar de forma rápida planilhas com o resultado do SELECT inserido
# Compatível com MySql e PostgreSQL

import logging
import os
import platform
import urllib.parse
from datetime import datetime
from pathlib import Path

import pandas as pd
import sqlalchemy
import yaml
from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log.txt", mode="w"),
        logging.StreamHandler(),
    ],
)


def load_credentials(file_name, conn_name: str) -> dict:
    """
    Carrega as credenciais que serão usadas para acessar o banco de dados.

    Args:
        file_name (str): Nome do arquivo yaml com as credencias.
        conn_name (str): Nome da conexão no arquivo yaml, ex: "AWS","Banco_Teste"


    Returns:
        dict: Dicionário com as credenciais de acesso ao banco de dados.
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

    query_file_path = Path(f"{os.getcwd()}/sql/{query_file_name}")

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
        target_database (str, optional): Nome do banco de dados alvo. Se não fornecido, usa o banco de dados padrão das credenciais.

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
            logging.info(
                f"Criando engine Postgres para : {target_database or database}"
            )
            return sqlalchemy.create_engine(conn_string)

        case "mysql":
            conn_string = f"mysql+pymysql://{username}:{urllib.parse.quote(password)}@{host}:{port}/{target_database or database}"
            logging.info(f"Criando engine MySQL para: {target_database or database}")
            return sqlalchemy.create_engine(conn_string)

        # case "sqlserver":
        #     conn_string = f"mssql+pyodbc://{username}:{urllib.parse.quote(password)}@{host}:{port}/{target_database or database}?driver=ODBC Driver 18 for SQL Server&TrustServerCertificate=yes"
        #     logging.info(f"Criando engine para SQL Server: {conn_string}")
        #     return sqlalchemy.create_engine(conn_string)

    logging.error("Tipo de engine não reconhecido!")
    raise SystemExit("Tipo de engine não reconhecido: {}".format(credentials["engine"]))


def get_all_databases(engine: sqlalchemy.engine.Engine) -> list:
    # Query para pegar todos os bancos de produção ativos no integrador.
    query = """
    SELECT  (regexp_match("CTE_STRINGPGSQL",'Database=(.*);Pooling'))[1] AS nome_databases
    FROM "CONTROLE_EMPRESAS"
    WHERE "CTE_COD_SIS" IN (3,10) 
    AND "CTE_DT_LIMITE" > NOW() 
    AND "CTE_STRINGPGSQL" IS NOT NULL
    AND (regexp_match("CTE_STRINGPGSQL",'Database=(.*);Pooling'))[1] != 'teste'
    ORDER BY (regexp_match("CTE_STRINGPGSQL",'Database=(.*);Pooling'))[1]
    -- LIMIT 1
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


def export_to_excel(dataframe: pd.DataFrame, sheet_name: str):
    sheet_folder = Path(f"{os.getcwd()}/out")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_path = Path(f"{sheet_folder}/{sheet_name}_{timestamp}.xlsx")

    os.makedirs(sheet_folder, exist_ok=True)

    dataframe.to_excel(
        excel_writer=full_path,
        sheet_name="Results",
        index=False,
    )
    logging.info(f"Planilha salva com sucesso em: {full_path}")


def get_data_from_db(engine: sqlalchemy.engine.Engine, query: str) -> pd.DataFrame:
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


def main():
    while True:
        # Limpa o terminal ao executar o script.
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

        conn_name = input("Informe o nome da conexão no YAML: ").strip()
        query_file = input("Informe o nome do arquivo com a query: ").strip()
        unify_results = (
            input("Deseja salvar os resultados em um único arquivo? (y/n): ")
            .strip()
            .lower()
        )

        credentials = load_credentials("conn.yaml", conn_name)
        query = load_query(query_file)

        engine = get_sqlalchemy_engine(credentials)
        all_databases = get_all_databases(engine)

        if unify_results == "y":
            dataframes = []

            for database in all_databases:
                engine = get_sqlalchemy_engine(credentials, database)

                try:
                    results = get_data_from_db(engine, query)

                    if not results.empty:
                        results["database"] = database
                        dataframes.append(results)

                except Exception as e:
                    logging.error(
                        f"Erro ao consultar dados da database {database}: {e}"
                    )
                    continue

            if dataframes:
                final_df = pd.concat(dataframes, ignore_index=True)
                export_to_excel(dataframe=final_df, sheet_name="Resultados_Agrupados")

            else:
                print("Nenhum resultado encontrado em nenhuma database.")
        else:
            for database in all_databases:
                engine = get_sqlalchemy_engine(credentials, database)

                try:
                    results = get_data_from_db(engine, query)

                    if not results.empty:
                        export_to_excel(dataframe=results, sheet_name=database)

                    else:
                        print(f"Nenhum resultado encontrado em: {database}")

                except Exception as e:
                    logging.error(
                        f"Erro ao consultar ou exportar dados da database {database}: {e}"
                    )
                    continue

        keep_execution = input("Script encerrado. Deseja reiniciar? (y/n)")
        if keep_execution.lower() == "n":
            print("Encerrando...")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExecução interrompida. Encerrando...")
