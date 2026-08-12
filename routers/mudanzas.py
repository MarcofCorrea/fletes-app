from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import MudanzaDB, UsuarioDB
from schemas import MudanzaCreate

router = APIRouter(tags=["Mudanzas"])

@router.post("/mudanzas", status_code=status.HTTP_201_CREATED)
def crear_mudanza(mudanza: MudanzaCreate, db: Session = Depends(get_db)):
    cliente = db.query(UsuarioDB).filter(UsuarioDB.id == mudanza.cliente_id, UsuarioDB.tipo == "cliente").first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    nueva_mudanza = MudanzaDB(
        cliente_id=mudanza.cliente_id,
        origen_direccion=mudanza.origen_direccion,
        destino_direccion=mudanza.destino_direccion,
        descripcion_carga=mudanza.descripcion_carga,
        estado="buscando_ofertas",
        estado_pago="pendiente"
    )
    db.add(nueva_mudanza)
    db.commit()
    db.refresh(nueva_mudanza)
    return {"mensaje": "Mudanza publicada con éxito", "mudanza": nueva_mudanza}

@router.get("/mudanzas/")
def listar_mudanzas(db: Session = Depends(get_db)):
    return db.query(MudanzaDB).all()