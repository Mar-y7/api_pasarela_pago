from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import compra as schemas
import mercadopago
import os
from app.utils.email import enviar_correo
from dotenv import load_dotenv
load_dotenv()

ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")

if not ACCESS_TOKEN:
    raise RuntimeError("Falta el MP_ACCESS_TOKEN en el archivo .env")
sdk = mercadopago.SDK(ACCESS_TOKEN)

router = APIRouter(prefix="/compras", tags=["Compras"])

@router.post("/", response_model=schemas.CompraResponse)
def crear_compra(compra: schemas.CompraCreate, db: Session = Depends(get_db)):
    preference_data = {
        "items": [
            {
                "title": compra.producto,
                "quantity": 1,
                "unit_price": compra.monto,
                "description": compra.descripcion,
                "currency_id": "CLP"
            }
        ],
        "back_urls": {
            "success": "https://www.ejemplo.cl/success",
            "failure": "https://www.ejemplo.cl/failure",
            "pending": "https://www.ejemplo.cl/pending"
        },
        "auto_return": "approved"
    }

    preference = sdk.preference().create(preference_data)

    if "id" not in preference["response"]:
        raise HTTPException(status_code=500, detail="Error al generar la preferencia")

    nueva_compra = models.Compra(
        producto=compra.producto,
        descripcion=compra.descripcion,
        monto=compra.monto,
        preference_id=preference["response"]["id"],
        email=compra.email
    )
    db.add(nueva_compra)
    db.commit()
    db.refresh(nueva_compra)

    return nueva_compra

@router.get("/{compra_id}", response_model=schemas.CompraResponse)
def obtener_compra(compra_id: int, db: Session = Depends(get_db)):
    compra = db.query(models.Compra).filter(models.Compra.id == compra_id).first()
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    return compra

@router.post("/webhook")
def recibir_webhook(payload: dict, db: Session = Depends(get_db)):
    if payload.get("type") != "payment":
        return {"mensaje": "Tipo de evento ignorado"}

    payment_id = payload.get("data", {}).get("id")

    if not payment_id:
        raise HTTPException(status_code=400, detail="ID de pago no encontrado")

    # Consultar estado real desde Mercado Pago
    payment = sdk.payment().get(payment_id)
    payment_info = payment["response"]
    status = payment_info.get("status")
    preference_id = payment_info.get("order", {}).get("id")

    # Buscar compra localmente por preference_id
    compra = db.query(models.Compra).filter(models.Compra.preference_id == preference_id).first()
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada para este preference_id")

    # Actualizar estado
    compra.estado = status
    db.commit()

    if status == "approved":
        enviar_correo(
            destinatario=compra.email, 
            asunto="Tu pago fue aprobado",
            mensaje=f"Tu compra '{compra.producto}' fue aprobada exitosamente."
            )

    return {"mensaje": f"Compra actualizada a estado: {status}"}

