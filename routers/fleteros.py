from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import UsuarioDB
from schemas import FleteroCreate, LoginRequest
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["Fleteros"])

class ActualizarFleteroIn(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    vehiculo: Optional[str] = None
    patente: Optional[str] = None
    cbu_cvu: Optional[str] = None
    alias_bancario: Optional[str] = None
    nombre_banco: Optional[str] = None

@router.post("/fleteros/", status_code=status.HTTP_201_CREATED)
def registrar_fletero(fletero: FleteroCreate, db: Session = Depends(get_db)):
    existente = db.query(UsuarioDB).filter(UsuarioDB.email == fletero.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")

    nuevo_fletero = UsuarioDB(
        nombre=fletero.nombre,
        tipo="fletero",
        telefono=fletero.telefono,
        email=fletero.email,
        password=fletero.password,
        vehiculo=fletero.vehiculo,
        patente=fletero.patente,
        cbu_cvu=getattr(fletero, 'cbu_cvu', None),
        alias_bancario=getattr(fletero, 'alias_bancario', None),
        nombre_banco=getattr(fletero, 'nombre_banco', None),
        dni_frente=fletero.dni_frente,
        dni_dorso=fletero.dni_dorso,
        cedula_frente=fletero.cedula_frente,
        cedula_dorso=fletero.cedula_dorso,
        seguro_pdf=fletero.seguro_pdf,
        calificacion=5.0
    )
    db.add(nuevo_fletero)
    db.commit()
    db.refresh(nuevo_fletero)
    return {
        "mensaje": "Fletero registrado con éxito. Documentación en revisión.",
        "fletero": {
            "id": nuevo_fletero.id,
            "nombre": nuevo_fletero.nombre,
            "vehiculo": nuevo_fletero.vehiculo,
            "patente": nuevo_fletero.patente,
            "cbu_cvu": nuevo_fletero.cbu_cvu,
            "alias_bancario": nuevo_fletero.alias_bancario,
            "nombre_banco": nuevo_fletero.nombre_banco
        }
    }

@router.post("/fleteros/login")
def login_fletero(credenciales: LoginRequest, db: Session = Depends(get_db)):
    fletero = db.query(UsuarioDB).filter(
        UsuarioDB.email == credenciales.email,
        UsuarioDB.tipo == "fletero"
    ).first()

    if not fletero or fletero.password != credenciales.password:
        raise HTTPException(status_code=400, detail="Correo o contraseña incorrectos")

    return {
        "mensaje": "Inicio de sesión exitoso",
        "fletero": {
            "id": fletero.id,
            "nombre": fletero.nombre,
            "email": fletero.email,
            "telefono": fletero.telefono,
            "vehiculo": fletero.vehiculo,
            "patente": fletero.patente,
            "cbu_cvu": fletero.cbu_cvu,
            "alias_bancario": fletero.alias_bancario,
            "nombre_banco": fletero.nombre_banco
        }
    }

@router.get("/fleteros/{fletero_id}")
def obtener_fletero(fletero_id: int, db: Session = Depends(get_db)):
    fletero = db.query(UsuarioDB).filter(UsuarioDB.id == fletero_id, UsuarioDB.tipo == "fletero").first()
    if not fletero:
        raise HTTPException(status_code=404, detail="Fletero no encontrado")
    return {
        "id": fletero.id,
        "nombre": fletero.nombre,
        "telefono": fletero.telefono,
        "email": fletero.email,
        "vehiculo": fletero.vehiculo,
        "patente": fletero.patente,
        "cbu_cvu": fletero.cbu_cvu,
        "alias_bancario": fletero.alias_bancario,
        "nombre_banco": fletero.nombre_banco,
        "calificacion": fletero.calificacion,
        "estado_aprobacion": "En estado de aprobación (Revisando documentación)"
    }

@router.put("/fleteros/{fletero_id}")
def actualizar_fletero(fletero_id: int, datos: ActualizarFleteroIn, db: Session = Depends(get_db)):
    fletero = db.query(UsuarioDB).filter(UsuarioDB.id == fletero_id, UsuarioDB.tipo == "fletero").first()
    if not fletero:
        raise HTTPException(status_code=404, detail="Fletero no encontrado")
    
    if datos.nombre is not None: fletero.nombre = datos.nombre
    if datos.email is not None: fletero.email = datos.email
    if datos.telefono is not None: fletero.telefono = datos.telefono
    if datos.vehiculo is not None: fletero.vehiculo = datos.vehiculo
    if datos.patente is not None: fletero.patente = datos.patente
    if datos.cbu_cvu is not None: fletero.cbu_cvu = datos.cbu_cvu
    if datos.alias_bancario is not None: fletero.alias_bancario = datos.alias_bancario
    if datos.nombre_banco is not None: fletero.nombre_banco = datos.nombre_banco
    
    db.commit()
    db.refresh(fletero)
    
    return {
        "status": "success",
        "mensaje": "Perfil actualizado correctamente",
        "fletero": {
            "id": fletero.id,
            "nombre": fletero.nombre,
            "email": fletero.email,
            "telefono": fletero.telefono,
            "vehiculo": fletero.vehiculo,
            "patente": fletero.patente,
            "cbu_cvu": fletero.cbu_cvu,
            "alias_bancario": fletero.alias_bancario,
            "nombre_banco": fletero.nombre_banco
        }
    }