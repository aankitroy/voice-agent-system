# We bring in the usual SQLAlchemy building blocks.
# Interestingly, you imported 'JSON' here, but didn't actually use it below!
# I'll point out exactly where it might come in handy in just a second.
from sqlalchemy import Column, String, DateTime, JSON

# Postgres-specific UUIDs are the gold standard for primary keys. They are fast and globally unique.
from sqlalchemy.dialects.postgresql import UUID, JSONB

# Python's built-in tool to actually generate those random UUID strings.
import uuid

# Timezone-aware datetimes are an absolute must for logging.
# When a bug happens at 3 AM, you need to know exactly when it occurred without mental timezone math.
from datetime import datetime, timezone

# Grabbing our declarative base so SQLAlchemy knows to hook this class up to the database.
from app.db import Base


# Our APILog model. Every row in this table represents one conversation with an external API.
class APILog(Base):
    
    # The physical table name in your Postgres database.
    __tablename__ = "api_logs"

    # Our standard primary key setup. It automatically generates a unique UUID for every new log entry.
    id = Column(UUID(as_uuid=True), primary_key=True, default= uuid.uuid4)
    
    # Who are we talking to? Your comment "bolna/ future-engine" is perfect.
    # Having this column makes it super easy to filter the database later if a specific vendor goes offline.
    provider = Column(String) 
    
    # The exact URL path we hit (e.g., "/v1/agents/create").
    endpoint = Column(String)
    
    # Was it a GET request? A POST? A DELETE? 
    method = Column(String)
    
    # The payload we sent to the external API.
    # Pro-tip: Since you imported 'JSON' at the top, you might want to change this from 'String' 
    # to 'JSON' (or 'JSONB' for Postgres). Storing it as a true JSON type allows you to run SQL queries 
    # to search *inside* the payload later!
    request_json = Column(JSONB)
    
    # What the API sent back to us. Same tip applies here—storing as JSON is incredibly powerful for debugging.
    response_json = Column(JSONB)
    
    # Did it succeed (200 OK) or crash (500 Internal Server Error)?
    # You've got it as a String here, which is fine, but using an Integer (e.g., Column(Integer)) 
    # is usually better for status codes so you can easily query things like `status_code >= 400` to find all errors.
    status_code = Column(String)
    
    # The exact moment the request happened.
    # Just a tiny heads up on naming conventions: you have a capital 'A' in 'created_At'.
    # Standard Python practice (PEP 8) is all lowercase ('created_at'), but it'll work perfectly fine as-is!
    created_at = Column(DateTime, default= lambda: datetime.now(timezone.utc))

    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))