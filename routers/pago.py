import os
import mercadopago
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import MudanzaDB

router = APIRouter(tags=["Pagos"])

# Inicializamos el SDK de Mercado Pago de forma segura usando variables de entorno
sdk = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN", ""))

class PeticionPago(BaseModel):
    mudanza_id: int
    monto: float
    titulo: str

@router.post("/crear-preferencia")
@router.post("/crear-preferencia-pago")
def crear_preferencia_pago(pago: PeticionPago, db: Session = Depends(get_db)):
    mudanza = db.query(MudanzaDB).filter(MudanzaDB.id == pago.mudanza_id).first()
    if not mudanza:
        raise HTTPException(status_code=404, detail="Mudanza no encontrada")

    preference_data = {
        "items": [
            {
                "title": pago.titulo,
                "quantity": 1,
                "unit_price": float(pago.monto)
            }
        ],
        "back_urls": {
            "success": "https://fletes-app.onrender.com/cliente.html?pago_exitoso=true&mudanza_id=" + str(pago.mudanza_id),
            "failure": "https://fletes-app.onrender.com/cliente.html?pago=fallido",
            "pending": "https://fletes-app.onrender.com/cliente.html?pago=pendiente"
        },
        "auto_return": "approved",
        "external_reference": str(pago.mudanza_id)
    }

    try:
        result = sdk.preference().create(preference_data)
        preference = result["response"]
        return {
            "preference_id": preference.get("id"),
            "init_point": preference.get("init_point"),
            "sandbox_init_point": preference.get("sandbox_init_point")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/procesar-pago")
@router.post("/procesar-pago/")
def procesar_pago(payment_data: dict, db: Session = Depends(get_db)):
    try:
        result = sdk.payment().create(payment_data)
        payment = result["response"]
        
        if payment.get("status") == "approved":
            external_ref = payment.get("external_reference")
            if external_ref:
                mudanza = db.query(MudanzaDB).filter(MudanzaDB.id == int(external_ref)).first()
                if mudanza:
                    mudanza.estado_pago = "pagado"
                    db.commit()
                    db.refresh(mudanza)
                    
        return payment
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/verificar-pago/{mudanza_id}")
def verificar_pago(mudanza_id: int, db: Session = Depends(get_db)):
    mudanza = db.query(MudanzaDB).filter(MudanzaDB.id == mudanza_id).first()
    if not mudanza:
        raise HTTPException(status_code=404, detail="Mudanza no encontrada")
    
    mudanza.estado_pago = "pagado"
    db.commit()
    db.refresh(mudanza)
    
    return {"mensaje": "Pago verificado y actualizado con éxito", "estado_pago": mudanza.estado_pago}