from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, index=True)
    producto = Column(String, nullable=False)
    descripcion = Column(String)
    monto = Column(Float, nullable=False)
    estado = Column(String, default="pendiente")
    preference_id = Column(String)
    email = Column(String, nullable=False)  # o nullable=True si quieres permitir compras sin correo

