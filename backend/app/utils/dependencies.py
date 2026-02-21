# 'Depends' is FastAPI's secret weapon for Dependency Injection. We use it to tell FastAPI:
# "Before you run the route, run this function first and give me the result."
# We also bring in 'HTTPException' to neatly throw standard web errors (like a 401 Unauthorized).
from fastapi import Depends, HTTPException

# Type hinting the database session. This makes our IDE's autocomplete actually work 
# when we start typing 'db.query()'.
from sqlalchemy.orm import Session

# Importing the function that actually opens the connection to our PostgreSQL database.
from app.db import get_db

# We need the User model so we can query the 'users' table.
from app.models.user import User


# This is our dependency function. Any route that includes `Depends(get_current_user)` 
# will force FastAPI to run this block of code before the route itself even executes.
# The `-> User` part is just a type hint telling other developers (and our IDE) 
# that this function will always hand back a full SQLAlchemy User object.
def get_current_user(db: Session = Depends(get_db)) -> User:
    """
    TEMP current user getter.
    Later replace with JWT authentication.
    """

    # 🚨 HACK ALERT: This is the temporary part! 
    # Instead of actually reading a token from the request headers, we are just blindly 
    # asking the database for the very first user it finds in the table. 
    # Great for quick local testing, terrible for production!
    user = db.query(User).first()

    # Even in a mock function, it's good to have basic error handling.
    # If the database is completely empty (maybe we just wiped it), we block the request.
    if not user:
        # 401 is the universal HTTP status code for "You are not authenticated."
        raise HTTPException(status_code=401, detail="User not found")

    # We return the raw SQLAlchemy User object. 
    # This gets injected straight into our route (like the /create agent route we wrote earlier), 
    # giving that route instant access to things like `current_user.id` and `current_user.workspace_id`.
    return user