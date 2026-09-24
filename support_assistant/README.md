# Module 3 — Zepto Support Assistant

## Overview

Module 3 implements a grounded GenAI support assistant for Zepto policy questions.

The service combines:

- An 8-document Zepto policy corpus
- Local document ingestion and chunking
- `all-MiniLM-L6-v2` local embeddings
- ChromaDB vector storage
- LangGraph `StateGraph` orchestration
- Intent classification and conditional routing
- Top-3 semantic retrieval
- Deterministic offline mock generation
- Optional real-LLM generation
- Pydantic structured output validation
- FastAPI `/ask` endpoint
- Docker containerization

The required graded baseline runs without an external LLM API by using deterministic `MOCK_LLM` mode. Embeddings are generated locally using `all-MiniLM-L6-v2`, and ChromaDB runs locally.

No LLM API key or LLM-provider network access is required for the required baseline.

## 1. Module Overview

The Support Assistant answers questions using a fixed Zepto policy corpus.

The complete RAG architecture is:

Policy Documents
      ↓
Document Ingestion
      ↓
Chunking
      ↓
Local Embeddings (`all-MiniLM-L6-v2`)
      ↓
ChromaDB Vector Store
      ↓
User Query
      ↓
Intent Classification
      ↓
Top-3 Semantic Retrieval
      ↓
Grounded Generation
      ↓
Pydantic Structured Response
      ↓
FastAPI `/ask`

The assignment requires the complete RAG flow:

ingestion → embedding → retrieval → generation

2. Project Structure
support_assistant/
│
├── README.md
├── Dockerfile
├── config.py
├── schemas.py
├── prompts.py
├── ingestion.py
├── build_index.py
├── graph.py
├── main.py
│
├── docs/
│   ├── doc_01.txt
│   ├── doc_02.txt
│   ├── doc_03.txt
│   ├── doc_04.txt
│   ├── doc_05.txt
│   ├── doc_06.txt
│   ├── doc_07.txt
│   └── doc_08.txt
│
└── chroma_db/
    └── generated locally

chroma_db/ is generated locally and should not be committed to Git.

3. Policy Documents

The application uses eight Zepto policy documents:

File	Policy
doc_01.txt	Delivery Policy
doc_02.txt	Returns & Refunds
doc_03.txt	Membership Tiers
doc_04.txt	Order Tracking
doc_05.txt	Order Cancellation
doc_06.txt	Damaged or Missing Items
doc_07.txt	Gift Cards
doc_08.txt	Customer Support Hours

These files are the complete policy corpus used by the application; no additional policy documents are required for the graded baseline.

4. Technologies
Core Technologies
Python
Sentence Transformers
all-MiniLM-L6-v2
ChromaDB
LangGraph
Pydantic
FastAPI
Uvicorn
Docker
Optional
Groq / another LLM provider when MOCK_LLM=0

The required embedding model is:

all-MiniLM-L6-v2

Embeddings are generated locally and do not require an API key.

5. Installation

From the project root:

python3 -m venv venv

Activate the virtual environment:

macOS / Linux
source venv/bin/activate
Windows
venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

If using the module requirements file instead:

pip install -r support_assistant/requirements.txt
6. MOCK_LLM Mode

The graded baseline uses deterministic offline mock mode.

By default:

MOCK_LLM=1

or simply leave the variable unset.

No LLM API key is required.

The assignment specifically states that the default mock mode is the graded baseline.

You can explicitly enable it with:

export MOCK_LLM=1

The optional real-LLM mode is:

export MOCK_LLM=0

The real LLM path is optional and is not required for the graded submission.

7. Step 1 — Build the Vector Index

From the support_assistant directory:

cd support_assistant
python build_index.py

This performs the following:

