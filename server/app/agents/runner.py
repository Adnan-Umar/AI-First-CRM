from typing import Any

from sqlalchemy.orm import Session

from app.agents.context import load_available_doctors, normalize_form_for_agent, today_iso
from app.agents.graph import agent_graph
from app.agents.schemas import INTENT_LABELS


def process_agent_message(
    db: Session,
    message: str,
    current_form: dict[str, Any],
) -> tuple[str, dict[str, Any] | None, str | None]:
    """Run the routed LangGraph agent and return reply, extracted fields, and intent."""
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

    result = agent_graph.invoke(initial_state)

    intent = result.get("intent")
    reply = result.get("reply") or "I processed your request."
    extracted_fields = result.get("extracted_fields")

    if intent:
        extracted_fields = extracted_fields or {}
        extracted_fields["intent"] = intent
        extracted_fields["intentLabel"] = INTENT_LABELS.get(intent, intent)

    return reply, extracted_fields, intent
