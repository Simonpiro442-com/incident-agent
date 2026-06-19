from fastapi import FastAPI 
from app.routes.alerts import router as alerts_router
from app.db.database import engine
from app.db.models import Incident
from app.db.database import Base 
from app.db.database import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Incident Response Agent",
    version="0.1.0"

)

app.include_router(alerts_router)