from langchain_groq import ChatGroq

from app.core.config import get_settings

# Larger model used for long-form context generation (follow-up plans, summaries)
# where a bigger context window helps quality. Override with GROQ_CONTEXT_MODEL.
CONTEXT_MODEL = "llama-3.3-70b-versatile"
DEFAULT_TEMPERATURE = 0.1

# The primary model is read from settings (GROQ_MODEL). gemma2-9b-it was
# decommissioned by Groq, so the default is now llama-3.3-70b-versatile
# (an assignment-sanctioned alternative). Swappable via the GROQ_MODEL env var.
def get_default_model() -> str:
    return get_settings().GROQ_MODEL or "llama-3.3-70b-versatile"


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
        model=model or get_default_model(),
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
