from sentence_transformers import SentenceTransformer, CrossEncoder
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
import fitz

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

client = chromadb.Client()
collection = client.get_or_create_collection(name="documents")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

def extract_text(file_path: str) -> str:
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception:
        return ""

def store_embedding(doc_id: int, text: str):
    if not text:
        return

    chunks = splitter.split_text(text)

    if not chunks:
        return

    embeddings = embedding_model.encode(chunks).tolist()

    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=[{"doc_id": doc_id, "chunk_index": i} for i in range(len(chunks))]
    )


def search_similar(query: str, top_k: int = 5) -> list:
    if collection.count() == 0:
        return ["No documents indexed yet"]

    query_embedding = embedding_model.encode(query).tolist()

    n_results = min(20, collection.count())
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    candidate_docs = results.get("documents", [[]])[0]

    if not candidate_docs:
        return ["No relevant content found"]

    pairs = [[query, doc] for doc in candidate_docs]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(candidate_docs, scores), key=lambda x: x[1], reverse=True)
    top_results = [doc for doc, score in ranked[:top_k]]

    return top_results


def remove_embedding(doc_id: int):
    try:
        existing = collection.get()
        ids_to_delete = [
            id_ for id_, meta in zip(existing["ids"], existing["metadatas"])
            if meta.get("doc_id") == doc_id
        ]
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
    except Exception:
        pass