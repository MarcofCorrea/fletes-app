from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime
from database import Base

class UsuarioDB(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    tipo = Column(String)  # "cliente" o "fletero"
    telefono = Column(String, nullable=True)
    email = Column(String, nullable=True, unique=True)
    password = Column(String, nullable=True)
    calificacion = Column(Float, default=5.0)
    
    # Datos de vehículo y documentación de fletero
    vehiculo = Column(String, nullable=True)
    patente = Column(String, nullable=True)
    dni_frente = Column(String, nullable=True)
    dni_dorso = Column(String, nullable=True)
    cedula_frente = Column(String, nullable=True)
    cedula_dorso = Column(String, nullable=True)
    seguro_pdf = Column(String, nullable=True)
    
    # NUEVOS DATOS BANCARIOS PARA EL PAGO / RETENCIÓN
    cbu_cvu = Column(String, nullable=True)
    alias_bancario = Column(String, nullable=True)
    nombre_banco = Column(String, nullable=True)

class MudanzaDB(Base):
    __tablename__ = "mudanzas"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer)
    origen_direccion = Column(String)
    destino_direccion = Column(String)
    descripcion_carga = Column(String)
    estado = Column(String, default="buscando_ofertas")
    fletero_ganador_id = Column(Integer, nullable=True)
    precio_final = Column(Float, nullable=True)
    estado_pago = Column(String, default="pendiente") # "pendiente", "retenido_en_garantia", "pagado"
    fletero_aprobo = Column(Boolean, default=False) # NUEVO: Control oficial en base de datos para la comunicación entre partes
    creado_at = Column(DateTime, default=datetime.now)

class OfertaDB(Base):
    __tablename__ = "ofertas"
    id = Column(Integer, primary_key=True, index=True)
    mudanza_id = Column(Integer)
    fletero_id = Column(Integer)
    monto_oferta = Column(Float)
    tiempo_estimado = Column(String)
    estado = Column(String, default="pendiente")

class ReseñaDB(Base):
    __tablename__ = "reseñas"
    id = Column(Integer, primary_key=True, index=True)
    mudanza_id = Column(Integer, index=True)
    autor = Column(String)  # "Cliente" o "Fletero"
    calificado_id = Column(Integer, index=True)
    estrellas = Column(Integer)
    comentario = Column(String, default="Sin comentarios")
    fecha = Column(String)