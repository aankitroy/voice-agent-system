from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.workspace_credits import WorkspaceCredits
from app.utils.dependencies import get_current_user


router = APIRouter()

@router.get("/balance")
def get_balance(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    credits = db.query(WorkspaceCredits).filter(
        WorkspaceCredits.workspace_id == current_user.workspace_id
    ).first()

    if not credits:
        return {
            "credits": 0.0,
            "total_added": 0.0,
            "total_used": 0.0
        }
    
    return credits

@router.post("/add")
def add_credits(
    amount: float,
    db:Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    credits = db.query(WorkspaceCredits).filter(
        WorkspaceCredits.workspace_id == current_user.workspace_id
    ).first()

    if not credits:
        credits = WorkspaceCredits(
            workspace_id = current_user.workspace_id,
            credits = amount,
            total_added = amount
        )
        db.add(credits)
    else:
        credits.credits += amount
        credits.total_added += amount
    
    db.commit()
    db.refresh(credits)
    return credits