import mercadopago
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import MudanzaDB

router = APIRouter(tags=["Pagos"])

# Inicializamos el SDK de Mercado Pago con tu Access Token de producción/credenciales
sdk = mercadopago.SDK("APP_USR-2370906297861152-081112-44bd34ccbf6c5ca4a15f26712bee3918-3609276874")

class PeticionPago(BaseModel):
    mudanza_id: int
    monto: float
    titulo: str

@router.post("/crear-preferencia")
def crear_preferencia_pago(pago: PeticionPago, db: Session = Depends(get_db)):
    # Verificamos que la mudanza exista
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
            "success": "https://fletes-app.onrender.com/cliente.html?pago=exitoso",
            "failure": "https://fletes-app.onrender.com/cliente.html?pago=fallido",
            "pending": "https://fletes-app.onrender.com/cliente.html?pago=pendiente"
        },
        "auto_return": "approved",
    }

    result = sdk.preference().create(preference_data)
    preference = result["response"]
    
    # Devolvemos el link de pago oficial de Mercado Pago
    return {
        "preference_id": preference.get("id"),
        "init_point": preference.get("init_point"),
        "sandbox_init_point": preference.get("sandbox_init_point")
    }