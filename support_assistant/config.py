import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "zepto_policies"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

MOCK_LLM = os.getenv("MOCK_LLM", "1") != "0"

TOP_K = 3