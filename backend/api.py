from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request

from backend.guardrails import input_guardrail
from backend.rag_service import RagService
from backend.schemas import SearchRequest, SearchResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    app.state.rag_service = RagService()
    yield


app = FastAPI(
    title="AgriMithran API",
    description="Search Tamil Nadu agriculture schemes in the local FAISS index.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/search", response_model=SearchResponse)
def search_schemes(
    request: SearchRequest,
    http_request: Request,
) -> SearchResponse:
    if not input_guardrail(request.query):
        raise HTTPException(
            status_code=400,
            detail="Question contains restricted or off-topic terms.",
        )

    return http_request.app.state.rag_service.search(
        request.query,
        request.language,
    )
