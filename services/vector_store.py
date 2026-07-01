import os
import uuid
from pathlib import Path
from typing import List, Dict

import chromadb
from sentence_transformers import SentenceTransformer
from config import CHROMA_PATH

_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
_client = chromadb.PersistentClient(path=CHROMA_PATH)


def get_collection(name: str):
    return _client.get_or_create_collection(name=name)


def read_text_files(folder: str) -> List[Dict]:
    records = []
    for path in Path(folder).glob("*.txt"):
        text = path.read_text(encoding="utf-8")
        records.append({"source": path.name, "text": text})
    return records


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]


def ingest_folder(collection_name: str, folder: str, doc_type: str) -> int:
    collection = get_collection(collection_name)
    records = read_text_files(folder)
    documents, metadatas, ids = [], [], []

    for record in records:
        chunks = chunk_text(record["text"])
        for idx, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({
                "source": record["source"],
                "doc_type": doc_type,
                "chunk": idx,
            })
            ids.append(f"{collection_name}-{record['source']}-{idx}-{uuid.uuid4()}")

    if not documents:
        return 0

    embeddings = _embedding_model.encode(documents).tolist()
    collection.add(documents=documents, metadatas=metadatas, ids=ids, embeddings=embeddings)
    return len(documents)


def query_collection(collection_name: str, query: str, n_results: int = 3) -> Dict:
    collection = get_collection(collection_name)
    query_embedding = _embedding_model.encode([query]).tolist()
    return collection.query(query_embeddings=query_embedding, n_results=n_results)


def format_results(results: Dict) -> Dict:
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    context = "\n\n".join([f"Source: {meta.get('source')}\n{doc}" for doc, meta in zip(documents, metadatas)])
    sources = [
        {
            "source": meta.get("source"),
            "doc_type": meta.get("doc_type"),
            "chunk": meta.get("chunk"),
        }
        for meta in metadatas
    ]
    return {"context": context, "sources": sources, "documents": documents}
