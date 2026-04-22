from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_smartflow_pipeline_and_lead_flow():
    pipeline_response = client.post(
        "/smartflow/pipelines",
        json={
            "name": "Funil Comercial",
            "stages": [{"name": "Novo"}, {"name": "Proposta"}, {"name": "Fechado"}],
        },
    )
    assert pipeline_response.status_code == 200
    pipeline_id = pipeline_response.json()["id"]

    lead_response = client.post(
        "/smartflow/leads",
        json={"title": "Lead Empresa XPTO", "pipeline_id": pipeline_id},
    )
    assert lead_response.status_code == 200
    assert lead_response.json()["stage_name"] == "Novo"

    lead_id = lead_response.json()["id"]

    move_response = client.patch(
        f"/smartflow/leads/{lead_id}",
        json={"stage_name": "Proposta"},
    )

    assert move_response.status_code == 200
    assert move_response.json()["stage_name"] == "Proposta"


def test_kanban_card_flow():
    create_response = client.post(
        "/kanban/cards",
        json={"title": "Ligar para cliente", "status": "todo"},
    )
    assert create_response.status_code == 200
    card_id = create_response.json()["id"]

    update_response = client.patch(
        f"/kanban/cards/{card_id}",
        json={"status": "doing"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "doing"


def test_configuracoes_update():
    update_response = client.put(
        "/configuracoes",
        json={
            "company_name": "CRM Labs",
            "locale": "pt-BR",
            "timezone": "America/Sao_Paulo",
        },
    )
    assert update_response.status_code == 200

    get_response = client.get("/configuracoes")
    assert get_response.status_code == 200
    assert get_response.json()["company_name"] == "CRM Labs"
