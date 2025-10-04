# Author: Danilo Oliveira (https://github.com/Dann-Oliv)
# Compatível com MySql e PostgreSQL
# Refatorado com estrutura modular e processamento paralelo com threads

import logging

from src.config import load_credentials, load_query
from src.database import create_engine, get_all_databases
from src.query_processor import process_databases_separate, process_databases_unified
from src.ui import ask_restart, clear_terminal, get_user_input

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log.txt", mode="w"),
        logging.StreamHandler(),
    ],
)


def main():
    """Função principal do aplicativo."""
    while True:
        clear_terminal()

        # Obtém inputs do usuário
        conn_name, query_file, unify_results = get_user_input()

        # Carrega credenciais e query
        credentials = load_credentials("conn_profiles.yaml", conn_name)
        query = load_query(query_file)

        # Obtém lista de databases
        engine = create_engine(credentials)
        all_databases = get_all_databases(engine)

        # Processa databases com threading
        if unify_results:
            process_databases_unified(credentials, all_databases, query)
        else:
            process_databases_separate(credentials, all_databases, query)

        # Pergunta se deseja reiniciar
        if not ask_restart():
            print("Encerrando...")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExecução interrompida. Encerrando...")
