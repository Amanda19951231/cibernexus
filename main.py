from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Leitura

app = FastAPI()

def listar(equipamento: str = None, db: Session = Depends(get_db)):
    query = db.query(Leitura)
    if equipamento:
        query = query.filter(Leitura.maquina == equipamento)
    return query.order_by(Leitura.id.desc()).all()

