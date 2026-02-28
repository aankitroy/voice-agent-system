from pydantic import BaseModel

class UpdatePasswordSchema(BaseModel):
    current_password: str
    new_password: str

class UpdateWorkspaceSchema(BaseModel):
    workspace_name: str

class UpdateLLMSchema(BaseModel):
    llm_provider: str  # "openai", "anthropic"
    llm_model: str 