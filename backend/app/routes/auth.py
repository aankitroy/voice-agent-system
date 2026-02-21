# Bringing in the heavy hitters from FastAPI.
# - APIRouter: Lets us split our routes into multiple files so our main.py doesn't become 5,000 lines long.
# - Depends: FastAPI's magic wand for "Dependency Injection" (we use it to hand a database connection to the route).
# - HTTPException: How we cleanly throw errors (like a 400 Bad Request) back to the frontend.
from fastapi import APIRouter, Depends, HTTPException

# This is the SQLAlchemy session. It's the actual "conversation" we are having with the database.
from sqlalchemy.orm import Session

# Importing all the tools we built in the previous steps.
from app.db import get_db
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.schemas.auth_schema import SignupSchema, LoginSchema
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token

# We create a router instance here. We will plug this into the main FastAPI app later.
router = APIRouter()

# ------------------------------------------------------------------
# SIGNUP ENDPOINT
# ------------------------------------------------------------------
# We use a POST request because we are sending sensitive data in the request body, not the URL.
@router.post("/signup")
def signup(data: SignupSchema, db:Session = Depends(get_db)):
    # First rule of signup: check if they already exist!
    # (Note: I see you used 'data.email' here—make sure you fixed that 'emails' typo in your Pydantic schema!)
    existing_user = db.query(User).filter(User.email == data.email).first()
    
    # If we find a user, slam the brakes and return a 400 error.
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Let's build the new user object in memory.
    new_user = User(
        email = data.email,
        # CRITICAL: We pass the raw password through our hasher BEFORE it ever touches the database object.
        hashed_password = hash_password(data.password),
        role = "owner" # Hardcoding owner here since they are creating a brand new workspace.
    )

    # The standard SQLAlchemy dance: add to the staging area, commit to the database, and refresh.
    # We HAVE to refresh here so SQLAlchemy populates 'new_user.id' with the UUID the database just generated.
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Now that we have a real user ID, let's build their workspace.
    workspace = Workspace(
        name = data.workspace_name,
        owner_user_id = new_user.id
    )

    # Same dance to save the workspace and grab its newly minted ID.
    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    # Finally, we glue the user and the workspace together in the join table.
    member = WorkspaceMember(
        workspace_id = workspace.id,
        user_id = new_user.id,
        role = "owner"
    )

    # We don't need to refresh here because we don't immediately need the member's ID for anything else.
    db.add(member)
    db.commit()

    # The user just gave us all their info, so let's do them a solid and log them in automatically.
    # We cast the UUID to a string because JWTs only transport text, not complex Python objects.
    token = create_access_token({"user_id": str(new_user.id)})

    # Hand the token back to the frontend. They'll save this in local storage or a cookie.
    return {"access_token": token}


# ------------------------------------------------------------------
# LOGIN ENDPOINT
# ------------------------------------------------------------------
@router.post("/login")
def login(data: LoginSchema, db:Session = Depends(get_db)):
    # Step 1: Try to find the user by their email.
    user = db.query(User).filter(User.email == data.email).first()

    # Security best practice right here: 
    # If the user doesn't exist, we just say "Invalid credentials". 
    # We NEVER say "User not found" because hackers could use that to check which emails are registered.
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Step 2: User exists, now check if the password matches the hash.
    # Notice we use the exact same vague "Invalid credentials" error message if they get the password wrong.
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # If they passed both checks, they are legit. Mint them a fresh token.
    token = create_access_token({"user_id": str(user.id)})

    # Send it back!
    return {"access_token": token}