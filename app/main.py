from fastapi import FastAPI
from app.database import engine, Base
from app.routers import compra

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Mercado Pago")

app.include_router(compra.router)
