# We're bringing in our standard SQLAlchemy toolkit.
# We're adding 'Float' for tracking money and time, and 'JSON' which is the MVP of this table.
from sqlalchemy import Column, String, Float, DateTime, JSON

# Postgres-specific UUIDs are heavily preferred here. 
# They index much faster than standard strings, which is crucial because an active 
# calling agent will generate *a lot* of rows in this table very quickly.
from sqlalchemy.dialects.postgresql import UUID

# Standard time and unique ID utilities.
from datetime import datetime
import uuid

# Bringing in our SQLAlchemy declarative base.
from app.db import Base


# We define the Execution model. Think of this as the "Receipts" table. 
# Every time Bolna makes or receives a call, a row goes here.
class Execution(Base):
    
    # Plural naming convention for the database table.
    __tablename__ = "executions"

    # This is OUR internal ID for the database row. 
    # It's important to keep our own ID separate from Bolna's ID so we control the primary key.
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ---------------------------------------------------------
    # RELATIONSHIPS
    # ---------------------------------------------------------
    # These link the call back to the workspace that pays for it and the agent that made it.
    # 💡 PRO-TIP: You currently just have these as standard UUID columns. If you are using 
    # Postgres, it is highly recommended to wrap these in a ForeignKey (e.g., ForeignKey("workspaces.id"))
    # so the database enforces referential integrity and prevents "orphaned" executions.
    workspace_id = Column(UUID(as_uuid=True))
    agent_id = Column(UUID(as_uuid=True))

    # This is the unique ID that *Bolna* generates for the call.
    # We save this so when Bolna sends us a webhook later saying "Call completed," 
    # we can query `Execution.bolna_execution_id == incoming_id` to update the right row.
    bolna_execution_id = Column(String)

    # ---------------------------------------------------------
    # CALL METADATA
    # ---------------------------------------------------------
    # Who picked up the phone, and what number did the AI dial from?
    # Storing these as Strings is best practice because phone numbers often include 
    # '+' signs, country codes, or leading zeros that Integer columns would destroy.
    recipient_number = Column(String)
    from_number = Column(String)

    # Tracks the current state (e.g., "queued", "in-progress", "completed", "failed").
    status = Column(String)

    # ---------------------------------------------------------
    # BILLING & METRICS
    # ---------------------------------------------------------
    # We use Float here because telephony is usually billed in fractions of a cent, 
    # and call duration often includes milliseconds (e.g., 45.5 seconds).
    cost = Column(Float, default=0)
    duration = Column(Float)

    # ---------------------------------------------------------
    # CALL CONTENT
    # ---------------------------------------------------------
    # The actual text of what was said during the call. 
    # Having this directly in the database is great for building a UI where users can read past calls.
    transcript = Column(String)
    
    # A link to the AWS S3 bucket (or similar) where the raw audio is stored.
    recording_url = Column(String)

    # ---------------------------------------------------------
    # THE LIFESAVER COLUMN
    # ---------------------------------------------------------
    # This JSON column is where you dump the *entire* raw webhook payload Bolna sends you.
    # Why? Because external APIs change. If Bolna adds a new field tomorrow (like "extracted_data") 
    # or if your parsing logic breaks, you won't lose the data. You can always go back and read the raw_json.
    raw_json = Column(JSON)

    # ---------------------------------------------------------
    # AUDIT TRAIL
    # ---------------------------------------------------------
    # Automatically stamps exactly when this execution was logged.
    # 💡 PRO-TIP: `datetime.utcnow` is technically deprecated in newer versions of Python (3.12+).
    # You might want to swap this to `lambda: datetime.now(timezone.utc)` just like you 
    # brilliantly did in your previous models!
    created_at = Column(DateTime, default=datetime.utcnow)