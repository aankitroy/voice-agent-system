from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.agent import Agent
from app.models.knowledge_base import KnowledgeBase
from app.services.bolna_client import BolnaClient
from app.schemas.agent_schema import AgentCreateSchema
from app.config.bolna_config import get_bolna_payload
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.get("/list")
def list_agents(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    agents = db.query(Agent).filter(
        Agent.workspace_id == current_user.workspace_id
    ).all()
    return agents


@router.post("/create")
def create_agent(
    payload: AgentCreateSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    agent_name = payload.agent_config.get("agent_name")

    if not agent_name:
        raise HTTPException(status_code=400, detail="agent_name missing in payload")

    agent = Agent(
        name=agent_name,
        config_json=payload.model_dump(),
        workspace_id=current_user.workspace_id,
        status="draft"
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    try:
        # KB vector_id fetch karo
        rag_config = payload.agent_config.get("rag_config")
        vector_id = None

        if rag_config:
            kb = db.query(KnowledgeBase).filter(
                KnowledgeBase.rag_id == rag_config.get("rag_id")
            ).first()
            if kb:
                vector_id = kb.vector_id

        bolna_payload = get_bolna_payload(payload.agent_config, payload.agent_prompts, vector_id)

        bolna = BolnaClient(db)
        response = bolna.post("/v2/agent", bolna_payload)

        if not response or "agent_id" not in response:
            raise HTTPException(status_code=502, detail="Invalid response from Bolna")

        agent.bolna_agent_id = response["agent_id"]
        agent.status = "active"
        db.commit()
        db.refresh(agent)

        return agent

    except Exception as e:
        agent.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Agent creation failed: {str(e)}")

@router.get("/{agent_id}")
def get_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.workspace_id == current_user.workspace_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent

@router.put("/{agent_id}")
def update_agent(
    agent_id: str,
    payload: AgentCreateSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.workspace_id == current_user.workspace_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if not agent.bolna_agent_id:
        raise HTTPException(status_code=400, detail="Agent not deployed to Bolna")

    try:
        # KB vector_id fetch karo
        rag_config = payload.agent_config.get("rag_config")
        vector_id = None

        if rag_config:
            kb = db.query(KnowledgeBase).filter(
                KnowledgeBase.rag_id == rag_config.get("rag_id")
            ).first()
            if kb:
                vector_id = kb.vector_id

        bolna_payload = get_bolna_payload(payload.agent_config, payload.agent_prompts, vector_id)


        bolna = BolnaClient(db)
        response = bolna.put(f"/v2/agent/{agent.bolna_agent_id}", bolna_payload)

        print(response)

        # Local database update karo
        agent.name = payload.agent_config.get("agent_name")
        agent.config_json = payload.model_dump()
        db.commit()
        db.refresh(agent)

        return agent

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


@router.post("/{agent_id}/set-inbound")
def set_inbound(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.workspace_id == current_user.workspace_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if not agent.bolna_agent_id:
        raise HTTPException(status_code=400, detail="Agent not deployed to Bolna")

    bolna = BolnaClient(db)
    response = bolna.post("/inbound/setup", {
        "agent_id": agent.bolna_agent_id
    })

    return response