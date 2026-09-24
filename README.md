# zepto-ai-data-platform-capstone
Zepto Data &amp; AI Platform

Setup

This project uses a consolidated root requirements.txt for the three modules.

1. Clone the repository
git clone https://github.com/harinidoppalapudi/zepto-ai-data-platform-capstone.git
cd zepto-ai-data-platform-capstone

2. Create a virtual environment
macOS/Linux
python3 -m venv venv
source venv/bin/activate
Windows
python -m venv venv
venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

The consolidated requirements file contains the dependencies used by the data pipeline, analytics/modeling workflow, and support-assistant stack.

Module 1 — Data Pipeline
Objective

The data pipeline collects book catalog data from Books to Scrape, cleans the scraped fields, converts GBP prices to INR using the project-defined fixed rate, stores the data in a normalized SQLite database, executes SQL queries, and validates SQL results against equivalent Pandas operations.

Run Module 1

From the repository root:

python data_pipeline/run_pipeline.py

The end-to-end pipeline performs:

Scraping from Books to Scrape.
Cleaning and type conversion.
Rating conversion from text to integers.
Availability conversion to Boolean values.
GBP-to-INR conversion.
SQLite database creation and loading.
SQL query execution.
Pandas pd.read_sql() analysis.
SQL JOIN vs. Pandas merge() validation.
Saving query outputs under data_pipeline/outputs/query_results/.
Fixed Currency Rate

The project uses the required fixed baseline:

1 GBP = 105.50 INR

The conversion is deterministic and does not require a currency API.

Module 1 Design Decisions

Scraping

requests and BeautifulSoup are used to retrieve and parse the public Books to Scrape pages.

Cleaning

The cleaning stage:

Converts prices into numeric values.
Removes the GBP currency symbol.
Converts star ratings from text to integers.
Converts availability into Boolean values.
Handles numeric parsing failures using median imputation.
Excludes unexpected stock values that cannot be safely inferred.
Currency Conversion

The assignment's fixed baseline is used:

1 GBP = 105.50 INR

A live exchange-rate API is not required.

Database

SQLite is used as the relational storage layer.

The database contains separate:

categories
books

tables connected using a primary-key/foreign-key relationship.

SQL and Pandas Validation

Required SQL operations are implemented in queries.py.

The SQL JOIN result is independently reproduced using:

pd.merge()

This provides a validation of equivalent relational behavior between SQL and Pandas.

More implementation details are available inside:

data_pipeline/

Module 2 — Analytics Pipeline
Objective

The analytics module performs an end-to-end Titanic dataset workflow covering:

Data profiling
Data cleaning
Exploratory Data Analysis
Visualization
Classification
Class imbalance analysis
Hyperparameter tuning
Regression
Residual analysis
Model comparison
Model persistence
Run Module 2

Open the notebooks in VS Code with the Jupyter extension or another Jupyter-compatible environment.

Run the notebooks in this order:

analytics/01_eda.ipynb
analytics/02_modeling.ipynb
EDA

01_eda.ipynb performs:

Dataset loading and profiling.
Missing-value analysis and cleaning.
Univariate analysis of age and fare.
IQR-based outlier analysis.
Survival analysis by sex.
Survival analysis by passenger class.
Survival analysis by sex and passenger class.
Correlation analysis on the required six numeric columns.
Multivariate visualizations with written interpretations.
Exploratory standardization checks for age and fare.
Saving the committed offline dataset as:
analytics/titanic.csv
Modeling

02_modeling.ipynb performs:

Stratified train/test splitting.
Leakage-safe preprocessing.
Imputation.
One-hot encoding.
Feature scaling.
Logistic Regression.
Decision Tree.
Random Forest.
Decision Tree visualization using plot_tree.
Confusion matrix.
Accuracy.
Precision.
Recall.
F1 score.
ROC curve.
AUC.
Baseline vs. class-weight balancing vs. SMOTE comparison.
Random Forest GridSearchCV tuning.
Out-of-bag evaluation.
Multivariate linear regression for fare prediction.
MAE.
RMSE.
R².
Adjusted R².
Residual analysis.
Explicit heteroscedasticity conclusion.
Final classification comparison.
Model recommendation.
Saving and reloading the complete preprocessing + estimator pipeline using joblib.
Module 2 Design Decisions
Offline Reproducibility

