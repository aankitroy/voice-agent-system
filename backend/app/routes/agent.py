from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.agent import Agent
from app.models.knowledge_base import KnowledgeBase
from app.services.bolna_client import BolnaClient
from app.schemas.agent_schema import AgentCreateSchema
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

        bolna_payload = {
            "agent_config": {
                "agent_name": payload.agent_config.get("agent_name"),
                "agent_type": "other",
                "agent_welcome_message": payload.agent_config.get("agent_welcome_message"),
                "tasks": [
                    {
                        "task_type": "conversation",
                        "tools_config": {
                            "llm_agent": {
                                "agent_type": "knowledgebase_agent" if vector_id else "simple_llm_agent",
                                "agent_flow_type": "streaming",
                                "llm_config": {
                                    "provider": payload.agent_config.get("llm_provider", "openai"),
                                    "model": payload.agent_config.get("llm_model", "gpt-4.1-mini"),
                                    "max_tokens": 150,
                                    "temperature": 0.1,
                                    "agent_flow_type": "streaming",
                                    "family": payload.agent_config.get("llm_provider", "openai"),
                                    "base_url": "https://api.anthropic.com" if payload.agent_config.get("llm_provider") == "anthropic" else "https://api.openai.com/v1",
                                    **({"rag_config": {
                                        "vector_store": {
                                            "provider": "LanceDB",
                                            "provider_config": {
                                                "vector_ids": [vector_id]
                                            }
                                        }
                                    }} if vector_id else {})
                                }
                            },
                            "transcriber": {
                                "provider": "deepgram",
                                "model": "nova-3",
                                "language": payload.agent_config.get("language", "hi"),
                                "stream": True
                            },
                            "synthesizer": {
                                "provider": "elevenlabs",
                                "provider_config": {
                                    "voice": payload.agent_config.get("voice", "Nila"),
                                    "voice_id": payload.agent_config.get("voice_id", "V9LCAAi4tTlqe9JadbCo"),
                                    "model": "eleven_turbo_v2_5"
                                },
                                "stream": True
                            },
                            "input": {"provider": "plivo", "format": "wav"},
                            "output": {"provider": "plivo", "format": "wav"}
                        },
                        "toolchain": {
                            "execution": "parallel",
                            "pipelines": [["transcriber", "llm", "synthesizer"]]
                        },
                        "task_config": {
                            "hangup_after_silence": 10,
                            "call_terminate": 90
                        }
                    }
                ]
            },
            "agent_prompts": payload.agent_prompts
        }

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