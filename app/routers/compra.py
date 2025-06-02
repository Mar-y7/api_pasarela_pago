from fastapi import APIRouter, Depends, HTTPException
from app.supabase_cliente import supabase
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
def crear_compra(compra: schemas.CompraCreate):
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
    preference_id = preference["response"].get("id")

    if not preference_id:
        raise HTTPException(status_code=500, detail="Error al generar la preferencia")

    # Construir el nuevo objeto
    nueva_compra = {
        "producto": compra.producto,
        "descripcion": compra.descripcion,
        "monto": compra.monto,
        "estado": "pendiente",
        "preference_id": preference_id,
        "email": compra.email
    }

    # Insertar en Supabase
    respuesta = supabase.table("compras").insert(nueva_compra).execute()

    if not respuesta.data:
        raise HTTPException(status_code=500, detail="No se pudo registrar la compra en Supabase")

    return respuesta.data[0]


@router.get("/{compra_id}", response_model=schemas.CompraResponse)
def obtener_compra(compra_id: int):
    resultado = supabase.table("compras").select("*").eq("id", compra_id).execute()
    if not resultado.data:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    return resultado.data[0]


@router.post("/webhook")
def recibir_webhook(payload: dict):
    if payload.get("type") != "payment":
        return {"mensaje": "Tipo de evento ignorado"}

    payment_id = payload.get("data", {}).get("id")
    
    if not payment_id:
        raise HTTPException(status_code=400, detail="ID de pago no encontrado")

    payment = sdk.payment().get(payment_id)
    payment_info = payment["response"]
    status = payment_info.get("status")
    preference_id = payment_info.get("order", {}).get("id")

    # Buscar compra en Supabase
    resultado = supabase.table("compras").select("*").eq("preference_id", preference_id).execute()

    if not resultado.data:
        raise HTTPException(status_code=404, detail="Compra no encontrada para este preference_id")

    compra = resultado.data[0]  # obtenemos el registro

    # Actualizar estado en Supabase
    supabase.table("compras").update({"estado": status}).eq("id", compra["id"]).execute()

    # Enviar correo si fue aprobado
    if status == "approved":
        enviar_correo(
            destinatario=compra["email"],
            asunto="Tu pago fue aprobado",
            mensaje=f"Tu compra '{compra['producto']}' fue aprobada exitosamente."
        )

    return {"mensaje": f"Compra actualizada a estado: {status}"}