The Titanic dataset is committed as:

analytics/titanic.csv

The modeling workflow uses the committed CSV as the offline dataset.

Data Leakage Prevention

Preprocessing is implemented inside scikit-learn Pipeline/ColumnTransformer components so that transformations are fitted only on the training data.

Class Imbalance

The following strategies are compared:

Baseline
class_weight='balanced'
SMOTE

SMOTE is applied only to the training data.

Classification

The following models are evaluated:

Logistic Regression
Decision Tree
Random Forest

The models are evaluated using the required classification metrics.

Regression

Fare prediction is treated as a separate regression task.

Regression metrics are kept separate from classification metrics.

Persistence

The saved model artifact contains the preprocessing steps together with the final estimator so that raw input can be passed directly to the loaded pipeline.

Module 3 — Support Assistant
Objective

Module 3 is a complete grounded GenAI service for Zepto policy questions.

The implementation contains:

An 8-document Zepto policy corpus.
Local document ingestion.
Document chunking.
Local embeddings using all-MiniLM-L6-v2.
ChromaDB vector storage.
Structured prompt engineering.
LangGraph StateGraph.
Intent classification.
Conditional routing.
Retrieval of the top-3 relevant chunks.
Deterministic offline mock generation.
Optional real-LLM generation.
Pydantic structured output.
FastAPI /ask endpoint.
Docker containerization.

The required graded baseline works entirely offline using MOCK_LLM.

No LLM API key or LLM-provider network access is required for the graded mock mode.

Module 3 — Document Corpus

The support_assistant/docs/ directory contains the required eight policy documents:

support_assistant/
└── docs/
    ├── doc_01.txt
    ├── doc_02.txt
    ├── doc_03.txt
    ├── doc_04.txt
    ├── doc_05.txt
    ├── doc_06.txt
    ├── doc_07.txt
    └── doc_08.txt

The documents cover:

Delivery Policy
Returns & Refunds
Membership Tiers
Order Tracking
Order Cancellation
Damaged or Missing Items
Gift Cards
Customer Support Hours

These documents are used as the source corpus for retrieval.

Module 3 — Embeddings and ChromaDB

The support assistant generates embeddings locally using:

sentence-transformers
all-MiniLM-L6-v2

No embedding API key is required.

The generated vectors are stored in ChromaDB.

The ingestion process:

Policy documents
      ↓
Document loading
      ↓
Chunking
      ↓
all-MiniLM-L6-v2
      ↓
Embeddings
      ↓
ChromaDB collection

The eight documents must be indexed before the API is started on a fresh clone.



IMPORTANT — Module 3 Reproducible Run Procedure

The ChromaDB index is created by the ingestion script.

On a fresh clone, run the ingestion step before starting FastAPI.

From the repository root:

cd support_assistant

Install dependencies if they have not already been installed:

pip install -r ../requirements.txt

or, if the support assistant has its own requirements file:

pip install -r requirements.txt

Then build the vector index:

python build_index.py

The build_index.py script uses the PolicyIndexer implementation in
ingestion.py to load the eight policy documents, chunk them, generate
local embeddings using all-MiniLM-L6-v2, and store them in ChromaDB.

The ingestion process loads the eight policy documents, chunks them, generates local embeddings using all-MiniLM-L6-v2, and stores them in ChromaDB.

After successful ingestion, start the FastAPI service:

uvicorn main:app --reload

The API is then available at:

http://127.0.0.1:8000

FastAPI Swagger documentation:

http://127.0.0.1:8000/docs
Important

Do not assume that simply creating:

