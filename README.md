# CRM SAAS - Módulo Inicial

Este repositório contém a base de um CRM com automação, com os módulos iniciais:

- **Smartflow**: gerenciamento de fluxo de negócios por estágios.
- **Kanban**: quadro visual para tarefas e cards.
- **Configurações**: preferências gerais do tenant.

## Stack inicial

- Python 3.11+
- FastAPI
- Testes com pytest

## Como executar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Como testar

```bash
pytest -q
```
