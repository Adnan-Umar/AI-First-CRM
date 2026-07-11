from datetime import date
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.api.deps import DBSession
from app.services.ai_service import process_chat_message

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
    extracted_fields: dict[str, Any] | None = None
    intent: str | None = None


@router.post("/chat/messages", response_model=ChatMessageResponse)
def send_chat_message(payload: ChatMessageRequest, db: DBSession) -> ChatMessageResponse:
    # Convert incoming request format to current form dictionary expected by the service
    current_form = {
        "doctorId": payload.doctor_id or "",
        "visitType": payload.visit_type or "In-person",
        "date": payload.interaction_date.isoformat() if payload.interaction_date else "",
        "productsDiscussed": ", ".join(payload.products_discussed) if payload.products_discussed else "",
        "notes": payload.notes or "",
        "followUpDate": payload.follow_up_date.isoformat() if payload.follow_up_date else "",
    }

    reply, extracted_fields = process_chat_message(db, payload.message, current_form)
    intent = extracted_fields.get("intent") if extracted_fields else None

    return ChatMessageResponse(reply=reply, extracted_fields=extracted_fields, intent=intent)
