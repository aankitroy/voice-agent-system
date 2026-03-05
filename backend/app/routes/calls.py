from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from app.db import get_db
from app.models.execution import Execution
from app.models.agent import Agent
from app.models.workspace_credits import WorkspaceCredits
from app.services.bolna_client import BolnaClient
from app.utils.dependencies import get_current_user
from app.schemas.call_schema import MakeCallSchema

load_dotenv()
FROM_NUMBER = os.getenv("FROM_NUMBER")

router = APIRouter()


@router.get("/list")
def list_calls(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    calls = db.query(Execution).filter(
        Execution.workspace_id == current_user.workspace_id
    ).order_by(Execution.created_at.desc()).all()
    return calls


 # not hyphen call
@router.post("/call")
def make_call(
    payload: MakeCallSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Credits check
    credits = db.query(WorkspaceCredits).filter(
        WorkspaceCredits.workspace_id == current_user.workspace_id
    ).first()

    if not credits or credits.credits <= 0:
        raise HTTPException(status_code=402, detail="Insufficient credits")

    # Agent fetch karo
    agent = db.query(Agent).filter(
        Agent.id == payload.agent_id,
        Agent.workspace_id == current_user.workspace_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Bolna ko call karo
    bolna = BolnaClient(db)
    response = bolna.post("/call", {
        "agent_id": agent.bolna_agent_id,
        "recipient_phone_number": payload.to_number,
        "from_phone_number": ""
    })

    # Execution save karo
    execution = Execution(
        workspace_id=current_user.workspace_id,
        agent_id=agent.id,
        bolna_execution_id=response.get("execution_id"),
        recipient_number=payload.to_number,
        status="queued",
        raw_json=response
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)

    return execution