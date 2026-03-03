# The classic 'requests' library! It's the absolute gold standard in Python for talking to external APIs.
import requests

# We need the SQLAlchemy session so our client can actually talk to our own database to save those logs.
from sqlalchemy.orm import Session

# Importing that beautiful APILog model we just built. 
from app.models.api_log import APILog

# Bringing in our environment variable loaders again to keep our API keys out of version control.
from dotenv import load_dotenv
import os

# Fire up the dotenv loader so it reads our .env file.
load_dotenv()

# We grab the base URL and the secret API key for Bolna right at the top.
# Setting these as global constants here makes the rest of the code much cleaner.
BOLNA_BASE_URL = os.getenv("BOLNA_BASE_URL")
BOLNA_API_KEY = os.getenv("BOLNA_API_KEY")


# ------------------------------------------------------------------
# API CLIENT / WRAPPER
# ------------------------------------------------------------------
class BolnaClient:

    # The constructor. When we create an instance of this client, we hand it our database session.
    # This ensures the client always has an open line to save its logs.
    def __init__(self, db: Session):
        self.db = db
    
    # A private helper function (indicated by the underscore '_log').
    # We don't expect the rest of our app to call this directly; it's just for internal use by the GET and POST and PUT methods.
    def _log(self, endpoint, method, request_json, response, status_code):
        # We build the log record.
        log = APILog(
            provider = "bolna", # Hardcoding the provider since this entire class is dedicated to Bolna.
            endpoint = endpoint,
            method = method,
            
            request_json = request_json,
            response_json = response, 
            
            # Pro-tip: `status_code` from the requests library is an Integer, so we cast it to a string 
            # here because your model defined it as a String.
            status_code = str(status_code) 
        )

        # Standard SQLAlchemy commit flow. 
        self.db.add(log)
        self.db.commit()
    
    # Our dedicated POST method.
    def post(self, endpoint:str, payload: dict):
        # We stitch the base URL and the specific endpoint together.
        url = f"{BOLNA_BASE_URL}{endpoint}"

        # We set up our headers. 
        # The Bearer token is how Bolna knows we're allowed to talk to them.
        headers = {
            "Authorization": f"Bearer {BOLNA_API_KEY}",
            "Content-Type": "application/json"
        }

        # The actual magical call to the external server! 
        # We pass the payload to the `json` parameter, and requests automatically serializes it for us.
        res = requests.post(url, json=payload, headers=headers, timeout=15)

        print("Bolna response status:", res.status_code)
        print("Bolna response text:", res.text)
        
        try:
            response_json = res.json()
        except Exception:
            response_json = {"raw_text": res.text}
        
        self._log(endpoint, "POST", payload, response_json, res.status_code)
        
        return response_json
    
    # Our dedicated GET method.
    def get(self, endpoint:str):
        # It should be: url = f"{BOLNA_BASE_URL}{endpoint}"
        url = f"{BOLNA_BASE_URL}{endpoint}"
        
        # Same authorization header, but GET requests don't need a Content-Type since there's no body.
        headers = {
            "Authorization": f"Bearer {BOLNA_API_KEY}"
        }

        # Firing off the GET request.
        res = requests.get(url, headers=headers, timeout=15)

        # Logging it. Since GET requests don't have a payload, passing `None` for the request_json is perfect.
        try:
            response_json = res.json()
        except Exception:
            response_json = {"raw_text": res.text}

        self._log(endpoint, "GET", None, response_json, res.status_code)
        return response_json
    
    def put(self, endpoint: str, payload: dict):
        url = f"{BOLNA_BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {BOLNA_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.put(
            url,
            json=payload,
            headers=headers,
            timeout= 15
        )
        try:
            response_json = response.json()
        except Exception:
            response_json = {"raw_text": response.text}
        self._log(endpoint, "PUT", payload, response_json, response.status_code)
        return response_json