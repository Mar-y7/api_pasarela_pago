from pydantic import BaseModel, EmailStr
from typing import Optional

class CompraBase(BaseModel):
    producto: str
    descripcion: Optional[str]
    monto: float
    email: EmailStr  

class CompraCreate(CompraBase):
    pass

class CompraResponse(CompraBase):
    id: int
    estado: str
    preference_id: Optional[str]

    class Config:
        from_attributes = True

