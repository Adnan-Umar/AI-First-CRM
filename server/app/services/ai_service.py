from typing import Any

from sqlalchemy.orm import Session

from app.agents.runner import process_agent_message


def process_chat_message(
    db: Session,
    message: str,
    current_form: dict[str, Any],
) -> tuple[str, dict[str, Any] | None]:
    """Backward-compatible wrapper around the LangGraph CRM agent."""
    reply, extracted_fields, _intent = process_agent_message(db, message, current_form)
    return reply, extracted_fields