assistant = SupportAssistantGraph()

automatically builds the ChromaDB index.

The reproducible workflow is:

python build_index.py
        ↓
ChromaDB index created/populated
        ↓
uvicorn main:app --reload
        ↓
POST /ask

This ensures that a fresh clone has a populated vector store before retrieval is attempted.

Module 3 — MOCK_LLM

The required graded mode is the deterministic offline mock mode.

The environment variable is:

MOCK_LLM

When MOCK_LLM is:

unset

or:

MOCK_LLM=1

the application uses the required offline mock behavior.

No LLM API call is made.

No API key is required.

No network call to an LLM provider is required.

Mock Mode

The default mock mode is used for grading.

classify_intent

The query is classified using a keyword heuristic.

A query is classified as:

policy_question

when its lowercase text contains one of:

delivery
return
refund
membership
tracking
cancel
gift card
support hours

Otherwise it is classified as:

general_question

No LLM call is made.

retrieve_and_answer

For a policy_question:

The query is embedded locally.
ChromaDB performs similarity retrieval.
The top-3 relevant chunks are retrieved.
The most relevant chunk is used by the mock response.
The mock answer follows the required structure:
Based on the retrieved context: <top chunk snippet>

The retrieval operation runs in both mock mode and optional real-LLM mode.

direct_answer

For a general_question, the mock mode returns a fixed response such as:

I can only answer questions about Zepto policies right now.

No retrieval is performed.

No LLM call is made.

Module 3 — LangGraph Architecture

The application uses a LangGraph StateGraph with a typed state and three main nodes:

                    ┌───────────────────┐
                    │  User Query       │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ classify_intent   │
                    └─────────┬─────────┘
                              │
                    Conditional Routing
                       ┌──────┴──────┐
                       │             │
                       ▼             ▼
             ┌────────────────┐  ┌────────────────┐
             │retrieve_and_   │  │ direct_answer  │
             │answer          │  │                │
             └───────┬────────┘  └───────┬────────┘
                     │                   │
                     └─────────┬─────────┘
                               ▼
                    ┌────────────────────┐
                    │ Pydantic Response  │
                    │ answer             │
                    │ sources            │
                    │ confidence          │
                    └────────────────────┘
Node 1 — classify_intent

Purpose:

Determine whether the query requires policy retrieval.

Possible classifications:

policy_question
general_question

Mock mode uses the required keyword heuristic.

Optional real-LLM mode can use an LLM for classification.

Node 2 — retrieve_and_answer

This node handles policy questions.

The process is:

Query
 ↓
Embedding
 ↓
ChromaDB similarity search
 ↓
Top-3 chunks
 ↓
Top relevant context
 ↓
Answer generation

In mock mode, no LLM is called.

In optional real-LLM mode, the retrieved context is passed to the structured prompt.

Node 3 — direct_answer

This node handles general questions.

In mock mode it returns the fixed canned response.

In optional real-LLM mode, the query can be passed directly to the LLM without retrieval.

Module 3 — Structured Prompt

The optional real-LLM path uses a structured prompt following the required:

Role
Context
Task
Format
Length

The prompt also includes:

Negative Constraint

The model must not answer using information that is not present in the supplied context.

Example:

Do not answer using information that is not present in the provided context.
Few-Shot Example

The prompt contains an example showing the expected grounded-answer behavior.

The structured prompt is used by the optional MOCK_LLM=0 path.

The required mock baseline does not depend on an external LLM.

Module 3 — Structured Output

The final response is validated using a Pydantic model containing:

answer
sources
confidence

The response structure is:

{
  "answer": "string",
  "sources": [],
  "confidence": 1.0
}
answer

Contains the generated or mock response.

sources

Contains the chunk/document IDs used for policy questions.

For general questions:

"sources": []
confidence

A float between:

0 and 1

In the deterministic mock mode, the confidence value is populated by application code.

Module 3 — Optional Real LLM Mode

