from fastapi import FastAPI
from app.routers import compra

app = FastAPI(title="API Mercado Pago")

# Registrar tu router (por ejemplo, compras)
app.include_router(compra.router, prefix="/compras", tags=["Compras"])