docs/*.txt
    ↓
Load documents
    ↓
Create document chunks
    ↓
Generate embeddings
    ↓
Store embeddings
    ↓
ChromaDB

The implementation uses:

ChromaDB collection:
zepto_policies

The documents are embedded using:

all-MiniLM-L6-v2

The assignment requires all eight documents to be embedded and queryable from ChromaDB.

## 7.1 Fresh Clone Requirement

On a fresh clone, run `python build_index.py` before starting the API.

This creates the local `chroma_db/` vector store from the eight policy documents. The generated `chroma_db/` directory is not required to be committed to Git.

8. Step 2 — Start the FastAPI Application

From:

support_assistant/

run:

uvicorn main:app --reload

The API will start at:

http://127.0.0.1:8000

Swagger documentation is available at:

http://127.0.0.1:8000/docs
9. API Endpoint
POST /ask

Request:

{
  "query": "What is the delivery policy?"
}

Response schema:

{
  "answer": "string",
  "sources": [],
  "confidence": 1.0
}

The Pydantic response contains:

answer
sources
confidence

The assignment requires confidence to be between 0 and 1.

10. LangGraph Architecture

The application uses a LangGraph `StateGraph` with a typed state definition.

The graph contains three required nodes:
- `classify_intent`
- `retrieve_and_answer`
- `direct_answer`

The graph flow is:

                 +-------------------+
                 | classify_intent   |
                 +---------+---------+
                           |
                +----------+----------+
                |                     |
                v                     v
       policy_question        general_question
                |                     |
                v                     v
    +----------------------+  +----------------+
    | retrieve_and_answer  |  | direct_answer  |
    +----------+-----------+  +-------+--------+
               |                    |
               +---------+----------+
                         |
                         v
                 Pydantic Response

The conditional routing is based on the classified intent.

The assignment requires this conditional edge.

11. classify_intent

The first node determines whether the query requires retrieval.

In mock mode, the query is converted to lowercase and checked for these keywords:

delivery
return
refund
membership
tracking
cancel
gift card
support hours

If one of these keywords is present:

policy_question

Otherwise:

general_question

Example:

What is the delivery policy?

Routes to:

policy_question

Example:

What is the capital of France?

Routes to:

general_question

No LLM call is made in the default mock mode.

12. retrieve_and_answer

For policy questions, the application:

Embeds the user query.
Searches ChromaDB.
Uses cosine similarity.
Retrieves the top 3 chunks.
The top 3 chunks are returned as retrieval context and source candidates; the deterministic mock generator uses the highest-ranked chunk to construct the answer.

The retrieval flow is:

User Query
    ↓
Embedding Model
    ↓
Query Vector
    ↓
ChromaDB
    ↓
Cosine Similarity
    ↓
Top 3 Chunks
    ↓
Top Chunk
    ↓
Mock Answer

The mock response follows the required format:

Based on the retrieved context: {top_chunk_snippet}

The retrieval operation runs in both mock and real-LLM modes. Only the final generation step changes.

13. direct_answer

For general questions, retrieval is skipped.

In mock mode the application returns:

I can only answer questions about Zepto policies right now.

No LLM call is made.

Example:

What is the capital of France?

Result:

general_question
       ↓
direct_answer
       ↓
Fixed response

This behavior is required by the assignment baseline.

14. RAG Pipeline Architecture
Stage 1 — Ingestion

File:

ingestion.py

The application loads:

docs/doc_01.txt
...
docs/doc_08.txt

Each document is converted into a document chunk.

Stage 2 — Embedding

File:

ingestion.py

Model:

all-MiniLM-L6-v2

Each policy chunk is converted into a numerical vector.

Stage 3 — Retrieval

Files:

ingestion.py
graph.py

The vectors are stored in the ChromaDB collection:

zepto_policies

For a policy query, retrieve_and_answer searches for the three most similar chunks using cosine similarity.

Stage 4 — Generation

File:

graph.py

For policy questions:

retrieve_and_answer

generates the grounded mock response.

For general questions:

direct_answer

returns the fixed mock response.

15. MOCK_LLM Branching

The retrieval stage does not depend on MOCK_LLM.

Retrieval always happens for policy questions.

The generation stage changes depending on:

MOCK_LLM
Default
MOCK_LLM=1

Flow:

Query
 ↓
Intent classification
 ↓
ChromaDB retrieval
 ↓
Deterministic mock response
 ↓
Pydantic validation

No LLM API call is made.

Optional Real LLM
MOCK_LLM=0

Flow:

Query
 ↓
Intent classification
 ↓
ChromaDB retrieval
 ↓
LLM generation
 ↓
Pydantic validation
 ↓
Response

The real-LLM path is optional and is not required for grading.

16. Structured Prompt

The structured prompt is defined in:

prompts.py

It follows the required:

ROLE
CONTEXT
TASK
FORMAT
LENGTH

structure.

It also includes:

An explicit negative constraint.
A few-shot example.
Grounding instructions.

The negative constraint prevents the model from answering using information that is not present in the retrieved context.

The prompt is used by the optional real-LLM path. The assignment requires the actual prompt text to contain the five skeleton components, negative constraint, and few-shot example.

17. Pydantic Output Validation

File:

schemas.py

The response schema is:

{
  "answer": "string",
  "sources": ["document/chunk IDs"],
  "confidence": 1.0
}
Policy question

Example:

{
  "answer": "Based on the retrieved context: ...",
  "sources": ["doc_01"],
  "confidence": 1.0
}
General question

Example:

{
  "answer": "I can only answer questions about Zepto policies right now.",
  "sources": [],
  "confidence": 1.0
}

In mock mode, the response is deterministic.

The optional real-LLM path includes validation retry logic.

18. API Example 1 — Policy Question

Run:

curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the delivery policy?"}'

JSON response
{
    "answer": "Based on the retrieved context: Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer's delivery zone and current order volume Standard del",
    "sources":[
        "doc_01_chunk_01","doc_02_chunk_01","doc_05_chunk_01"
    ],
    "confidence":1.0
} 

The assignment specifically requires the raw JSON responses from the example calls to be recorded in the README.

19. API Example 2 — General Question

Run:

curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the capital of France?"}'

JSON response
{
  "answer":"I can only answer questions about Zepto policies right now.",
  "sources":[],
  "confidence":1.0
}

20. Docker

The application includes a Dockerfile.

From the repository root:

docker build -t zepto-support-assistant ./support_assistant

Run:

docker run --rm -p 7860:7860 zepto-support-assistant

The API will be available at:

http://127.0.0.1:7860

Test it:

curl -X POST "http://127.0.0.1:7860/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the delivery policy?"}'

The assignment requires the Dockerfile to build and run the FastAPI /ask endpoint locally.

21. Docker Architecture
Docker Container
       |
       v
FastAPI
       |
       v
LangGraph
       |
       +------------------+
       |                  |
       v                  v
ChromaDB             Direct Answer
       |
       v
Policy Context
       |
       v
Structured Response

The Docker container runs with:

MOCK_LLM=1

so the required baseline does not need an LLM API key.

22. End-to-End Execution

From the repository root:

source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Build the index:

cd support_assistant
python build_index.py

Start FastAPI:

uvicorn main:app --reload

Then test:

curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the delivery policy?"}'

And:

curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the capital of France?"}'


23. Files and Responsibilities
File	Responsibility
config.py	Paths, model name, ChromaDB configuration, mock mode
schemas.py	Pydantic request/response models
prompts.py	Structured role/context/task/format/length prompt
ingestion.py	Document loading, chunking, embeddings, ChromaDB
build_index.py	Builds the vector index
graph.py	LangGraph nodes, routing, retrieval and generation
main.py	FastAPI application and /ask endpoint
Dockerfile	Containerized FastAPI application
docs/*.txt	Zepto policy corpus