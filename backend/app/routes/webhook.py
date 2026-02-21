# We bring in 'Request' from FastAPI. This gives us direct access to the raw HTTP request 
# that the external server (Bolna) just sent to us.
from fastapi import APIRouter, Depends, Request

# Our standard database session tool.
from sqlalchemy.orm import Session

# Importing our database connection and the two tables we need to talk to.
from app.db import get_db
from app.models.execution import Execution
from app.models.webhook import WebhookLog

router = APIRouter()

# ------------------------------------------------------------------
# BOLNA WEBHOOK ENDPOINT
# ------------------------------------------------------------------
# Notice this is an 'async def'. Webhooks can hit your server incredibly fast, 
# so using async allows FastAPI to handle hundreds of incoming webhooks simultaneously 
# without locking up your server.
@router.post("/bolna")
async def bolna_webhook(request: Request, db: Session = Depends(get_db)):

    # We use 'await' here because reading the raw body of an incoming request 
    # takes a tiny fraction of a second, and we don't want to block other operations while it downloads.
    payload = await request.json()

    # 1️⃣ LOG EVERYTHING
    # The moment the data arrives, we drop it into our "Inbox" table.
    log = WebhookLog(
        # We don't know the workspace ID yet, but we can update this later if needed.
        workspace_id=None,  
        
        # We label it so we know where this webhook came from.
        event_type="bolna_event",
        
        # We save the entire raw JSON payload. If our code crashes on step 2 or 3, 
        # we still have the full message saved safely in the database!
        payload=payload
    )
    
    db.add(log)
    db.commit()

    # 2️⃣ EXTRACT THE ID AND FIND THE MATCHING RECORD
    # Bolna might send the ID as "id" or "execution_id" depending on the event type.
    # The `.get()` method safely tries both without throwing an error.
    execution_id = payload.get("id") or payload.get("execution_id")

    # If they sent us a weird webhook with no ID, we just stop here and say we're done.
    if not execution_id:
        return {"message": "no execution id"}

    # We ask our database: "Find the Execution row that matches this Bolna ID."
    execution = db.query(Execution).filter(
        Execution.bolna_execution_id == execution_id
    ).first()

    # If the database can't find it (maybe the call was deleted, or the ID is wrong), stop here.
    if not execution:
        return {"message": "execution not found"}

    # 3️⃣ UPDATE THE EXECUTION FIELDS
    # We grab the new data Bolna sent us. 
    # The second argument in `.get("status", execution.status)` is a brilliant fallback: 
    # it means "If Bolna didn't send a status, just keep the old status we already had in the database."
    execution.status = payload.get("status", execution.status)
    execution.duration = payload.get("conversation_time", execution.duration)
    execution.cost = payload.get("total_cost", execution.cost)
    execution.transcript = payload.get("transcript", execution.transcript)

    # Sometimes recordings are nested inside a 'telephony_data' dictionary.
    # We safely check if that dictionary exists before trying to grab the URL inside it.
    telephony = payload.get("telephony_data")
    if telephony:
        execution.recording_url = telephony.get("recording_url")

    # Finally, we update the raw_json in the Execution table to reflect the most recent state.
    execution.raw_json = payload

    # We save all these updates to the database.
    db.commit()

    # We return a standard 200 OK message to Bolna so they know we received the webhook.
    # If we didn't return anything, Bolna might assume we crashed and try sending the webhook again!
    return {"message": "updated"}