from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.schemas.common import Timestamps, UUIDModel


class HCPBase(BaseModel):
    organization_id: UUID | None = None
    first_name: str = Field(min_length=2, max_length=100)
    last_name: str = Field(min_length=2, max_length=100)
    specialty: str = Field(min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    preferred_channel: str | None = Field(default=None, max_length=50)


class HCPCreate(HCPBase):
    pass


class HCPUpdate(BaseModel):
    organization_id: UUID | None = None
    first_name: str | None = Field(default=None, min_length=2, max_length=100)
    last_name: str | None = Field(default=None, min_length=2, max_length=100)
    specialty: str | None = Field(default=None, min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    preferred_channel: str | None = Field(default=None, max_length=50)


class HCPRead(HCPBase, UUIDModel, Timestamps):
    full_name: str
    organization_name: str | None = None

    @model_validator(mode="before")
    @classmethod
    def assemble_custom_fields(cls, data: Any) -> Any:
        if hasattr(data, "first_name") and hasattr(data, "last_name"):
            data.full_name = f"{data.first_name} {data.last_name}"
        if hasattr(data, "organization") and data.organization:
            data.organization_name = data.organization.name
        return data

