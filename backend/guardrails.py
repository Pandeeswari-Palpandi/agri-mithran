BLOCKED_KEYWORDS = (
    "hack",
    "exploit",
    "violence",
    "password",
    "politics",
    "election",
)


def input_guardrail(query: str) -> bool:
    normalized_query = query.casefold()
    return not any(keyword in normalized_query for keyword in BLOCKED_KEYWORDS)
