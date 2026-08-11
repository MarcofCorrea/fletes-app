from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import OfertaDB, MudanzaDB, UsuarioDB
from schemas import OfertaCreate

router = APIRouter(tags=["Ofertas"])

@router.post("/ofertas/", status_code=status.HTTP_201_CREATED)
def crear_oferta(oferta: OfertaCreate, db: Session = Depends(get_db)):
    fletero = db.query(UsuarioDB).filter(UsuarioDB.id == oferta.fletero_id, UsuarioDB.tipo == "fletero").first()
    if not fletero:
        raise HTTPException(status_code=404, detail="Fletero no encontrado")
    
    mudanza = db.query(MudanzaDB).filter(MudanzaDB.id == oferta.mudanza_id).first()
    if not mudanza:
        raise HTTPException(status_code=404, detail="Mudanza no encontrada")

    nueva_oferta = OfertaDB(
        mudanza_id=oferta.mudanza_id,
        fletero_id=oferta.fletero_id,
        monto_oferta=oferta.monto_oferta,
        tiempo_estimado=oferta.tiempo_estimado,
        estado="pendiente"
    )
    db.add(nueva_oferta)
    db.commit()
    db.refresh(nueva_oferta)
    return {"mensaje": "Oferta creada con éxito", "oferta": nueva_oferta}

@router.get("/ofertas/")
def listar_ofertas(db: Session = Depends(get_db)):
    return db.query(OfertaDB).all()

@router.get("/fletero/{fletero_id}/ofertas")
def listar_ofertas_fletero(fletero_id: int, db: Session = Depends(get_db)):
    return db.query(OfertaDB).filter(OfertaDB.fletero_id == fletero_id).all()

@router.put("/ofertas/{oferta_id}/aceptar")
def aceptar_oferta(oferta_id: int, db: Session = Depends(get_db)):
    oferta = db.query(OfertaDB).filter(OfertaDB.id == oferta_id).first()
    if not oferta:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    
    # Marcar oferta como aceptada
    oferta.estado = "aceptada"
    
    # Cambiar la mudanza a en_curso
    mudanza = db.query(MudanzaDB).filter(MudanzaDB.id == oferta.mudanza_id).first()
    if mudanza:
        mudanza.estado = "en_curso"
        
    # Rechazar el resto de ofertas para esta misma mudanza
    otras_ofertas = db.query(OfertaDB).filter(
        OfertaDB.mudanza_id == oferta.mudanza_id, 
        OfertaDB.id != oferta_id
    ).all()
    for otra in otras_ofertas:
        otra.estado = "rechazada"
        
    db.commit()
    return {"mensaje": "Oferta aceptada con éxito. Viaje en curso."}