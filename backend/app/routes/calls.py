# Bringing in the tools we need to create the web route and connect to the database.
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Importing our database connection, our models (tables), and our custom Bolna helper.
from app.db import get_db
from app.models.execution import Execution
from app.models.agent import Agent
from app.services.bolna_client import BolnaClient

# Our security bouncer that ensures only logged-in users can trigger a call.
from app.utils.dependencies import get_current_user

# Creating the router so we can add this endpoint to our main app later.
router = APIRouter()


# This is a POST request because triggering a call is an "action" that creates new data.
@router.post("/make")
def make_call(
    agent_id: str,
    to_number: str,
    from_number: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) # 🔒 Security: Grabs the user making the request.
):

    # 1️⃣ FETCH AND VERIFY THE AGENT
    # We ask the database: "Find the agent with this ID, BUT only if it belongs to this user's workspace."
    # This is a crucial security check so users can't make calls using someone else's agent!
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.workspace_id == current_user.workspace_id
    ).first()

    # If the database comes up empty, we stop everything and throw an error.
    if not agent:
        raise Exception("Agent not found")

    # If the agent exists locally but was never successfully sent to Bolna, it can't make calls.
    if not agent.bolna_agent_id:
        raise Exception("Agent not deployed to Bolna")

    # 2️⃣ PREPARE AND MAKE THE BOLNA CALL
    # We build the exact dictionary (JSON) that Bolna expects to receive.
    # Notice we use the 'bolna_agent_id', not our local database ID.
    bolna_payload = {
        "agent_id": agent.bolna_agent_id,
        "recipient_phone_number": to_number,
        "from_phone_number": from_number
    }

    # We hand the payload to our custom client and tell it to hit the "/call" endpoint.
    bolna = BolnaClient(db)
    response = bolna.post("/call", bolna_payload)

    # If Bolna's servers are down or reject the call, we stop here.
    if not response:
        raise Exception("Call failed")

    # Bolna will send back a unique ID for this specific phone call. We grab it here.
    execution_id = response.get("execution_id")

    # 3️⃣ SAVE THE RECEIPT LOCALLY
    # The call has been triggered! Now we create a record in our database so we can track it.
    execution = Execution(
        workspace_id=current_user.workspace_id,
        agent_id=agent.id,
        bolna_execution_id=execution_id,
        recipient_number=to_number,
        from_number=from_number,
        # We save whatever status Bolna gave us (probably "queued" or "in-progress" right now).
        status=response.get("status"), 
        # We save the entire raw response just in case we need to debug it later.
        raw_json=response 
    )

    # We save the new execution record to our database.
    db.add(execution)
    db.commit()
    db.refresh(execution)

    # Finally, we return the saved record back to the frontend so the user can see it processing!
    return execution