The real-LLM path is optional and is not required for the graded baseline.

To activate the optional path:

export MOCK_LLM=0

The real-LLM implementation must use the structured prompt and grounded retrieved context.

If the raw LLM response fails Pydantic validation, the implementation retries up to two additional times with a corrective instruction before returning a clearly marked error response.

API keys must never be hardcoded or committed to Git.

Module 3 — FastAPI

The LangGraph workflow is exposed through FastAPI.

Endpoint
POST /ask
Request
{
  "query": "What is the delivery policy?"
}
Response
{
  "answer": "...",
  "sources": [
    "..."
  ],
  "confidence": 1.0
}

The exact sources values depend on the chunk/document IDs generated by the implementation.

Module 3 — Example API Calls

The following examples must be run with MOCK_LLM left at its default.

Example 1 — Policy Question

This query should trigger retrieval:

curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the delivery policy?"}'


Raw JSON response
{
    "answer":"Based on the retrieved context: Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer's delivery zone and current order volume. Standard del",
    "sources":[
        "doc_01_chunk_01","doc_02_chunk_01","doc_05_chunk_01"
        ],
    "confidence":1.0
} 

The response should demonstrate:

policy_question routing.
ChromaDB retrieval.
Retrieval from the relevant delivery-policy document.
The required mock response format.
Pydantic validation.
Example 2 — General Question

This query should not trigger policy retrieval:

curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the capital of France?"}'
Raw JSON response

{
  "answer": "I can only answer questions about Zepto policies right now.",
  "sources": [],
  "confidence": 1.0
}

This example demonstrates:

general_question classification.
Routing to direct_answer.
No retrieval.
No LLM call.
Empty sources.
Validated Pydantic output.
Module 3 — RAG Pipeline Architecture

The complete RAG pipeline is:

┌─────────────────────────┐
│  8 Zepto Policy Docs    │
│  support_assistant/docs │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Ingestion / Chunking    │
│ ingestion.py            │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Local Embeddings        │
│ all-MiniLM-L6-v2        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ ChromaDB                │
│ Vector Collection       │
└────────────┬────────────┘
             │
             │ Query
             ▼
┌─────────────────────────┐
│ classify_intent         │
└────────────┬────────────┘
             │
       ┌─────┴──────┐
       │            │
       ▼            ▼
 policy_question   general_question
       │            │
       ▼            ▼
┌──────────────┐  ┌──────────────┐
│ Retrieval    │  │ direct_answer│
│ Top-3 chunks │  │              │
└──────┬───────┘  └──────┬───────┘
       │                  │
       ▼                  │
┌──────────────┐          │
│ Generation   │          │
└──────┬───────┘          │
       │                  │
       └────────┬─────────┘
                ▼
       ┌─────────────────┐
       │ Pydantic Output │
       │ answer          │
       │ sources         │
       │ confidence      │
       └─────────────────┘
Pipeline Stages
1. Ingestion

The eight policy documents are loaded from:

support_assistant/docs/

The ingestion process is implemented in:

ingestion.py

It loads and chunks the documents before indexing them.

2. Embedding

Each document chunk is converted into a vector using:

sentence-transformers
all-MiniLM-L6-v2

This embedding process runs locally.

3. Retrieval

The vectors are stored in ChromaDB.

For a policy question, the retrieve_and_answer LangGraph node:

Embeds the incoming query.
Searches ChromaDB.
Retrieves the top-3 most similar chunks.
Uses the retrieved context for answer generation.
4. Generation

In the required mock mode, generation is deterministic and performed by application code.

The policy response uses:

Based on the retrieved context: ...

The general-question response uses the fixed canned response.

In optional MOCK_LLM=0 mode, the retrieved context is passed to the real LLM through the structured prompt.

MOCK_LLM Behavior

The retrieval pipeline itself does not depend on the LLM toggle.

