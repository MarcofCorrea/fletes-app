from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import UsuarioDB, MudanzaDB
from schemas import MudanzaCreate

router = APIRouter(tags=["Mudanzas"])

@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_mudanza(mudanza: MudanzaCreate, db: Session = Depends(get_db)):
    cliente = db.query(UsuarioDB).filter(UsuarioDB.id == mudanza.cliente_id).first()
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

    # Serializamos a diccionario para evitar errores de Pydantic
    mudanza_dict = {
        "id": nueva_mudanza.id,
        "cliente_id": nueva_mudanza.cliente_id,
        "origen_direccion": nueva_mudanza.origen_direccion,
        "destino_direccion": nueva_mudanza.destino_direccion,
        "descripcion_carga": nueva_mudanza.descripcion_carga,
        "estado": getattr(nueva_mudanza, "estado", "buscando_ofertas"),
        "estado_pago": getattr(nueva_mudanza, "estado_pago", "pendiente")
    }

    return {"mensaje": "Mudanza publicada con éxito", "mudanza": mudanza_dict}

@router.get("", response_model=list)
@router.get("/", response_model=list)
def listar_mudanzas(db: Session = Depends(get_db)):
    mudanzas = db.query(MudanzaDB).all()
    resultado = []
    for m in mudanzas:
        resultado.append({
            "id": m.id,
            "cliente_id": m.cliente_id,
            "origen_direccion": m.origen_direccion,
            "destino_direccion": m.destino_direccion,
            "descripcion_carga": m.descripcion_carga,
            "estado": getattr(m, "estado", "buscando_ofertas"),
            "estado_pago": getattr(m, "estado_pago", "pendiente")
        })
    return resultado

@router.get("/cliente/{cliente_id}")
@router.get("/cliente/{cliente_id}/")
def listar_mudanzas_por_cliente(cliente_id: int, db: Session = Depends(get_db)):
    mudanzas = db.query(MudanzaDB).filter(MudanzaDB.cliente_id == cliente_id).all()
    resultado = []
    for m in mudanzas:
        resultado.append({
            "id": m.id,
            "cliente_id": m.cliente_id,
            "origen_direccion": m.origen_direccion,
            "destino_direccion": m.destino_direccion,
            "descripcion_carga": m.descripcion_carga,
            "estado": getattr(m, "estado", "buscando_ofertas"),
            "estado_pago": getattr(m, "estado_pago", "pendiente")
        })
    return resultado