from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine, Base
from models import UsuarioDB, MudanzaDB, OfertaDB
from routers import clientes, fleteros, mudanzas, ofertas
import mercadopago
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import text

Base.metadata.create_all(bind=engine)

try:
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE mudanzas ADD COLUMN estado_pago VARCHAR DEFAULT 'pendiente'"))
except Exception:
    pass

try:
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE usuarios ADD COLUMN cbu_cvu VARCHAR"))
        connection.execute(text("ALTER TABLE usuarios ADD COLUMN alias_bancario VARCHAR"))
        connection.execute(text("ALTER TABLE usuarios ADD COLUMN nombre_banco VARCHAR"))
except Exception:
    pass

app = FastAPI(
    title="FletesApp API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Corrección de prefijos para evitar errores 404 en las peticiones del frontend
app.include_router(clientes.router, prefix="/clientes")
app.include_router(fleteros.router, prefix="/fleteros")
app.include_router(mudanzas.router, prefix="/mudanzas")
app.include_router(ofertas.router, prefix="/ofertas")

sdk = mercadopago.SDK("APP_USR-2370906297861152-081112-44bd34ccbf6c5ca4a15f26712bee3918-3609276874")

class ItemPago(BaseModel):
    mudanza_id: int
    titulo: str
    monto: float

class RegistrarTarjetaIn(BaseModel):
    cliente_id: int
    token_tarjeta: str
    email: str

class CobroGuardadoIn(BaseModel):
    mudanza_id: int
    monto: float
    customer_id: str
    card_id: str

class CalificacionIn(BaseModel):
    usuario_id: int
    estrellas: float

@app.post("/crear-preferencia-pago")
def crear_preferencia(item: ItemPago, request: Request):
    try:
        base_url = str(request.base_url).rstrip("/")
        
        preference_data = {
            "items": [
                {
                    "title": f"Mudanza #{item.mudanza_id} - {item.titulo}",
                    "quantity": 1,
                    "unit_price": float(item.monto),
                    "currency_id": "ARS"
                }
            ],
            "back_urls": {
                "success": f"https://fletes-app.onrender.com/cliente.html?pago=exitoso&mudanza_id={item.mudanza_id}",
                "failure": f"https://fletes-app.onrender.com/cliente.html?pago=fallido&mudanza_id={item.mudanza_id}",
                "pending": f"https://fletes-app.onrender.com/cliente.html?pago=pendiente&mudanza_id={item.mudanza_id}"
            },
            "auto_return": "approved",
            "external_reference": str(item.mudanza_id)
        }
        
        preference_response = sdk.preference().create(preference_data)
        
        if isinstance(preference_response, dict):
            resp_body = preference_response.get("response", preference_response)
            init_point = resp_body.get("sandbox_init_point") or resp_body.get("init_point")
            if init_point:
                return {"init_point": init_point}
        
        return {"detail": f"Respuesta inesperada de MP: {str(preference_response)}"}

    except Exception as e:
        return {"detail": str(e)}

@app.get("/verificar-pago/{mudanza_id}")
def verificar_pago_mp(mudanza_id: int):
    from database import SessionLocal
    db = SessionLocal()
    try:
        filters = {"external_reference": str(mudanza_id)}
        search_result = sdk.payment().search({"filters": filters})
        
        pagos = search_result.get("response", {}).get("results", [])
        pago_aprobado = False
        
        for pago in pagos:
            if pago.get("status") == "approved":
                pago_aprobado = True
                break
                
        mudanza = db.query(MudanzaDB).filter(MudanzaDB.id == mudanza_id).first()
        if mudanza and pago_aprobado:
            mudanza.estado_pago = "pagado"
            db.commit()
            return {"status": "pagado", "mensaje": "Pago verificado y acreditado por Mercado Pago."}
        
        return {"status": "pendiente", "mensaje": "No se encontró ningún pago aprobado para esta mudanza en Mercado Pago."}
    except Exception as e:
        return {"detail": str(e)}
    finally:
        db.close()

@app.put("/mudanzas/{mudanza_id}/pagar")
def marcar_mudanza_pagada(mudanza_id: int):
    from database import SessionLocal
    db = SessionLocal()
    try:
        mudanza = db.query(MudanzaDB).filter(MudanzaDB.id == mudanza_id).first()
        if not mudanza:
            return {"detail": "Mudanza no encontrada"}
        mudanza.estado_pago = "pagado"
        db.commit()
        return {"status": "success"}
    finally:
        db.close()

@app.post("/guardar-tarjeta")
def guardar_tarjeta(data: RegistrarTarjetaIn):
    try:
        customer_data = {"email": data.email}
        customer_response = sdk.customer().create(customer_data)
        
        if isinstance(customer_response, dict) and "response" in customer_response:
            customer_id = customer_response["response"]["id"]
            card_data = {"token": data.token_tarjeta}
            card_response = sdk.customer_card(customer_id).create(card_data)
            
            if isinstance(card_response, dict) and "response" in card_response:
                card_info = card_response["response"]
                return {
                    "status": "success",
                    "customer_id": customer_id,
                    "card_id": card_info.get("id"),
                    "ultimos_digitos": card_info.get("last_four_digits")
                }
        
        return {"status": "error", "detail": "No se pudo registrar la tarjeta"}
    except Exception as e:
        return {"detail": str(e)}

@app.post("/pagar-con-tarjeta-guardada")
def pagar_con_tarjeta_guardada(pago: CobroGuardadoIn):
    try:
        payment_data = {
            "transaction_amount": float(pago.monto),
            "description": f"Mudanza #{pago.mudanza_id}",
            "payment_method_id": "master", 
            "payer": { "id": pago.customer_id },
            "token": pago.card_id
        }
        
        payment_response = sdk.payment().create(payment_data)
        payment = payment_response.get("response", {})
        
        return {
            "status": payment.get("status"),
            "status_detail": payment.get("status_detail"),
            "id": payment.get("id")
        }
    except Exception as e:
        return {"detail": str(e)}

@app.post("/calificar-usuario")
def calificar_usuario(data: CalificacionIn):
    from database import SessionLocal
    db = SessionLocal()
    try:
        usuario = db.query(UsuarioDB).filter(UsuarioDB.id == data.usuario_id).first()
        if not usuario:
            return {"detail": "Usuario no encontrado"}
        usuario.calificacion = data.estrellas
        db.commit()
        return {"status": "success", "mensaje": "Calificación actualizada con éxito"}
    except Exception as e:
        return {"detail": str(e)}
    finally:
        db.close()

@app.get("/api-info")
def raiz():
    return {"mensaje": "¡Bienvenido a la API de FletesApp con verificación de pagos y soporte bancario en Modo Tester! 🚀"}

app.mount("/", StaticFiles(directory=".", html=True), name="static")