from pydantic import BaseModel

class MakeCallSchema(BaseModel):
    agent_id: str
    to_number: str

