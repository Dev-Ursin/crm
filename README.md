# CRM em Python

Este projeto fornece um CRM simples em Python usando SQLite e uma interface de linha de comando. É ideal para registrar clientes, acompanhar interações e gerar resumos rápidos sem depender de serviços externos.

## Requisitos
- Python 3.10 ou superior

## Instalação
Crie e ative um ambiente virtual (opcional) e instale as dependências opcionais de teste:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Uso
Execute os comandos abaixo a partir da raiz do repositório. O banco de dados é criado automaticamente em `crm.db`, mas você pode alterar o caminho com `--db`.

### Adicionar cliente
```bash
python -m crm.cli add-customer "Maria da Silva" --email maria@example.com --phone "+55 11 99999-9999" --company "ACME"
```

### Listar clientes
```bash
python -m crm.cli list-customers
python -m crm.cli list-customers --search "Silva"
```

### Registrar interação
```bash
python -m crm.cli add-interaction 1 --type "call" --notes "Follow-up sobre proposta"
```

### Detalhar cliente e interações
```bash
python -m crm.cli show-customer 1
```

### Resumo de interações
```bash
python -m crm.cli summary 1
```

## Testes
Os testes usam `pytest`.

```bash
pytest
```