The difference is in the generation/classification behavior:

                         MOCK_LLM
                            │
              ┌─────────────┴─────────────┐
              │                           │
          MOCK_LLM=1                 MOCK_LLM=0
          or unset                   optional
              │                           │
              ▼                           ▼
       Deterministic mock             Real LLM
       No API key                     API key required
       No LLM network call            External LLM call
Mock mode
MOCK_LLM unset

or:

MOCK_LLM=1

is the required graded baseline.

Real LLM mode
MOCK_LLM=0

activates the optional real-LLM extension.

The real-LLM mode must not be required for the project to run or receive the required baseline functionality.

Module 3 — Docker

A Dockerfile is provided inside:

support_assistant/Dockerfile

The container is designed to run the FastAPI service locally.

Build

From the repository root:

docker build -t zepto-support-assistant ./support_assistant
Run
docker run -p 7860:7860 zepto-support-assistant

The API should then be available at:

http://127.0.0.1:7860

Swagger documentation:

http://127.0.0.1:7860/docs
Test Dockerized API
curl -X POST "http://127.0.0.1:7860/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the delivery policy?"}'

The Dockerfile is required to be locally buildable and runnable.

An actual cloud deployment is not required for the graded baseline.

Optional Hugging Face Deployment

Deployment to Hugging Face Spaces is optional.

If attempted:

Use the Docker-based application.
Do not hardcode API keys.
Store secrets using the platform's secret-management mechanism.
Document the live Space URL.
Document that the free community CPU tier was used.

A live Hugging Face deployment is not required for the baseline Module 3 submission.

Module 3 Design Decisions
Grounded Retrieval

Policy questions are answered using the project policy corpus instead of relying on unsupported external information.

Local Embeddings

all-MiniLM-L6-v2 is used so embeddings can be generated locally without an embedding API.

ChromaDB

ChromaDB is used as the local vector store for document chunks and embeddings.

LangGraph

LangGraph provides the explicit intent-routing workflow:

classify_intent
       │
       ├── policy_question ──> retrieve_and_answer
       │
       └── general_question ─> direct_answer
Deterministic Mock Mode

The required baseline does not depend on a real LLM provider.

This makes the project:

Offline reproducible.
Deterministic.
Free to run.
Independent of API availability.
Suitable for automated grading.
Structured Output

Pydantic validates the final response structure:

answer
sources
confidence
FastAPI

FastAPI provides the service interface through:

POST /ask
Docker

Docker provides a reproducible local runtime for the API.

Outputs

Important generated or committed artifacts include:

data_pipeline/
├── data/
├── database/
│   └── zepto_books.db
└── outputs/
    └── query_results/

analytics/
├── titanic.csv
├── models/
│   └── best_pipeline.joblib
└── outputs/

support_assistant/

├── docs/
├── ChromaDB index generated locally
├── LangGraph application
├── FastAPI application
└── Dockerfile


The local ChromaDB vector store is excluded from Git and is regenerated
by running:

```bash
cd support_assistant
python build_index.py

Generated chart images are supporting artifacts. Required interpretations are documented in Markdown cells or README files.

Git Workflow

The repository follows a feature-branch workflow:

main
  │
  └── feature branch
        │
        ├── commit #1
        │
        ├── commit #2
        │
        └── merge back into main

The repository should demonstrate:

A feature branch created from main.
At least two commits on the feature branch.
The feature branch merged back into main.
The resulting history pushed to GitHub.
To inspect the history:

git log --graph --all --oneline --decorate

The Git workflow requirement applies to the repository as a whole; it does not have to be repeated separately for every module.

---

```markdown
## Final Repository Structure

```text
zepto-ai-data-platform-capstone/
│
├── README.md
├── requirements.txt
│
├── data_pipeline/
│
├── analytics/
│   └── titanic.csv
│
└── support_assistant/
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
    ├── config.py
    ├── schemas.py
    ├── prompts.py
    ├── ingestion.py
    ├── build_index.py
    ├── graph.py
    ├── main.py
    ├── Dockerfile
    └── README.md