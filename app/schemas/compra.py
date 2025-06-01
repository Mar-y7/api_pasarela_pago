from pydantic import BaseModel
from typing import Optional

class CompraBase(BaseModel):
    producto: str
    descripcion: Optional[str]
    monto: float
    email: str

class CompraCreate(CompraBase):
    pass

class CompraResponse(CompraBase):
    id: int
    estado: str
    preference_id: Optional[str]

    class Config:
        orm_mode = True
