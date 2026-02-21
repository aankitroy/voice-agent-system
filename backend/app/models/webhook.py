# We're bringing in our SQLAlchemy tools. 
from sqlalchemy import Column, String, DateTime, JSON

# Postgres UUIDs for fast, secure primary keys.
from sqlalchemy.dialects.postgresql import UUID

# The built-in UUID generator.
import uuid

# Timezone-aware datetimes so we know exactly when a webhook hit our server.
from datetime import datetime, timezone

# Importing our database configuration.
from app.db import Base


# ------------------------------------------------------------------
# WEBHOOK LOG MODEL
# ------------------------------------------------------------------
# Think of this table as your "Inbox". Every time an external service (like Bolna or Stripe)
# sends an automatic message to your server, you drop a copy of it right here.
class WebhookLog(Base):
    
    # Standard plural naming for the table.
    __tablename__ = "webhook_logs"

    # Our standard, auto-generating unique ID for this specific log entry.
    id = Column(UUID(as_uuid=True), primary_key= True, default= uuid.uuid4)
    
    # Which workspace does this webhook belong to? 
    # This is helpful so if a user asks "Why didn't my call update?", you can easily 
    # search this table by their workspace_id to see if Bolna actually sent the webhook.
    workspace_id = Column(UUID(as_uuid=True))
    
    # What kind of event is this? 
    # Usually, webhooks come with an event string like "call.completed", "call.started", or "agent.failed".
    # Storing this as a string makes it super easy to filter the database later.
    event_type = Column(String)
    
    # The MVP column! We store the entire raw JSON body that the external server sent us.
    # If our code crashes while trying to read the webhook, we don't lose the data. 
    # We can just look at this column, see what they sent, and fix our code.
    payload = Column(JSON)
    
    # The exact moment the webhook hit our server.
    # 🐛 BUG ALERT: In your original code, you had `default=datetime.now(timezone.utc)`.
    # Remember from our earlier models: if you put the `()` at the end, it calculates the time 
    # exactly once when the server boots up. Every single webhook would get the exact same timestamp!
    # I added the `lambda:` keyword back in so it generates a fresh timestamp for every new row.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))