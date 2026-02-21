# We're bringing in BaseModel from Pydantic. 
# Think of Pydantic as the strict bouncer at the door of your API. 
# It looks at the incoming JSON from the frontend and says, "Does this match exactly what I expect?" 
# If it doesn't, it automatically rejects the request with a clean 422 Validation Error before the bad data can crash your app.
from pydantic import BaseModel


# This defines the exact "shape" of the data we expect when someone hits the registration endpoint.
# Inheriting from BaseModel is what gives this class all of Pydantic's validation superpowers.
class SignupSchema(BaseModel):
    
    # We expect the user's email address as a string.
    # NOTE: You might want to rename this to 'email' (singular) to match your database model!
    # Pro-tip: Pydantic actually has an 'EmailStr' type you can import if you want it to automatically 
    # check that it's a valid email format (like containing an '@' symbol), rather than just any random string.
    email: str
    
    # The raw, plain-text password coming from the frontend registration form.
    # We validate it here as a string, and then we'll pass it to our hashing function later.
    password: str
    
    # We're grabbing the name for their new workspace right at signup.
    # This is great UX—it allows us to create their User record *and* their first Workspace record 
    # all in a single API call.
    workspace_name: str


# This is the much leaner schema for when an existing user comes back to log in.
class LoginSchema(BaseModel):
    
    # Just the email they signed up with. 
    # Again, if they forget to include this in the JSON body, Pydantic immediately blocks the request.
    email: str
    
    # The plain-text password they just typed in, which we will grab and compare 
    # against the hashed password in the database using the 'verify_password' function we wrote earlier.
    password: str