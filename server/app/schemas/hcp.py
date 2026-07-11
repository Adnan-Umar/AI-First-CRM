from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

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
    pass

