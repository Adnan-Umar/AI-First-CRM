from typing import Any

from sqlalchemy.orm import Session

from app.agents.context import load_available_doctors, normalize_form_for_agent, today_iso
from app.agents.graph import agent_graph
from app.agents.schemas import INTENT_LABELS

# gemma2-9b-it (and llama-3.3-70b-versatile) are text-only; Groq rejects image input.
TEXT_ONLY_REPLY = (
    "This assistant is text-only (powered by gemma2-9b-it, which has no vision), "
    "so I can't read images. Please describe the image in words and I'll capture it for you."
)

_IMAGE_ERROR_MARKERS = ("does not support image", "cannot read", "image input", "vision")


def _is_image_error(text: str | None) -> bool:
    lowered = (text or "").lower()
    return any(marker in lowered for marker in _IMAGE_ERROR_MARKERS)


def _text_only_result() -> tuple[str, dict[str, Any] | None, str | None]:
    return (
        TEXT_ONLY_REPLY,
        {"intent": "log_interaction", "note": "image input rejected (text-only model)"},
        "log_interaction",
    )


def process_agent_message(
    db: Session,
    message: str,
    current_form: dict[str, Any],
) -> tuple[str, dict[str, Any] | None, str | None]:
    """Run the routed LangGraph agent and return reply, extracted fields, and intent."""
    # Pre-guard: refuse obvious image payloads before calling the LLM.
    if not isinstance(message, str) or "data:image/" in message or "<img" in message:
        return _text_only_result()

    available_doctors = load_available_doctors(db)
    normalized_form = normalize_form_for_agent(current_form)

    initial_state = {
        "message": message,
        "current_form": normalized_form,
        "available_doctors": available_doctors,
        "today": today_iso(),
        "db": db,
        "intent": None,
        "reply": "",
        "extracted_fields": None,
    }

    try:
        result = agent_graph.invoke(initial_state)
    except Exception as exc:  # defensive: never surface a raw provider error
        if _is_image_error(str(exc)):
            return _text_only_result()
        return "Something went wrong while processing your request.", None, None

    intent = result.get("intent")
    reply = result.get("reply") or "I processed your request."
    extracted_fields = result.get("extracted_fields")

    # Post-guard: a tool may have caught an image error and surfaced it as the reply.
    if _is_image_error(reply):
        return _text_only_result()

    if intent:
        extracted_fields = extracted_fields or {}
        extracted_fields["intent"] = intent
        extracted_fields["intentLabel"] = INTENT_LABELS.get(intent, intent)

    return reply, extracted_fields, intent
