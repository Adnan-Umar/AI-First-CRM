from langchain_groq import ChatGroq

from app.core.config import get_settings

# Mandated primary model for the assignment (Groq).
DEFAULT_MODEL = "gemma2-9b-it"
# Optional larger model used for long-form context generation (follow-up plans,
# summaries) where a bigger context window helps quality.
CONTEXT_MODEL = "llama-3.3-70b-versatile"
DEFAULT_TEMPERATURE = 0.1


def get_groq_api_key() -> str | None:
    return get_settings().GROQ_API_KEY


def create_llm(
    *,
    temperature: float = DEFAULT_TEMPERATURE,
    model: str | None = None,
) -> ChatGroq:
    api_key = get_groq_api_key()
    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured.")
    return ChatGroq(
        model=model or DEFAULT_MODEL,
        groq_api_key=api_key,
        temperature=temperature,
    )


def create_structured_llm(
    schema: type,
    *,
    temperature: float = DEFAULT_TEMPERATURE,
    model: str | None = None,
):
    return create_llm(temperature=temperature, model=model).with_structured_output(schema)
