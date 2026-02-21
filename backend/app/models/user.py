# First, we grab the basic building blocks from SQLAlchemy to define our table structure.
# Column is for the field itself; String/DateTime are the data types.
from sqlalchemy import Column, String, DateTime, ForeignKey

# Since we are using a PostgreSQL database, we import their specific UUID type.
# This is much faster and more efficient than storing IDs as standard text strings.
from sqlalchemy.dialects.postgresql import UUID

# This is Python's built-in tool for generating unique IDs. 
# We need this to actually create the random numbers for our primary keys.
import uuid

# We need datetime and timezone to handle timestamps correctly. 
# Using timezone-aware dates is a best practice so we don't get confused by server locations.
from datetime import datetime, timezone

# Importing 'Base' from our local project configuration. 
# This is the parent class that connects this model to our specific database setup.
from app.db import Base


# Here we define the User model. 
# Inheriting from (Base) tells SQLAlchemy: "Hey, map this class to a real database table."
class User(Base):
    
    # This explicitly tells the database to name the table "users".
    # If we didn't do this, SQLAlchemy might try to guess the name based on the class name.
    __tablename__ = "users"

    # This is our Primary Key.
    # - UUID(as_uuid=True): We tell Python to handle this as a real UUID object, not a string.
    # - default=uuid.uuid4: This is crucial. It means if we don't provide an ID, Python generates a random one automatically.
    id = Column(UUID(as_uuid=True), primary_key= True, default=uuid.uuid4)

    # The email field.
    # - unique=True: The database will throw an error if someone tries to sign up with an email that already exists.
    # - nullable=True: This allows the email to be empty. Useful if you have "guest" users or phone-number-only logins.
    email = Column(String, unique= True, nullable=True)

    # We store the *hashed* version of the password here, never the plain text.
    # - nullable=False: A user absolutely must have a password to exist in this system.
    hashed_password = Column(String, nullable= False)

    # This handles permissions. 
    # We set the default to "user" so we don't accidentally create an admin account by mistake.
    role = Column(String, default="user")

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"))

    # Tracks when the user signed up.
    # NOTE: The 'lambda' function here is a pro move. 
    # If we just put `datetime.now()`, the time would be fixed to when the server started.
    # The lambda ensures the function runs fresh *every single time* a new user is added.
    created_at = Column(DateTime, default= lambda: datetime.now(timezone.utc))