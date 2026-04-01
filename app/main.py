from fastapi import FastAPI

from app.routes import auth, documents, rag, roles
from app.database import Base, engine
from app import models

app = FastAPI(title="Financial Document Management API")

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(rag.router, prefix="/rag", tags=["RAG"])
app.include_router(roles.router, prefix="", tags=["Roles & Permissions"])


@app.get("/")
def home():
    return {"message": "Financial Document API is running"}