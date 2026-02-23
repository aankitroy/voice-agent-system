# We're bringing in 'ForeignKey' this time.
# This is essential because this specific table is all about linking data from two other tables.
from sqlalchemy import Column, String, DateTime, ForeignKey

# Again, using the Postgres-specific UUID type so the database handles IDs efficiently.
from sqlalchemy.dialects.postgresql import UUID

# The Python tool to generate those random ID strings.
import uuid

# Standard time imports. We need 'timezone' to ensure we stick to UTC and avoid timezone headaches later.
from datetime import datetime, timezone

# Importing the parent class that connects this file to our app's database registry.
from app.db import Base


# This class acts as the middleman between Users and Workspaces.
# In database terms, this creates a "Many-to-Many" relationship (one user can be in many workspaces, and vice versa).
class WorkspaceMember(Base):
    
    # Naming the table in the database. 
    # Plural "members" is standard since it holds multiple records.
    __tablename__ = "workspace_members"

    # Even though this is a linking table, it's good practice to give each row its own unique ID.
    # It makes it easier to reference or delete a specific membership record later.
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # This is the first half of the link.
    # ForeignKey("workspaces.id") tells the database: "Make sure this ID actually exists in the 'workspaces' table."
    # If you try to add a member to a non-existent workspace, the DB will yell at you.
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"))

    # This is the second half of the link.
    # It connects a specific row in the "users" table to this membership.
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # We need to know *what* this user is allowed to do in this specific workspace.
    # defaulting to "member" is safer than "admin"—always give the lowest permissions by default.
    role = Column(String, default="member")

    # The audit trail. 
    # As with the User model, the 'lambda' function is critical here.
    # It ensures the timestamp is generated exactly when the user is added to the workspace, not when the app boots up.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))