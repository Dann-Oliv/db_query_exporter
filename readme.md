# Query Results To Excel

Este projeto tem como objetivo acessar múltiplos bancos de dados (Dentro de uma instância PostgreSQL ou MySQL) com estruturas iguais, executar uma consulta SQL e exportar os resultados para arquivos Excel (.xlsx). É possível agrupar os resultados de todas as bases em um único arquivo ou gerar um arquivo para cada base.

## Funcionalidades
- Conexão dinâmica com diferentes bancos de dados usando SQLAlchemy.
- Suporte a PostgreSQL e MySQL.
- Exportação dos resultados para Excel.
- Log salvo em arquivo.

## Estrutura do Projeto
```
├── conn_profiles.yaml                # Arquivo de credenciais
├── conn_profiles.example.yaml        # Exemplo de configuração de credenciais
├── requirements.txt                  # Dependências do projeto
├── main.py                           # Script principal
├── sql/
│   └── exemplo.sql                   # Exemplo de query SQL
└── out/                              # (Gerado) Planilhas exportadas
```

## Como usar

### 1. Instale as dependências
Windows
```
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
```
Unix
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
### 2. Configure as credenciais
Crie um arquivo `conn_profiles.yaml` baseado no exemplo `conn_profiles.example.yaml`:
```yaml
databases:
  nome_conexao:
    engine: "postgres"  # ou "mysql"
    host: "hosto"
    port: 5432
    username: "usuario"
    password: "senha"
    database: "nome_database"
```

### 3. Crie sua query
Salve sua consulta SQL na pasta `sql/` (ex: `minha_query.sql`).


### 4. Edite a query da função get_all_databases()
Altere a query para pegar os nomes das databases de acordo com as suas condições.

#### Pega todos os nomes de databases em uma instância do postgres.
Ex: "SELECT datname FROM pg_database" 

### 4. Execute o script
```bash
python main.py
```

O script irá solicitar:
- Nome da conexão (conforme definido no `conn_profiles.yaml`)
- Nome do arquivo com a query (ex: `minha_query.sql`)
- Se deseja agrupar os resultados em um único arquivo Excel

Os arquivos gerados serão salvos na pasta `out/`.

### 5. Logs
Toda execução gera um log  em `log.txt` e também exibe as mensagens no terminal.

## Exemplo de uso
```
Informe o nome da conexão no YAML: localhost
Informe o nome do arquivo com a query: minha_query.sql
Deseja consolidar os resultados em um único arquivo? (y/n): y
```

---
