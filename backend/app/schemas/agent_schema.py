from pydantic import BaseModel
from typing import Optional


class LLMConfig(BaseModel):
    provider:str
    model: str
    max_tokens: int
    temprature: float


class AgentCreateSchema(BaseModel):
    agent_config: dict
    agent_prompts: dict