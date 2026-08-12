from pydantic import BaseModel, ConfigDict

class ClienteCreate(BaseModel):
    nombre: str
    telefono: str
    email: str
    password: str
    dni_frente: str
    dni_dorso: str

class FleteroCreate(BaseModel):
    nombre: str
    telefono: str
    email: str
    password: str
    vehiculo: str
    patente: str
    dni_frente: str
    dni_dorso: str
    cedula_frente: str
    cedula_dorso: str
    seguro_pdf: str

class LoginRequest(BaseModel):
    email: str
    password: str

class MudanzaCreate(BaseModel):
    cliente_id: int
    origen_direccion: str
    destino_direccion: str
    descripcion_carga: str

class OfertaCreate(BaseModel):
    mudanza_id: int
    fletero_id: int
    monto_oferta: float
    tiempo_estimado: str

class OfertaUpdate(BaseModel):
    nuevo_monto: float
    nuevo_tiempo: str

class OfertaResponse(BaseModel):
    id: int
    mudanza_id: int
    fletero_id: int
    monto_oferta: float
    tiempo_estimado: str
    estado: str

    model_config = ConfigDict(from_attributes=True)