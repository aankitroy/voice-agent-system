# We're bringing in APIRouter and Depends for routing and dependency injection.
from fastapi import APIRouter, Depends

# Session is needed for our database connection type hint so the IDE helps us out.
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.agent import Agent
from app.services.bolna_client import BolnaClient

# Our new security bouncer! This ensures only logged-in users can hit this endpoint.
from app.utils.dependencies import get_current_user

router = APIRouter()


# ------------------------------------------------------------------
# CREATE AGENT ENDPOINT (DRAFT & PUBLISH PATTERN)
# ------------------------------------------------------------------
@router.post("/create")
def create_agent(
    payload: dict,
    db: Session = Depends(get_db),
    # By adding this dependency, FastAPI automatically intercepts the request, 
    # verifies the JWT token, and hands us the fully loaded User object right here.
    current_user = Depends(get_current_user)
):
    # Safely extracting the agent name. Using .get() prevents nasty KeyError crashes 
    # if the frontend accidentally sends an incomplete or empty payload.
    agent_name = payload.get("agent_config", {}).get("agent_name")

    if not agent_name:
        # PRO-TIP: Throwing a raw Exception works, but raising an HTTPException(status_code=400) 
        # is usually better here so the frontend gets a clean, standard JSON error response!
        raise Exception("agent_name missing in payload")

    # 1️⃣ SAVE THE DRAFT FIRST
    # This is a brilliant safety net. We save their configuration locally *before* we talk to Bolna.
    agent = Agent(
        name=agent_name,
        config_json=payload,
        
        # We automatically link this agent to the current user's workspace using their token.
        # This prevents "Insecure Direct Object Reference" (IDOR) vulnerabilities where hackers 
        # try to create agents in other people's workspaces.
        workspace_id=current_user.workspace_id,
        
        # It starts its life as a draft.
        status="draft" 
    )

    # Standard SQLAlchemy dance to get our local UUID generated.
    db.add(agent)
    db.commit()
    db.refresh(agent)

    try:
        # 2️⃣ SAFELY BUILD THE EXTERNAL PAYLOAD
        # We construct exactly what Bolna expects. This sanitizes the data so we aren't 
        # blindly passing everything the frontend gave us to a third-party server.
        bolna_payload = {
            "agent_config": payload.get("agent_config"),
            "agent_prompts": payload.get("agent_prompts", {})
        }

        # Fire up our custom client wrapper and make the POST request.
        bolna = BolnaClient(db)
        response = bolna.post("/v2/agent", bolna_payload)

        # Defensive programming! Always assume the external API might send back garbage, 
        # change their response shape without telling you, or return a weird HTML error page.
        if not response or "agent_id" not in response:
            raise Exception("Invalid response from Bolna")

        # 3️⃣ UPDATE TO SUCCESS
        # We got the green light from Bolna. We save their ID and upgrade our local record.
        agent.bolna_agent_id = response["agent_id"]
        agent.status = "active"

        # We don't need to do db.add() again because SQLAlchemy is already tracking this 'agent' object in memory.
        db.commit()
        db.refresh(agent)

        return agent

    except Exception as e:
        # 4️⃣ GRACEFUL FAILURE
        # If absolutely anything goes wrong during the Bolna call (timeout, network drop, bad API key),
        # we catch it here. We update our local database to reflect the failure so it isn't stuck as a "draft".
        agent.status = "failed"
        db.commit()

        # We re-raise the error so the frontend knows exactly why it failed and can show a toast notification.
        raise Exception(f"Agent creation failed: {str(e)}")