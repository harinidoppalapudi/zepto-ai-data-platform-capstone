from fastapi import FastAPI

from graph import SupportAssistantGraph
from schemas import AskRequest, AskResponse


app = FastAPI(
    title="Zepto Support Assistant",
    description="RAG-based Zepto policy support assistant",
    version="1.0.0",
)


assistant = SupportAssistantGraph()


@app.get("/")
def root():
    return {
        "service": "Zepto Support Assistant",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post(
    "/ask",
    response_model=AskResponse,
)
def ask(request: AskRequest):

    return assistant.ask(
        request.query
    )
