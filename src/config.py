# Author: Danilo Oliveira (https://github.com/Dann-Oliv)
# Configuration and credentials loading module

import logging
import os
from pathlib import Path
from typing import Dict

import yaml


def load_credentials(file_name: str, conn_name: str) -> Dict:
    """
    Carrega as credenciais que serão usadas para acessar o banco de dados.

    Args:
        file_name (str): Nome do arquivo yaml com as credenciais.
        conn_name (str): Nome da conexão no arquivo yaml, ex: "Localhost","Banco_Teste"

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


def load_query(query_file_name: str) -> str:
    """
    Carrega a query inserida no arquivo desejado.

    Args:
        query_file_name (str): Nome do arquivo com a query

    Returns:
        str: String com a query que foi escrita no arquivo selecionado.
    """
    query_file_path = Path(f"{os.getcwd()}/sql/{query_file_name}")

    if not os.path.isfile(query_file_path):
        logging.warning("Arquivo com a query não encontrado!")
        raise SystemExit

    with open(query_file_path, "r") as query_file:
        query = query_file.read()

    if not query:
        logging.warning("Arquivo de query está vazio!")

    logging.info("Query carregada com sucesso!")
    return query
