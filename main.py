import os

from fastapi import FastAPI
from sqlmodel import SQLModel, Field, create_engine, Session, select
from prometheus_fastapi_instrumentator import Instrumentator

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///chamados.db")

engine = create_engine(DATABASE_URL)

app = FastAPI()

Instrumentator().instrument(app).expose(app)

class Chamado(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    titulo: str
    descricao: str
    status: str = "aberto"

SQLModel.metadata.create_all(engine)

@app.get("/")
def home():
    return {"mensagem": "Helpdesk API no ar"}

@app.post("/chamados")
def criar_chamado(chamado: Chamado):
    with Session(engine) as session:
        session.add(chamado)
        session.commit()
        session.refresh(chamado)
        return chamado

@app.get("/chamados")
def listar_chamados():
    with Session(engine) as session:
        return session.exec(select(Chamado)).all()

@app.put("/chamados/{chamado_id}")
def atualizar_status(chamado_id: int, novo_status: str):
    with Session(engine) as session:
        chamado = session.get(Chamado, chamado_id)
        if chamado:
            chamado.status = novo_status
            session.add(chamado)
            session.commit()
            session.refresh(chamado)
            return chamado
        return {"erro": "Chamado não encontrado"}