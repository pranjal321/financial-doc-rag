# Financial Document Management API

FastAPI application for financial document management with AI-powered semantic search (RAG).

## Tech Stack
- FastAPI + PostgreSQL + SQLAlchemy
- ChromaDB (vector database)
- Sentence Transformers (all-MiniLM-L6-v2) for embeddings
- CrossEncoder (ms-marco-MiniLM-L-6-v2) for reranking
- JWT authentication + RBAC

## Setup

### 1. Install dependencies
pip install -r requirements.txt

### 2. Create PostgreSQL database
CREATE DATABASE finance_db;

### 3. Configure database
Update DATABASE_URL in app/database.py

### 4. Run server
uvicorn app.main:app --reload

### 5. Open API docs
http://127.0.0.1:8000/docs

## RAG Pipeline
Document → Text Extraction → Chunking (500 tokens) → Embeddings → ChromaDB
Query → Embedding → Top 20 Vector Search → CrossEncoder Reranking → Top 5 Results

## API Endpoints

### Auth
- POST /auth/register
- POST /auth/login

### Documents
- POST /documents/upload
- GET /documents/
- GET /documents/{id}
- DELETE /documents/{id}
- GET /documents/search?company=ABC&document_type=invoice

### RAG
- POST /rag/index-document
- DELETE /rag/remove-document/{id}
- POST /rag/search
- GET /rag/context/{id}

### Roles & Permissions
- POST /roles/create
- POST /roles/assign-role
- GET /roles/users/{id}/roles
- GET /roles/users/{id}/permissions

## Roles
| Role | Permissions |
|------|-------------|
| Admin | Full access |
| Analyst | Upload and edit documents |
| Auditor | Review documents |
| Client | View documents only |
```

Then push it:
```
git add README.md
git commit -m "Add README"
git push
