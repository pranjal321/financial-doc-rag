from sqlalchemy.orm import Session
from app import models


def save_document(db: Session, title, company_name, document_type, file_path, user):
    new_doc = models.Document(
        title=title,
        company_name=company_name,
        document_type=document_type,
        file_path=file_path,
        uploaded_by=user.id  
    )

    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    return new_doc