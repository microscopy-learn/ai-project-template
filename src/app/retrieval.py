"""A dependency-free keyword retriever.

It is deliberately simple so the template runs anywhere. Replace it with your real retriever
(vector search, hybrid search, or graph retrieval over Neo4j / SPARQL) and keep the same
`search()` signature so the API, tests and evals keep working.
"""

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

TOKEN = re.compile(r"[a-z0-9]+")
STOPWORDS = set(
    "a an and are as at be by for from how in is it of on or that the this to what when which "
    "who why with".split()
)


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN.findall(text.lower()) if t not in STOPWORDS]


@dataclass(frozen=True)
class Chunk:
    source: str
    text: str


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float


class KeywordRetriever:
    """TF-IDF scoring over paragraph chunks."""

    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self.tokens = [Counter(tokenize(c.text)) for c in chunks]
        df = Counter(term for toks in self.tokens for term in toks)
        n = max(len(chunks), 1)
        self.idf = {term: math.log(1 + n / count) for term, count in df.items()}

    @classmethod
    def from_dir(cls, docs_dir: Path) -> "KeywordRetriever":
        chunks = []
        for path in sorted(docs_dir.glob("*.md")):
            for para in path.read_text(encoding="utf-8").split("\n\n"):
                para = para.strip()
                if para and not para.startswith("#"):
                    chunks.append(Chunk(source=path.name, text=para))
        return cls(chunks)

    def search(self, query: str, top_k: int = 3) -> list[Hit]:
        q = tokenize(query)
        scored = []
        for chunk, toks in zip(self.chunks, self.tokens, strict=True):
            score = sum(toks[t] * self.idf.get(t, 0.0) for t in q)
            if score > 0:
                scored.append(Hit(chunk=chunk, score=round(score, 4)))
        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:top_k]
