import os

os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

from pathlib import Path
from typing import List, Dict

import chromadb
from sentence_transformers import SentenceTransformer

from config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    DOCS_DIR,
    EMBEDDING_MODEL_NAME,
)


class PolicyIndexer:
    def __init__(self):
        import contextlib
        import io

        # Suppress Hugging Face Hub startup messages
        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR)
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def load_documents(self) -> List[Dict]:
        documents = []

        for file_path in sorted(DOCS_DIR.glob("doc_*.txt")):
            text = file_path.read_text(encoding="utf-8").strip()

            documents.append(
                {
                    "id": file_path.stem,
                    "text": text,
                    "source": file_path.name,
                }
            )

        if len(documents) != 8:
            raise ValueError(
                f"Expected 8 documents, found {len(documents)}"
            )

        return documents

    def chunk_documents(
        self,
        documents: List[Dict],
    ) -> List[Dict]:

        chunks = []

        for document in documents:
            text = document["text"]

            # The assignment allows one chunk per document.
            chunks.append(
                {
                    "id": f"{document['id']}_chunk_01",
                    "document_id": document["id"],
                    "text": text,
                    "source": document["source"],
                }
            )

        return chunks

    def build_index(self):
        documents = self.load_documents()
        chunks = self.chunk_documents(documents)

        texts = [chunk["text"] for chunk in chunks]

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        ).tolist()

        # Rebuild collection deterministically.
        try:
            self.client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        self.collection.add(
            ids=[chunk["id"] for chunk in chunks],
            documents=texts,
            embeddings=embeddings,
            metadatas=[
                {
                    "document_id": chunk["document_id"],
                    "source": chunk["source"],
                }
                for chunk in chunks
            ],
        )

        print(f"Indexed {len(chunks)} chunks.")
        print(f"Collection: {COLLECTION_NAME}")
        print(f"Database: {CHROMA_DIR}")

    def retrieve(self, query: str, top_k: int = 3):
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        ).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
        )

        retrieved = []

        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for i in range(len(ids)):
            retrieved.append(
                {
                    "id": ids[i],
                    "document": documents[i],
                    "metadata": metadatas[i],
                    "distance": distances[i],
                }
            )

        return retrieved


if __name__ == "__main__":
    indexer = PolicyIndexer()
    indexer.build_index()