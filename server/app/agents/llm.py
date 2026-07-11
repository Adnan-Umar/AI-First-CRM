from langchain_groq import ChatGroq

from app.core.config import get_settings

DEFAULT_MODEL = "gemma2-9b-it"
DEFAULT_TEMPERATURE = 0.1


def get_groq_api_key() -> str | None:
    return get_settings().GROQ_API_KEY


def create_llm(*, temperature: float = DEFAULT_TEMPERATURE) -> ChatGroq:
    api_key = get_groq_api_key()
    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured.")
    return ChatGroq(
        model=DEFAULT_MODEL,
        groq_api_key=api_key,
        temperature=temperature,
    )


def create_structured_llm(schema: type, *, temperature: float = DEFAULT_TEMPERATURE):
    return create_llm(temperature=temperature).with_structured_output(schema)
