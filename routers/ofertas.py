from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import OfertaDB, MudanzaDB
from pydantic import BaseModel

router = APIRouter(tags=["Ofertas"])

class OfertaCreate(BaseModel):
    mudanza_id: int
    fletero_id: int
    monto_oferta: float
    tiempo_estimado: str
    estado: str = "pendiente"

@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_oferta(oferta: OfertaCreate, db: Session = Depends(get_db)):
    nueva = OfertaDB(
        mudanza_id=oferta.mudanza_id,
        fletero_id=oferta.fletero_id,
        monto_oferta=oferta.monto_oferta,
        tiempo_estimado=oferta.tiempo_estimado,
        estado=oferta.estado
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return {"mensaje": "Oferta creada con éxito", "oferta": {
        "id": nueva.id,
        "mudanza_id": nueva.mudanza_id,
        "fletero_id": nueva.fletero_id,
        "monto_oferta": nueva.monto_oferta,
        "tiempo_estimado": nueva.tiempo_estimado,
        "estado": nueva.estado
    }}

@router.get("", response_model=list)
@router.get("/", response_model=list)
def listar_ofertas(db: Session = Depends(get_db)):
    ofertas = db.query(OfertaDB).all()
    return [{
        "id": o.id,
        "mudanza_id": o.mudanza_id,
        "fletero_id": o.fletero_id,
        "monto_oferta": o.monto_oferta,
        "tiempo_estimado": o.tiempo_estimado,
        "estado": o.estado
    } for o in ofertas]

@router.put("/{oferta_id}/aceptar")
@router.put("/{oferta_id}/aceptar/")
def aceptar_oferta(oferta_id: int, db: Session = Depends(get_db)):
    oferta = db.query(OfertaDB).filter(OfertaDB.id == oferta_id).first()
    if not oferta:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    oferta.estado = "aceptada"
    
    # Actualizamos también el estado de la mudanza relacionada
    mudanza = db.query(MudanzaDB).filter(MudanzaDB.id == oferta.mudanza_id).first()
    if mudanza:
        mudanza.estado = "aprobada"
        
    db.commit()
    return {"mensaje": "Oferta aceptada con éxito"}