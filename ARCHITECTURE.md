# Documentação Técnica - Arquitetura Modular

## Visão Geral

Este documento descreve a arquitetura modular do Query Results Exporter e como os diferentes módulos interagem entre si.

## Módulos

### src/config.py
**Responsabilidade**: Gerenciamento de configuração e carregamento de dados externos.

**Funções principais**:
- `load_credentials(file_name, conn_name)`: Carrega credenciais do arquivo YAML
- `load_query(query_file_name)`: Carrega a query SQL de um arquivo

**Dependências**: `yaml`, `os`, `pathlib`, `logging`

### src/database.py
**Responsabilidade**: Operações relacionadas a banco de dados.

**Funções principais**:
- `create_engine(credentials, target_database)`: Cria engine SQLAlchemy para conexão
- `get_all_databases(engine)`: Obtém lista de databases disponíveis
- `query_database(engine, query)`: Executa query e retorna resultados como DataFrame

**Dependências**: `sqlalchemy`, `pandas`, `urllib.parse`, `logging`

### src/exporter.py
**Responsabilidade**: Exportação de dados para formato Excel.

**Funções principais**:
- `export_to_excel(dataframe, sheet_name)`: Exporta DataFrame para arquivo Excel

**Dependências**: `pandas`, `datetime`, `pathlib`, `os`, `logging`

### src/ui.py
**Responsabilidade**: Interface com o usuário (CLI).

**Funções principais**:
- `clear_terminal()`: Limpa o terminal
- `get_user_input()`: Coleta informações do usuário
- `ask_restart()`: Pergunta se o usuário deseja reiniciar

**Dependências**: `os`, `platform`

### src/query_processor.py
**Responsabilidade**: Processamento paralelo de múltiplas databases.

**Funções principais**:
- `process_single_database(credentials, database, query)`: Processa uma única database (thread-safe)
- `process_databases_unified(credentials, databases, query, max_workers)`: Processa múltiplas databases em paralelo e unifica resultados
- `process_databases_separate(credentials, databases, query, max_workers)`: Processa múltiplas databases em paralelo e salva separadamente

**Dependências**: `concurrent.futures`, `pandas`, `logging`, outros módulos locais

**Características**:
- Usa `ThreadPoolExecutor` para processamento paralelo
- Configurável com `max_workers` (padrão: 5 threads)
- Thread-safe para operações concorrentes

## Fluxo de Execução

```
main.py
  │
  ├─> ui.clear_terminal()
  ├─> ui.get_user_input()
  │
  ├─> config.load_credentials()
  ├─> config.load_query()
  │
  ├─> database.create_engine()
  ├─> database.get_all_databases()
  │
  └─> query_processor.process_databases_*()
       │
       ├─> [Thread 1] process_single_database()
       │    ├─> database.create_engine()
       │    ├─> database.query_database()
       │    └─> exporter.export_to_excel() (modo separado)
       │
       ├─> [Thread 2] process_single_database()
       ├─> [Thread 3] process_single_database()
       │    ...
       │
       └─> exporter.export_to_excel() (modo unificado)
```

## Benefícios da Arquitetura Modular

1. **Separação de Responsabilidades**: Cada módulo tem uma função específica e bem definida
2. **Facilidade de Manutenção**: Mudanças em um módulo não afetam os outros
3. **Testabilidade**: Cada módulo pode ser testado independentemente
4. **Reutilização**: Módulos podem ser reutilizados em outros projetos
5. **Clareza**: O código é mais fácil de entender e documentar
6. **Performance**: Threading melhora significativamente o desempenho ao processar múltiplas databases

## Threading e Concorrência

O módulo `query_processor.py` implementa processamento paralelo usando `ThreadPoolExecutor`:

- **Vantagens**:
  - Múltiplas databases são processadas simultaneamente
  - Redução significativa no tempo total de execução
  - Melhor utilização de recursos do sistema

- **Configuração**:
  - Por padrão, usa 5 threads paralelas
  - Pode ser ajustado modificando o parâmetro `max_workers`

- **Thread Safety**:
  - Cada thread tem sua própria engine de conexão
  - DataFrames são construídos independentemente
  - Logging é thread-safe por padrão no Python

## Type Hints

O código utiliza type hints para melhorar a documentação e suporte de IDEs:

```python
def load_credentials(file_name: str, conn_name: str) -> Dict:
    ...

def query_database(engine: sqlalchemy.engine.Engine, query: str) -> pd.DataFrame:
    ...
```

## Tratamento de Erros

Cada módulo implementa tratamento de erros apropriado:
- Erros críticos resultam em `SystemExit`
- Erros não-críticos são logados e a execução continua
- Exceções em threads são capturadas e logadas sem interromper outras threads
