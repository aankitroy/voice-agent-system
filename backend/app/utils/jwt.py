# We're using 'python-jose' here. It's the industry standard for Python JWTs.
# We import JWTError even though we aren't using it yet—we'll definitely need it later when we write the code to *verify* these tokens.
from jose import JWTError, jwt

# Timedelta is the MVP here—it lets us do math with time (like "now + 30 minutes").
# We import timezone to force everything to UTC. Trust me, using local server time for tokens is a nightmare waiting to happen.
from datetime import datetime, timedelta, timezone

# These two interact with the operating system to hide our secrets.
# We never, ever want to hardcode passwords in the file where they can be accidentally pushed to GitHub.
from dotenv import load_dotenv
import os

# This line explicitly searches for a .env file and loads those variables into the app.
load_dotenv()


# Getting the expiration time.
# IMPORTANT: os.getenv always returns a String (text). 
# We wrap this in int() because the math function later will crash if we try to add a string "30" to a timestamp.
access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# This is the master key. If a hacker gets this, they can forge tokens and become any user they want.
secret_key = os.getenv("SECRET_KEY")

# Usually "HS256". It tells the code *how* to scramble the data.
algorithm = os.getenv("ALGORITHM")


# The function that actually mints the new digital ID card (Token).
# We take a dictionary 'data' which usually holds the User ID (sub).
def create_access_token(data: dict):
    
    # Crucial step: We make a shallow copy of the data first.
    # Python passes dictionaries by reference. If we didn't copy this, we might accidentally 
    # modify the original user object elsewhere in the app memory, which causes phantom bugs.
    to_encode = data.copy()

    # We set the expiration timestamp.
    # We use UTC time so it's universal. It prevents issues where a server in London creates a token 
    # that looks "expired" to a server in New York due to timezone math.
    expire = datetime.now(timezone.utc) + timedelta(minutes=access_token_expire_minutes)

    # We add the "exp" field to the payload.
    # "exp" is a reserved keyword in the JWT standard. Libraries automatically look for this key 
    # to check if the token is still valid.
    to_encode.update({"exp": expire})

    # Finally, we seal the envelope.
    # We mix the data, the secret key, and the chosen algorithm to create that long encrypted string.
    # (I filled in the missing arguments here so the code runs!)
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)