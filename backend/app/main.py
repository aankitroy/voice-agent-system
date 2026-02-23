from fastapi import FastAPI

from app.db import Base, engine
from app.models.workspace import Workspace   # IMPORTANT
from app.models.user import User
from app.models.workspace_member import WorkspaceMember
from app.models.agent import Agent
from app.models.execution import Execution
from app.models.api_log import APILog
from app.models.webhook import WebhookLog
# -------------------------------------------------------------
from app.routes import auth #IMPORTING ROUTES
from app.routes import agent
from app.routes import webhook
from app.routes import calls

# --------------------------------------------------------------

app = FastAPI(title="Voice AI SaaS Platform")

# ----------------------------------------------------------------

# TABLE CREATE
Base.metadata.create_all(bind=engine)

# -----------------------------------------------------------------


app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(agent.router, prefix="/agent", tags = ["Agents"])
app.include_router(webhook.router, prefix="/webhook", tags=["Webhook"])
app.include_router(calls.router, prefix="/calls", tags = ["Calls"])

# ----------------------------------------------------------------------

@app.get("/")
def home():
    return {"message": "Voice AI backend running"}
