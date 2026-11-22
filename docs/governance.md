# Governance note

A one-page summary of how this system handles data, risk and accountability. This is where a data-governance background stands out, so keep it concrete.

| Area | How it's handled |
| --- | --- |
| Data sources and licences | <list, with licences> |
| Personal or sensitive data | <none used / classification and controls> |
| Access control | <who can call the API, keys, rate limits> |
| Logging and audit | <what is logged, retention, no secrets or personal data in logs> |
| Prompt injection and misuse | <tests in evals/, input limits, output checks> |
| Hallucination controls | <grounding, citations, "don't know" behaviour, eval results> |
| Human oversight | <where a person reviews or approves> |
| Model and data lineage | <versions of model, prompts, data, linked to releases> |
| Cost controls | <spending cap, model choice, caching> |
| Known risks and mitigations | <top three> |

References: OWASP Top 10 for LLM Applications; your organisation's AI use policy.
