from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="client")  # admin, analyst, auditor, client


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    company_name = Column(String)
    document_type = Column(String)
    file_path = Column(String)
    uploaded_by = Column(Integer, ForeignKey("users.id"))  # keep as uploaded_by
    created_at = Column(DateTime, default=datetime.utcnow)