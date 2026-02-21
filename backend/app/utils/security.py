# We're grabbing CryptContext from the passlib library.
# Instead of us trying to write our own cryptography (which is almost always a bad idea),
# this tool handles all the complex, secure hashing logic for us.
from passlib.context import CryptContext

# Here we set up our hashing configuration. 
# - schemes=["bcrypt"]: We are explicitly telling it to use bcrypt. It's an industry-standard, 
#   battle-tested algorithm for passwords that is intentionally slow to prevent brute-force attacks.
# - deprecated="auto": This is a really smart feature. If we ever decide to upgrade to a newer 
#   algorithm later (like Argon2), passlib will automatically flag old bcrypt hashes so we can 
#   silently upgrade them the next time the user logs in.
pwd_context = CryptContext(schemes=["bcrypt"],
                            deprecated="auto",
                            bcrypt__rounds = 12)


# A clean little helper function for when a user signs up or resets their password.
# We enforce type hinting (password: str) so our IDE helps us catch bugs early.
def hash_password(password: str):
    # We hand the raw, plain-text password to passlib. 
    # Under the hood, it automatically generates a random "salt", mixes it with the password, 
    # hashes it, and returns a single, safe string that we can save to the database.
    return pwd_context.hash(password)


# The helper function for your login route. 
# It takes the plain password the user just typed in, and the ugly hashed string from the database.
def verify_password(password: str, hashed: str):
    # Passlib does the heavy lifting here. It safely extracts the salt from the 'hashed' string,
    # applies it to the plain 'password', and checks if the results match.
    # Doing it this way protects against "timing attacks" where hackers try to guess passwords 
    # based on how long the server takes to respond.
    return pwd_context.verify(password, hashed)