"""Provider-agnostic LLM client.

Offline mode returns an extractive answer (the best-matching passage) so tests, CI and evals
run without an API key or cost. Switch to a real model with LLM_PROVIDER=anthropic.
Add other providers by implementing `generate()`.
"""

from typing import Protocol

from app.config import Settings

SYSTEM_PROMPT = (
    "Answer the question using only the context passages. "
    "If the context does not contain the answer, say you don't know. "
    "Cite the source file names you used in square brackets."
)


class LLM(Protocol):
    def generate(self, question: str, context: list[str]) -> str: ...


class OfflineLLM:
    def generate(self, question: str, context: list[str]) -> str:
        if not context:
            return "I don't know based on the available documents."
        return context[0]


class AnthropicLLM:
    def __init__(self, settings: Settings):
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        import anthropic  # optional dependency: `uv sync --extra llm`

        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.llm_model
        self.max_tokens = settings.max_output_tokens

    def generate(self, question: str, context: list[str]) -> str:
        passages = "\n\n".join(f"<passage>\n{c}\n</passage>" for c in context)
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"{passages}\n\nQuestion: {question}"},
            ],
        )
        return "".join(block.text for block in message.content if block.type == "text")


def get_llm(settings: Settings) -> LLM:
    if settings.llm_provider == "anthropic":
        return AnthropicLLM(settings)
    return OfflineLLM()
