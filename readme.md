# Query Results To Excel

Este projeto tem como objetivo acessar múltiplos bancos de dados (Dentro de uma instância PostgreSQL ou MySQL) com estruturas iguais, executar uma consulta SQL e exportar os resultados para arquivos Excel (.xlsx). É possível agrupar os resultados de todas as bases em um único arquivo ou gerar um arquivo para cada base.

## Funcionalidades
- **Arquitetura Modular**: Código organizado em módulos seguindo práticas de código limpo
- **Processamento Paralelo**: Usa threads para consultar múltiplas databases simultaneamente, melhorando significativamente a performance
- **Conexão Dinâmica**: Suporte a diferentes bancos de dados usando SQLAlchemy
- **Suporte a PostgreSQL e MySQL**
- **Exportação para Excel**: Resultados exportados em formato .xlsx
- **Sistema de Logging**: Logs detalhados salvos em arquivo e exibidos no terminal

## Estrutura do Projeto
```
├── conn_profiles.yaml                # Arquivo de credenciais
├── conn_profiles.example.yaml        # Exemplo de configuração de credenciais
├── requirements.txt                  # Dependências do projeto
├── main.py                           # Script principal (refatorado)
├── src/                              # Módulos do projeto
│   ├── __init__.py                   # Inicialização do pacote
│   ├── config.py                     # Carregamento de credenciais e queries
│   ├── database.py                   # Operações de banco de dados
│   ├── exporter.py                   # Exportação para Excel
│   ├── query_processor.py            # Processamento paralelo com threads
│   └── ui.py                         # Interface com usuário
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
Altere a query no arquivo `src/database.py` na função `get_all_databases()` para pegar os nomes das databases de acordo com as suas condições.

#### Pega todos os nomes de databases em uma instância do postgres.
Ex: "SELECT datname FROM pg_database" 

### 5. Execute o script
```bash
python main.py
```

O script irá solicitar:
- Nome da conexão (conforme definido no `conn_profiles.yaml`)
- Nome do arquivo com a query (ex: `minha_query.sql`)
- Se deseja agrupar os resultados em um único arquivo Excel

Os arquivos gerados serão salvos na pasta `out/`.

**Nota**: O processamento é feito em paralelo usando threads, o que significa que múltiplas databases serão consultadas simultaneamente, tornando a execução muito mais rápida quando há muitos bancos de dados.

### 6. Logs
Toda execução gera um log  em `log.txt` e também exibe as mensagens no terminal.

## Melhorias Implementadas

### Arquitetura Modular
O código foi refatorado em módulos distintos, cada um com uma responsabilidade específica:
- **config.py**: Gerencia o carregamento de credenciais e queries
- **database.py**: Encapsula todas as operações de banco de dados
- **exporter.py**: Responsável pela exportação para Excel
- **query_processor.py**: Implementa o processamento paralelo com threads
- **ui.py**: Gerencia a interface com o usuário

### Processamento Paralelo
O sistema agora utiliza `ThreadPoolExecutor` do módulo `concurrent.futures` para processar múltiplas databases simultaneamente. Isso resulta em:
- **Melhor Performance**: Queries executadas em paralelo em vez de sequencialmente
- **Uso Eficiente de Recursos**: Até 5 threads paralelas por padrão (configurável)
- **Melhor Experiência**: Redução significativa no tempo de execução para múltiplas databases

### Código Limpo
- Funções com responsabilidades únicas e bem definidas
- Type hints para melhor documentação e IDE support
- Melhor separação de concerns
- Código mais testável e manutenível

## Exemplo de uso
```
Informe o nome da conexão no YAML: localhost
Informe o nome do arquivo com a query: minha_query.sql
Deseja consolidar os resultados em um único arquivo? (y/n): y
```

---
