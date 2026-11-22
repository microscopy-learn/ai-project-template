# Evals

An eval suite is the strongest single signal in an AI engineering portfolio. Keep it small, real and growing.

## Files

- `dataset.jsonl`: one test case per line: `id`, `question`, `expected_source`, `must_include`.
- `run_evals.py`: runs every case through the pipeline and writes `results/results.md` and `results/results.json`.
- `results/`: commit `results.md` for each release so the README can show progress over time.

## How to grow the set

1. Start with 10 to 20 hand-written cases that cover your main use cases.
2. Add every bug you find as a new case before you fix it.
3. Add hard cases: questions with no answer in the data, ambiguous wording, multi-hop questions.
4. Measure retrieval and generation separately, so you know which part to fix.
5. For real models, add an LLM-as-judge faithfulness check, and spot-check a sample by hand.

## Run

```bash
uv run python evals/run_evals.py                          # offline, free
LLM_PROVIDER=anthropic uv run python evals/run_evals.py   # real model
```
