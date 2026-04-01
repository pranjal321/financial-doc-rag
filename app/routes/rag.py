from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas import SearchQuery
from app.services.rag_service import search_similar, store_embedding, remove_embedding, extract_text
from app.services.dependencies import get_current_user

router = APIRouter()


@router.post("/index-document")
def index_document(document_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    text = extract_text(doc.file_path)
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text")

    store_embedding(doc.id, text)
    return {"message": f"Document {document_id} indexed"}


@router.delete("/remove-document/{document_id}")
def remove_document_embeddings(document_id: int, user=Depends(get_current_user)):
    remove_embedding(document_id)
    return {"message": f"Embeddings for document {document_id} removed"}


@router.post("/search")
def semantic_search(data: SearchQuery, user=Depends(get_current_user)):
    results = search_similar(data.query)
    return {"query": data.query, "results": results}


@router.get("/context/{document_id}")
def get_document_context(document_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    text = extract_text(doc.file_path)
    return {"document_id": document_id, "context": text[:1000] if text else "No content"}


@router.post("/ask")
def ask_question(data: SearchQuery, user=Depends(get_current_user)):
    results = search_similar(data.query)
    return {"question": data.query, "results": results}