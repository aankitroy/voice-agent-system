from fastapi import FastAPI

from app.db import Base, engine
# -------------------------------------------------------------
from fastapi.middleware.cors import CORSMiddleware
# -------------------------------------------------------------
from app.models.workspace import Workspace   # IMPORTANT
from app.models.user import User
from app.models.workspace_member import WorkspaceMember
from app.models.agent import Agent
from app.models.execution import Execution
from app.models.api_log import APILog
from app.models.webhook import WebhookLog
from app.models.knowledge_base import KnowledgeBase
# -------------------------------------------------------------
from app.routes import auth #IMPORTING ROUTES
from app.routes import agent
from app.routes import webhook
from app.routes import calls
from app.routes import settings
from app.routes import knowledge_base

# --------------------------------------------------------------

app = FastAPI(title="Voice AI SaaS Platform")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# ----------------------------------------------------------------

# TABLE CREATE
Base.metadata.create_all(bind=engine)

# -----------------------------------------------------------------


app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(agent.router, prefix="/agent", tags = ["Agents"])
app.include_router(webhook.router, prefix="/webhook", tags=["Webhook"])
app.include_router(calls.router, prefix="/calls", tags = ["Calls"])
app.include_router(settings.router, prefix='/settings', tags = ["Settings"])
app.include_router(knowledge_base.router, prefix="/knowledge-base", tags=["Knowledge Base"])

# ----------------------------------------------------------------------

@app.get("/")
def home():
    return {"message": "Voice AI backend running"}
