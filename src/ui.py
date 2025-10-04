# Author: Danilo Oliveira (https://github.com/Dann-Oliv)
# User interface module

import os
import platform


def clear_terminal() -> None:
    """Limpa o terminal de acordo com o sistema operacional."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def get_user_input() -> tuple[str, str, bool]:
    """
    Obtém inputs do usuário.

    Returns:
        tuple: (conn_name, query_file, unify_results)
    """
    conn_name = input("Informe o nome da conexão no YAML: ").strip()
    query_file = input("Informe o nome do arquivo com a query: ").strip()
    unify_results = (
        input("Deseja salvar os resultados em um único arquivo? (y/n): ")
        .strip()
        .lower()
    )

    return conn_name, query_file, unify_results == "y"


def ask_restart() -> bool:
    """
    Pergunta ao usuário se deseja reiniciar.

    Returns:
        bool: True se deseja reiniciar, False caso contrário
    """
    keep_execution = input("Script encerrado. Deseja reiniciar? (y/n): ").strip().lower()
    return keep_execution != "n"
