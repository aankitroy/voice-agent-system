from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

from datetime import datetime, timezone
from app.db import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"))

    name = Column(String)
    config_json = Column(JSON)
    bolna_agent_id = Column(String)
    status = Column(String, default="draft")

    created_at = Column(DateTime, default= lambda: datetime.now(timezone.utc))

    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))