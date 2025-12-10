# CRM de Planilhas em Python

Aplicação web simples em Flask para gerenciar contatos armazenados em planilhas CSV. Inclui tela de login, dashboard com gráficos e cartões, cadastro manual de contatos e importação/exportação de planilhas.

## Funcionalidades
- **Login** com usuário e senha configuráveis por variáveis de ambiente (`CRM_USER`, `CRM_PASSWORD`).
- **Dashboard** com indicadores (leads, prospects, clientes, faturamento estimado) e gráfico do funil via Chart.js.
- **Lista rápida** dos últimos contatos ordenados por `ultima_interacao`.
- **Cadastro manual** de novos registros diretamente pelo formulário.
- **Upload de CSV** para substituir a base atual (mantém todas as colunas presentes no arquivo enviado).
- **Download** da planilha CSV atual.

## Como executar
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_SECRET="uma-chave-secreta"
# opcional: export CRM_USER=meu_user CRM_PASSWORD=minha_senha
python app.py
```

A aplicação ficará disponível em http://localhost:5000. Usuário padrão: `admin` / `admin`.

## Estrutura da planilha
A base padrão está em `data/clientes.csv`. As colunas recomendadas são:

- `nome`
- `email`
- `telefone`
- `empresa`
- `status` (Lead, Prospect, Cliente)
- `ultima_interacao` (AAAA-MM-DD)
- `valor_estm` (valor estimado do negócio)

Você pode exportar ou substituir essa planilha a qualquer momento pelo dashboard.
