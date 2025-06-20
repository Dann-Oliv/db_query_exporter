# Author: Danilo Oliveira (https://github.com/Dann-Oliv)
# o intuito deste script é acessar databases diferentes mas com estruturas iguais
# e gerar de forma rápida planilhas com o resultado do SELECT inserido
# Compatível com MySql e PostgreSQL

import os
import yaml
import platform
import urllib.parse
import pandas as pd

from pathlib import Path
from datetime import date
from sqlalchemy import text
from sqlalchemy import create_engine


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


def get_sqlalchemy_conn_string(credentials: dict, target_database: str) -> str:
    """
    Cria a string de conexão do sqlalchemy.

    Args:
        credentials (dict): Dicionário com o host, username, password, port, engine.
        target_database (str): Nome da database em especifo para incluir na string de conexão.

    Returns:
        str: String de conexão de acordo com o tipo de banco de dados.


    """
    host = credentials["host"]
    port = credentials["port"]
    username = credentials["username"]
    password = credentials["password"]

    match credentials["engine"]:
        case "postgres":
            conn_string = f"postgresql://{username}:{urllib.parse.quote(password)}@{host}:{port}/{target_database}"
            return conn_string

        case "mysql":
            conn_string = f"mysql+pymysql://{username}:{urllib.parse.quote(password)}@{host}:{port}/{target_database}"
            return conn_string

        case "sqlserver":
            conn_string = f"mssql+pyodbc://{username}:{urllib.parse.quote(password)}@{host}:{port}/{target_database}?driver=ODBC Driver 18 for SQL Server&TrustServerCertificate=yes"
            return conn_string

    return "A engine inserida não é válida"


def main():
    while True:
        # Limpa o terminal ao executar o script.
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

        target_database = input("Insira o nome da database: ")

        credentials = load_credentials("conn.yaml", target_database)

        query_file = input("Insira o nome do arquivo com a query a ser executada: ")

        query = load_query(query_file)

        keep_execution = input("Deseja continuar? (y/n)")

        if keep_execution.lower() == "n":
            print("Encerrando...")
            break


if __name__ == "__main__":
    main()
