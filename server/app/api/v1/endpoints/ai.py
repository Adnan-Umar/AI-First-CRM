from datetime import date

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class ChatMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    doctor_id: str | None = None
    visit_type: str | None = None
    interaction_date: date | None = None
    products_discussed: list[str] = Field(default_factory=list)
    notes: str | None = None
    follow_up_date: date | None = None


class ChatMessageResponse(BaseModel):
    reply: str


@router.post("/chat/messages", response_model=ChatMessageResponse)
def send_chat_message(payload: ChatMessageRequest) -> ChatMessageResponse:
    products = ", ".join(payload.products_discussed) if payload.products_discussed else "none yet"
    visit = payload.visit_type or "Not specified"
    interaction_date = payload.interaction_date.isoformat() if payload.interaction_date else "Not set"
    follow_up_date = payload.follow_up_date.isoformat() if payload.follow_up_date else "Not set"

    reply = (
        "Captured. Here is the structured draft:\n"
        f"- Doctor: {payload.doctor_id or 'Not selected'}\n"
        f"- Visit type: {visit}\n"
        f"- Date: {interaction_date}\n"
        f"- Products discussed: {products}\n"
        f"- Follow-up date: {follow_up_date}\n"
        f"- Notes summary: {(payload.notes or payload.message).strip()[:240]}"
    )
    return ChatMessageResponse(reply=reply)

