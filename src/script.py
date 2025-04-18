# Copyright (C) 2025 by Danilo Oliveira
# o intuito deste script é acessar databases diferentes mas com estruturas iguais
# e gerar de forma rápida planilhas com o resultado do SELECT inserido
# Compatível com MySql e PostgreSQL

# Módulos importados em ordem alfabética (por quê tenho TOC)
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy import text
import json
import os
import pandas as pd
import platform
from urllib.parse import quote_plus

# 1. Identifica qual é o sistema operacional usado:
actual_os = platform.system()
print(f"Sistema operacional: {actual_os}\n")

# 2. Identifica o diretório atual no qual o programa está sendo executado:
actual_dir = os.getcwd()
print(F"Diretório atual: {actual_dir}\n")

# 3. Define o caminho onde as planilhas serão salvas de acordo com o sistema operacional:
pathExcel = os.path.join(actual_dir, 'results')

# 3.1 Verifica se a pasta existe, caso não, cria a pasta.
if not os.path.exists(pathExcel):
    print("Criando pasta para armazenar as planilhas...\n")
    os.makedirs(pathExcel)
    
# 4. Tenta abrir o JSON com os dados do banco de dados:
try:
    with open('conn.json','r') as json_file:
        json_data = json.load(json_file)
        print("Arquivo JSON carregado !\n")

except FileNotFoundError:    # Captura o erro de não encontrar o arquivo
    raise SystemExit("Erro: Arquivo JSON não encontrado.")

except json.JSONDecodeError: # Captura o erro de JSON inválido
    raise SystemExit("Erro: Arquivo JSON inválido.")

except PermissionError:      # Captura o erro de Permissão 
    raise SystemExit("Erro: Permissão de acesso negada para o arquivo JSON.")

except Exception as e:       # Captura qualquer erro inesperado
    raise SystemExit(f"Erro inesperado: {e}")

# 5. Tenta abrir o arquivo com a query a ser executada no banco de dados:
try:
    with open('sql/query.sql', 'r') as query_file:
        query = query_file.read()
        print("Arquivo SQL carregado !\n")

except FileNotFoundError:    # Captura o erro de não encontrar o arquivo
    raise SystemExit("Erro: Arquivo não encontrado.")

except PermissionError:      # Captura o erro de Permissão 
    raise SystemExit("Erro: Permissão de acesso negada para o arquivo.")

except Exception as e:       # Captura qualquer erro inesperado
    raise SystemExit(f"Erro inesperado: {e}")

# 6. Criando a string de conexão com o SqlAlchemy de acordo com o tipo de banco escolhido (mysql - postgres):
db_type = json_data['db_type'].lower() # Pega o tipo de banco de dados informado no JSON

if (db_type == 'postgres'):
    # Padrão da engine: postgresql+psycopg2://username:password@host:port/database
    driver = "postgresql+psycopg2"

    engine = create_engine(f"{driver}://{json_data['user']}:{json_data['password']}@{json_data['host']}:{json_data['port']}/{json_data['database']}")

elif (db_type == 'mysql'):
    # Padrão da engine: mysql+mysqldb://username:password@host:port/database
    driver = "mysql+mysqldb"

    engine = create_engine(f"{driver}://{json_data['user']}:{json_data['password']}@{json_data['host']}:{json_data['port']}/{json_data['database']}")

else:
    raise SystemExit("Erro: O tipo de banco de dados escolhido não é suportado.")

# 7. Função para verificar se o banco de dados é válido:
def verify_conn():
    try:
        with engine.connect() as connection:
            print(f"Conexão com banco de dados bem-sucedida !\n")
            return True
    
    except Exception as e:
        raise SystemExit(f"Erro: {e}")    

# 8. Se os dados de conexão forem válidos, acessa o banco de dados e executa a query.
if verify_conn() == True:
    # Executa as instruções para cada uma das databases
    for database in json_data["databases"]:

        print(f"Executando script na database: {database}\n")

        # Monta a engine separada para cada uma das databases
        engine = create_engine(f"{driver}://{json_data['user']}:{quote_plus(json_data['password'])}@{json_data['host']}:{json_data['port']}/{database}")

        # Executa a query no banco de dados e gera um dataframe
        try:
            # Executa a query
            query_result = pd.read_sql(text(query),engine)

            # Gera o dataframe do resultado
            df = pd.DataFrame(query_result)

            # Coloca o resultado em uma planilha
            df.to_excel(os.path.join(pathExcel,f"{database}_{date.today()}.xlsx"),index=False)
        
            print(f"Planilha com os resultados gerada com sucesso !\n")


        except Exception as e:
            print(f"Ocorreu um erro na database {database}: {e} ")
            continue
        
