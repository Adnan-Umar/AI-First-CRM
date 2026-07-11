from datetime import date as date_type, datetime
from uuid import UUID
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator, field_serializer

from app.schemas.common import Timestamps, UUIDModel


def map_hcp_id_to_uuid(v: Any) -> UUID:
    if isinstance(v, str):
        if v == "hcp-001":
            return UUID("a0000000-0000-0000-0000-000000000001")
        elif v == "hcp-002":
            return UUID("a0000000-0000-0000-0000-000000000002")
        elif v == "hcp-003":
            return UUID("a0000000-0000-0000-0000-000000000003")
    try:
        return UUID(str(v))
    except ValueError:
        raise ValueError(f"Invalid UUID: {v}")


def map_uuid_to_hcp_id(v: Any) -> str:
    val_str = str(v).lower()
    if val_str == "a0000000-0000-0000-0000-000000000001":
        return "hcp-001"
    elif val_str == "a0000000-0000-0000-0000-000000000002":
        return "hcp-002"
    elif val_str == "a0000000-0000-0000-0000-000000000003":
        return "hcp-003"
    return val_str


class InteractionBase(BaseModel):
    hcp_id: Any
    visit_type: str = Field(min_length=2, max_length=50)  # 'In-person', 'Call', 'Video'
    date: date_type
    products_discussed: list[str] = Field(default_factory=list)
    notes: str | None = None
    follow_up_date: date_type | None = None

    @field_validator("hcp_id", mode="before")
    @classmethod
    def parse_hcp_id(cls, v: Any) -> UUID:
        return map_hcp_id_to_uuid(v)


class InteractionCreate(InteractionBase):
    objective: str | None = None
    summary: str | None = None
    outcome: str | None = None


class InteractionUpdate(BaseModel):
    hcp_id: Any | None = None
    visit_type: str | None = None
    date: date_type | None = None
    products_discussed: list[str] | None = None
    notes: str | None = None
    follow_up_date: date_type | None = None
    objective: str | None = None
    summary: str | None = None
    outcome: str | None = None

    @field_validator("hcp_id", mode="before")
    @classmethod
    def parse_hcp_id(cls, v: Any) -> UUID | None:
        if v is None:
            return None
        return map_hcp_id_to_uuid(v)


class InteractionRead(InteractionBase, UUIDModel, Timestamps):
    hcp_name: str | None = None
    channel: str | None = None

    # Extracted fields (can be null/empty initially)
    objective: str | None = None
    summary: str | None = None
    outcome: str | None = None

    @model_validator(mode="before")
    @classmethod
    def assemble_fields(cls, data: Any) -> Any:
        # If it is an ORM object, extract attributes into dict or map them
        is_orm = not isinstance(data, dict)
        
        # Determine hcp object and construct name
        hcp = getattr(data, "hcp", None) if is_orm else data.get("hcp")
        if hcp:
            first = getattr(hcp, "first_name", "")
            last = getattr(hcp, "last_name", "")
            hcp_name = f"{first} {last}".strip()
        else:
            hcp_name = None
            
        # Get hcp_id
        raw_hcp_id = getattr(data, "hcp_id", None) if is_orm else data.get("hcp_id")
        hcp_id_mapped = map_uuid_to_hcp_id(raw_hcp_id)
        
        # Get visit_type
        vt = getattr(data, "visit_type", None) if is_orm else data.get("visit_type")
        
        if is_orm:
            # For Pydantic model_validate from ORM
            data.hcp_name = hcp_name
            data.channel = vt
            # Assign the mapped string to hcp_id for serialization
            # Pydantic allows assigning it if we validate/serialize it
        else:
            data["hcp_name"] = hcp_name
            data["channel"] = vt
            data["hcp_id"] = hcp_id_mapped
            
        return data

    @field_serializer("hcp_id")
    def serialize_hcp_id(self, v: Any) -> str:
        return map_uuid_to_hcp_id(v)
