from pathlib import Path
from typing import Dict, List, Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="CRM SAAS", version="0.2.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


class Stage(BaseModel):
    name: str = Field(..., min_length=2, max_length=60)


class Pipeline(BaseModel):
    id: int
    name: str = Field(..., min_length=2, max_length=80)
    stages: List[Stage] = Field(default_factory=list)


class CreatePipeline(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    stages: List[Stage] = Field(default_factory=list)


class Lead(BaseModel):
    id: int
    title: str = Field(..., min_length=2, max_length=120)
    pipeline_id: int
    stage_name: str


class CreateLead(BaseModel):
    title: str = Field(..., min_length=2, max_length=120)
    pipeline_id: int


class MoveLead(BaseModel):
    stage_name: str


class Card(BaseModel):
    id: int
    title: str = Field(..., min_length=2, max_length=120)
    status: Literal["todo", "doing", "done"] = "todo"


class CreateCard(BaseModel):
    title: str = Field(..., min_length=2, max_length=120)
    status: Literal["todo", "doing", "done"] = "todo"


class UpdateCardStatus(BaseModel):
    status: Literal["todo", "doing", "done"]


class Settings(BaseModel):
    company_name: str = "Minha Empresa"
    locale: str = "pt-BR"
    timezone: str = "America/Sao_Paulo"


pipelines: Dict[int, Pipeline] = {}
leads: Dict[int, Lead] = {}
cards: Dict[int, Card] = {}
settings = Settings()

pipeline_counter = 1
lead_counter = 1
card_counter = 1


@app.get("/")
def frontend() -> FileResponse:
    return FileResponse(BASE_DIR / "templates" / "index.html")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/smartflow/pipelines", response_model=Pipeline)
def create_pipeline(payload: CreatePipeline) -> Pipeline:
    global pipeline_counter

    pipeline = Pipeline(id=pipeline_counter, name=payload.name, stages=payload.stages)
    pipelines[pipeline_counter] = pipeline
    pipeline_counter += 1
    return pipeline


@app.get("/smartflow/pipelines", response_model=List[Pipeline])
def list_pipelines() -> List[Pipeline]:
    return list(pipelines.values())


@app.post("/smartflow/leads", response_model=Lead)
def create_lead(payload: CreateLead) -> Lead:
    global lead_counter

    pipeline = pipelines.get(payload.pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline não encontrada")
    if not pipeline.stages:
        raise HTTPException(status_code=400, detail="Pipeline sem estágios")

    lead = Lead(
        id=lead_counter,
        title=payload.title,
        pipeline_id=payload.pipeline_id,
        stage_name=pipeline.stages[0].name,
    )
    leads[lead_counter] = lead
    lead_counter += 1
    return lead


@app.get("/smartflow/leads", response_model=List[Lead])
def list_leads() -> List[Lead]:
    return list(leads.values())


@app.patch("/smartflow/leads/{lead_id}", response_model=Lead)
def move_lead(lead_id: int, payload: MoveLead) -> Lead:
    lead = leads.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    pipeline = pipelines.get(lead.pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline não encontrada")

    valid_stages = {stage.name for stage in pipeline.stages}
    if payload.stage_name not in valid_stages:
        raise HTTPException(status_code=400, detail="Estágio inválido para a pipeline")

    lead.stage_name = payload.stage_name
    leads[lead_id] = lead
    return lead


@app.post("/kanban/cards", response_model=Card)
def create_card(payload: CreateCard) -> Card:
    global card_counter

    card = Card(id=card_counter, title=payload.title, status=payload.status)
    cards[card_counter] = card
    card_counter += 1
    return card


@app.get("/kanban/cards", response_model=List[Card])
def list_cards() -> List[Card]:
    return list(cards.values())


@app.patch("/kanban/cards/{card_id}", response_model=Card)
def update_card_status(card_id: int, payload: UpdateCardStatus) -> Card:
    card = cards.get(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card não encontrado")

    card.status = payload.status
    cards[card_id] = card
    return card


@app.get("/configuracoes", response_model=Settings)
def get_settings() -> Settings:
    return settings


@app.put("/configuracoes", response_model=Settings)
def update_settings(payload: Settings) -> Settings:
    global settings

    settings = payload
    return settings
