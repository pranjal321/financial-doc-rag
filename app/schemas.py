from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    email: str
    password: str
    role: Optional[str] = "client"


class UserLogin(BaseModel):
    email: str
    password: str


class DocumentResponse(BaseModel):
    id: int
    title: str
    company_name: str
    document_type: str
    uploaded_by: int

    class Config:
        from_attributes = True


class RoleAssign(BaseModel):
    user_id: int
    role: str


class SearchQuery(BaseModel):
    query: str