from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.knowledge_base import KnowledgeBase
from app.utils.dependencies import get_current_user
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
BOLNA_API_KEY = os.getenv("BOLNA_API_KEY")
BOLNA_BASE_URL = os.getenv("BOLNA_BASE_URL")

router = APIRouter()

@router.get("/list")
def list_knowledge_bases(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    kbs = db.query(KnowledgeBase).filter(
        KnowledgeBase.workspace_id == current_user.workspace_id
    ).all()
    return kbs

@router.post("/upload")
async def upload_knowledge_base(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    file_content = await file.read()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BOLNA_BASE_URL}/knowledgebase",
            headers={"Authorization": f"Bearer {BOLNA_API_KEY}"},
            files={"file": (file.filename, file_content, file.content_type)},
            data={"chunk_size": 512, "similarity_top_k": 15, "overlapping": 128}
        )
    
    bolna_data = response.json()
    bolna_data = response.json()
    print("BOLNA KB RESPONSE:", bolna_data)

    kb = KnowledgeBase(
        workspace_id=current_user.workspace_id,
        file_name=file.filename,
        rag_id=bolna_data.get("rag_id"),
        status=bolna_data.get("status", "processing")
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)

    return kb

@router.delete("/{rag_id}")
async def delete_knowledge_base(
    rag_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    async with httpx.AsyncClient() as client:
        await client.delete(
            f"{BOLNA_BASE_URL}/knowledgebase/{rag_id}",
            headers={"Authorization": f"Bearer {BOLNA_API_KEY}"}
        )

    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.rag_id == rag_id,
        KnowledgeBase.workspace_id == current_user.workspace_id
    ).first()
    
    if kb:
        db.delete(kb)
        db.commit()

    return {"message": "Deleted"}


@router.get("/sync-status")
async def sync_status(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    kbs = db.query(KnowledgeBase).filter(
        KnowledgeBase.workspace_id == current_user.workspace_id,
        KnowledgeBase.status == 'processing'
    ).all()

    async with httpx.AsyncClient() as client:
        for kb in kbs:
            response = await client.get(
                f"{BOLNA_BASE_URL}/knowledgebase/{kb.rag_id}",
                headers= {"Authorization": f"Bearer {BOLNA_API_KEY}"}
            )
            data = response.json()
            kb.status = data.get("status", kb.status)
            kb.vector_id = data.get("vector_id")
    db.commit()
    return {"message": "synced"}