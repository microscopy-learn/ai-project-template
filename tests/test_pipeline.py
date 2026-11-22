from pathlib import Path

from app.llm import OfflineLLM
from app.pipeline import Pipeline
from app.retrieval import Chunk, KeywordRetriever, tokenize

DOCS = Path("data/sample_docs")


def test_tokenize_drops_stopwords_and_case():
    assert tokenize("What is the SHACL shape?") == ["shacl", "shape"]


def test_retriever_ranks_relevant_chunk_first():
    retriever = KeywordRetriever(
        [Chunk("a.md", "SPARQL queries RDF graphs"), Chunk("b.md", "Cooking pasta with salt")]
    )
    hits = retriever.search("How do I query RDF?")
    assert hits[0].chunk.source == "a.md"


def test_retriever_returns_nothing_for_unknown_terms():
    retriever = KeywordRetriever.from_dir(DOCS)
    assert retriever.search("zzzz qqqq") == []


def test_pipeline_answers_with_sources():
    pipeline = Pipeline(KeywordRetriever.from_dir(DOCS), OfflineLLM())
    result = pipeline.ask("Which query language does Neo4j use?")
    assert "Cypher" in result.answer
    assert result.sources[0] == "knowledge-graphs.md"


def test_pipeline_says_unknown_without_context():
    pipeline = Pipeline(KeywordRetriever.from_dir(DOCS), OfflineLLM())
    assert "don't know" in pipeline.ask("zzzz qqqq").answer
