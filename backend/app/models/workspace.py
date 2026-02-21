# Import specific utilities from the SQLAlchemy library to define database columns.
# Column: a new column in table
# String: a text-based datatype
# Datetime: a datatype for dates and times
# Float: a numeric data type for numbers with decimals

from sqlalchemy import Column, String, DateTime, Float


# import the UUID type specifically for postgres database
# allows the database to use its native, efficient UUID format rather than storing it as standard text
from sqlalchemy.dialects.postgresql import UUID

# import python's build in uuid library
# need this to generate unique identifiers (UUIDs) for our database records.
import uuid

# import the datetime class from python's built in datetime module
# this is used to capture the current moment in time (timestamps)
from datetime import datetime, timezone

# import the base class from local file located at app/db.py
# Base is the parent class provided by sqlalchemy that maintains a catalog of classes and tables
# relative to that base. all of the models must inherit from this
from app.db import Base



# Define a class named 'Workspace' that inherits from 'Base'.
# This class creates a "Model," which maps this Python class to a specific database table.
class Workspace(Base):
    
    # This special variable tells SQLAlchemy the specific name of the table in the database.
    # When the database is created, a table named "workspaces" will be generated.
    __tablename__ = "workspaces"

    # Define the 'id' column, which is the unique identifier for every row in this table.
    # - UUID(as_uuid=True): Sets the type to UUID. 'as_uuid=True' ensures Python handles it as a UUID object, not a string.
    # - primary_key=True: Marks this column as the primary key, meaning it is the main unique index for searching.
    # - default=uuid.uuid4: If no ID is provided when creating a row, Python will automatically generate a new random UUID.
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Define the 'name' column to hold the name of the workspace.
    # - String: Sets the column type to text.
    # - nullable=True: Allows this column to be empty (NULL) in the database. 
    name = Column(String, nullable=True)

    # Define the 'owner_user_id' column to store the ID of the user who owns this workspace.
    # - UUID(as_uuid=True): Uses the UUID type to match the format of User IDs (assuming Users also use UUIDs).
    # This links this workspace to a specific user.
    owner_user_id = Column(UUID(as_uuid=True))

    # Define the 'wallet_balance' column to store money or credits.
    # - Float: Sets the type to a number that allows decimals (e.g., 10.50).
    # - default=0: If no balance is specified, it starts at 0.
    wallet_balance = Column(Float, default=0)

    # Define the 'created_at' column to store when the workspace was made.
    # - DateTime: Sets the type to store date and time.
    # - default=...: Sets the default value to the current time using UTC timezone.
    # NOTE: In Python, passing the function call `datetime.now()` executes it immediately when the app starts. 
    # To ensure it captures the time *when the row is inserted*, it is often better to pass the function itself 
    # without parentheses (e.g., default=datetime.utcnow) or use `server_default`.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
