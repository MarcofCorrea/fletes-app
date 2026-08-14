from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import UsuarioDB
from schemas import ClienteCreate, LoginRequest
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["Clientes"])

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None

@router.get("", status_code=status.HTTP_200_OK)
@router.get("/", status_code=status.HTTP_200_OK)
def listar_clientes(db: Session = Depends(get_db)):
    clientes = db.query(UsuarioDB).filter(UsuarioDB.tipo == "cliente").all()
    return clientes

@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    existente = db.query(UsuarioDB).filter(UsuarioDB.email == cliente.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")
    
    nuevo = UsuarioDB(
        nombre=cliente.nombre,
        tipo="cliente",
        telefono=cliente.telefono,
        email=cliente.email,
        password=cliente.password,
        dni_frente=cliente.dni_frente,
        dni_dorso=cliente.dni_dorso
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"mensaje": "Cliente registrado con éxito", "cliente": {"id": nuevo.id, "nombre": nuevo.nombre}}

@router.post("/login")
@router.post("/login/")
def login_cliente(credenciales: LoginRequest, db: Session = Depends(get_db)):
    cliente = db.query(UsuarioDB).filter(
        UsuarioDB.email == credenciales.email,
        UsuarioDB.tipo == "cliente"
    ).first()
    if not cliente or cliente.password != credenciales.password:
        raise HTTPException(status_code=400, detail="Correo o contraseña incorrectos")
    return {"mensaje": "Login exitoso", "cliente": {"id": cliente.id, "nombre": cliente.nombre}}

@router.get("/{cliente_id}", status_code=status.HTTP_200_OK)
@router.get("/{cliente_id}/", status_code=status.HTTP_200_OK)
def obtener_cliente_por_id(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(UsuarioDB).filter(UsuarioDB.id == cliente_id, UsuarioDB.tipo == "cliente").first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"cliente": cliente}

@router.put("/{cliente_id}")
@router.put("/{cliente_id}/")
def actualizar_cliente(cliente_id: int, datos: ClienteUpdate, db: Session = Depends(get_db)):
    cliente = db.query(UsuarioDB).filter(UsuarioDB.id == cliente_id, UsuarioDB.tipo == "cliente").first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    if datos.nombre is not None:
        cliente.nombre = datos.nombre
    if datos.email is not None:
        cliente.email = datos.email
    if datos.telefono is not None:
        cliente.telefono = datos.telefono
    db.commit()
    db.refresh(cliente)
    return {"mensaje": "Perfil actualizado con éxito", "cliente": cliente}

@router.get("/{cliente_id}/mudanzas")
@router.get("/{cliente_id}/mudanzas/")
def obtener_mudanzas_cliente(cliente_id: int, db: Session = Depends(get_db)):
    from models import MudanzaDB, OfertaDB
    mudanzas = db.query(MudanzaDB).filter(MudanzaDB.cliente_id == cliente_id).all()
    resultado = []
    for m in mudanzas:
        ofertas = db.query(OfertaDB).filter(OfertaDB.mudanza_id == m.id).all()
        resultado.append({
            "mudanza": m,
            "ofertas": ofertas
        })
    return resultado