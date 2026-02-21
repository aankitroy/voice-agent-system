from fastapi import FastAPI

from app.db import Base, engine
from app.models.workspace import Workspace   # IMPORTANT
from app.routes import auth #IMPORTING ROUTES
from app.routes import agent

app = FastAPI(title="Voice AI SaaS Platform")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(agent.router, prefix="/agent", tags = ["Agents"])

# TABLE CREATE
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "Voice AI backend running"}
