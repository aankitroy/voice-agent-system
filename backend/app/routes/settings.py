from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.utils.dependencies import get_current_user
from app.schemas.settings_schema import UpdatePasswordSchema, UpdateWorkspaceSchema, UpdateLLMSchema
from app.utils.security import verify_password, hash_password
from app.models.workspace import Workspace
router = APIRouter()



@router.get("/me")
def get_profile(current_user = Depends(get_current_user)):
    return{
        "email": current_user.email,
        "workspace_id": current_user.workspace_id
    }

@router.post("/change-password")
def change_password(payload: UpdatePasswordSchema,
                    db: Session = Depends(get_db),
                    current_user = Depends(get_current_user)):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail='Current password is incorrect')
    
    current_user.hashed_password = hash_password(payload.new_password)
    db.commit()

    return {"message": "Password updated"}

@router.get("/workspace")
def get_workspace(db:Session = Depends(get_db),
                  current_user = Depends(get_current_user)
                  ):
    workspace = db.query(Workspace).filter(
        Workspace.id == current_user.workspace_id
    ).first()
    return workspace

@router.post("/workspace")
def change_workspace(payload: UpdateWorkspaceSchema,
                     db: Session = Depends(get_db),
                     current_user = Depends(get_current_user)
                     ):
    workspace = db.query(Workspace).filter(
        Workspace.id == current_user.workspace_id
    ).first()
    workspace.name = payload.workspace_name
    db.commit()
    return {"message": "workspace name updated"}

