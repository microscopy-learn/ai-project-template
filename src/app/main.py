"""HTTP API. Run locally with: uv run uvicorn app.main:app --reload"""

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field

from app import __version__
from app.pipeline import Pipeline, get_pipeline

app = FastAPI(title="AI Project", version=__version__)


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    latency_ms: float


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": __version__}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest, pipeline: Pipeline = Depends(get_pipeline)) -> AskResponse:  # noqa: B008
    result = pipeline.ask(req.question)
    return AskResponse(answer=result.answer, sources=result.sources, latency_ms=result.latency_ms)
