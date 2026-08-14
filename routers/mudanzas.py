from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import UsuarioDB, MudanzaDB, OfertaDB
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
        estado_pago="pendiente",
        fletero_aprobo=False
    )
    db.add(nueva_mudanza)
    db.commit()
    db.refresh(nueva_mudanza)

    mudanza_dict = {
        "id": nueva_mudanza.id,
        "cliente_id": nueva_mudanza.cliente_id,
        "origen_direccion": nueva_mudanza.origen_direccion,
        "destino_direccion": nueva_mudanza.destino_direccion,
        "descripcion_carga": nueva_mudanza.descripcion_carga,
        "estado": getattr(nueva_mudanza, "estado", "buscando_ofertas"),
        "estado_pago": getattr(nueva_mudanza, "estado_pago", "pendiente"),
        "fletero_aprobo": getattr(nueva_mudanza, "fletero_aprobo", False)
    }

    return {"mensaje": "Mudanza publicada con éxito", "mudanza": mudanza_dict}

@router.get("", response_model=list)
@router.get("/", response_model=list)
def listar_mudanzas(db: Session = Depends(get_db)):
    mudanzas = db.query(MudanzaDB).all()
    resultado = []
    for m in mudanzas:
        ofertas_db = db.query(OfertaDB).filter(OfertaDB.mudanza_id == m.id).all()
        ofertas_serializadas = [{
            "id": o.id,
            "mudanza_id": o.mudanza_id,
            "fletero_id": o.fletero_id,
            "monto_oferta": o.monto_oferta,
            "tiempo_estimado": o.tiempo_estimado,
            "estado": o.estado
        } for o in ofertas_db]

        resultado.append({
            # Propiedades planas para el panel del fletero
            "id": m.id,
            "cliente_id": m.cliente_id,
            "origen_direccion": m.origen_direccion,
            "destino_direccion": m.destino_direccion,
            "descripcion_carga": m.descripcion_carga,
            "estado": getattr(m, "estado", "buscando_ofertas"),
            "estado_pago": getattr(m, "estado_pago", "pendiente"),
            "fletero_aprobo": getattr(m, "fletero_aprobo", False),
            
            # Estructura anidada para el cliente
            "mudanza": {
                "id": m.id,
                "cliente_id": m.cliente_id,
                "origen_direccion": m.origen_direccion,
                "destino_direccion": m.destino_direccion,
                "descripcion_carga": m.descripcion_carga,
                "estado": getattr(m, "estado", "buscando_ofertas"),
                "estado_pago": getattr(m, "estado_pago", "pendiente"),
                "fletero_aprobo": getattr(m, "fletero_aprobo", False)
            },
            "ofertas": ofertas_serializadas
        })
    return resultado

@router.get("/cliente/{cliente_id}")
@router.get("/cliente/{cliente_id}/")
def listar_mudanzas_por_cliente(cliente_id: int, db: Session = Depends(get_db)):
    mudanzas = db.query(MudanzaDB).filter(MudanzaDB.cliente_id == cliente_id).all()
    resultado = []
    for m in mudanzas:
        ofertas_db = db.query(OfertaDB).filter(OfertaDB.mudanza_id == m.id).all()
        ofertas_serializadas = [{
            "id": o.id,
            "mudanza_id": o.mudanza_id,
            "fletero_id": o.fletero_id,
            "monto_oferta": o.monto_oferta,
            "tiempo_estimado": o.tiempo_estimado,
            "estado": o.estado
        } for o in ofertas_db]

        resultado.append({
            "mudanza": {
                "id": m.id,
                "cliente_id": m.cliente_id,
                "origen_direccion": m.origen_direccion,
                "destino_direccion": m.destino_direccion,
                "descripcion_carga": m.descripcion_carga,
                "estado": getattr(m, "estado", "buscando_ofertas"),
                "estado_pago": getattr(m, "estado_pago", "pendiente"),
                "fletero_aprobo": getattr(m, "fletero_aprobo", False)
            },
            "ofertas": ofertas_serializadas
        })
    return resultado

@router.put("/{mudanza_id}/aprobar-fletero")
@router.put("/{mudanza_id}/aprobar-fletero/")
def aprobar_fletero(mudanza_id: int, db: Session = Depends(get_db)):
    mudanza = db.query(MudanzaDB).filter(MudanzaDB.id == mudanza_id).first()
    if not mudanza:
        raise HTTPException(status_code=404, detail="Mudanza no encontrada")
    
    mudanza.fletero_aprobo = True
    db.commit()
    db.refresh(mudanza)
    return {"mensaje": "Mudanza aprobada por el fletero con éxito", "mudanza_id": mudanza.id}