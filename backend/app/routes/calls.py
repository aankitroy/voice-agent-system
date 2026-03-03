from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from app.db import get_db
from app.models.execution import Execution
from app.models.agent import Agent
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


@router.post("/make-call") # not hyphen call
def make_call(
    payload: MakeCallSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    agent = db.query(Agent).filter(
        Agent.id == payload.agent_id,
        Agent.workspace_id == current_user.workspace_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if not agent.bolna_agent_id:
        raise HTTPException(status_code=400, detail="Agent not deployed to Bolna")

    bolna_payload = {
        "agent_id": agent.bolna_agent_id,
        "recipient_phone_number": payload.to_number,
        "from_phone_number": FROM_NUMBER
    }

    bolna = BolnaClient(db)
    response = bolna.post("/call", bolna_payload)

    if not response:
        raise HTTPException(status_code=502, detail="Call failed")

    execution_id = response.get("execution_id")

    execution = Execution(
        workspace_id=current_user.workspace_id,
        agent_id=agent.id,
        bolna_execution_id=execution_id,
        recipient_number=payload.to_number,
        from_number=FROM_NUMBER,
        status=response.get("status"),
        raw_json=response
    )

    db.add(execution)
    db.commit()
    db.refresh(execution)

    return execution