"""The end-to-end pipeline: retrieve, then generate. The API, demo, tests and evals all use it."""

import time
from dataclasses import dataclass, field
from functools import lru_cache

from app.config import Settings, settings
from app.llm import LLM, get_llm
from app.retrieval import KeywordRetriever


@dataclass
class Answer:
    answer: str
    sources: list[str]
    latency_ms: float
    retrieved: list[dict] = field(default_factory=list)


class Pipeline:
    def __init__(self, retriever: KeywordRetriever, llm: LLM, top_k: int = 3):
        self.retriever = retriever
        self.llm = llm
        self.top_k = top_k

    @classmethod
    def from_settings(cls, cfg: Settings) -> "Pipeline":
        return cls(KeywordRetriever.from_dir(cfg.docs_dir), get_llm(cfg), cfg.top_k)

    def ask(self, question: str) -> Answer:
        start = time.perf_counter()
        hits = self.retriever.search(question, self.top_k)
        text = self.llm.generate(question, [h.chunk.text for h in hits])
        sources = list(dict.fromkeys(h.chunk.source for h in hits))
        return Answer(
            answer=text,
            sources=sources,
            latency_ms=round((time.perf_counter() - start) * 1000, 2),
            retrieved=[{"source": h.chunk.source, "score": h.score} for h in hits],
        )


@lru_cache(maxsize=1)
def get_pipeline() -> Pipeline:
    return Pipeline.from_settings(settings)
