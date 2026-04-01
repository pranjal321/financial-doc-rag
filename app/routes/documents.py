from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import shutil
import os

from app.database import get_db
from app import models
from app.services.dependencies import get_current_user
from app.services.document_service import save_document
from app.services.rag_service import store_embedding, remove_embedding, extract_text

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/")
def get_all_documents(db: Session = Depends(get_db), user=Depends(get_current_user)):
    docs = db.query(models.Document).all()
    return docs


@router.get("/search")
def search_documents(
    company: str = None,
    document_type: str = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(models.Document)
    if company:
        query = query.filter(models.Document.company_name.ilike(f"%{company}%"))
    if document_type:
        query = query.filter(models.Document.document_type == document_type)
    return query.all()


@router.get("/{document_id}")
def get_document(document_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ["admin", "analyst"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    remove_embedding(document_id)

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted"}


@router.post("/upload")
def upload_document(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    company_name: str = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ["admin", "analyst"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        new_doc = save_document(db, title, company_name, document_type, file_path, user)

        text = extract_text(file_path) or f"{title} {company_name} {document_type}"
        background_tasks.add_task(store_embedding, new_doc.id, text)

        return {"message": "Document uploaded", "document_id": new_doc.id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))