from typing import Any, TypedDict

from sqlalchemy.orm import Session

from app.agents.schemas import AgentIntent


class AgentState(TypedDict):
    message: str
    current_form: dict[str, Any]
    available_doctors: list[dict[str, str]]
    today: str
    db: Session
    intent: AgentIntent | None
    reply: str
    extracted_fields: dict[str, Any] | None
