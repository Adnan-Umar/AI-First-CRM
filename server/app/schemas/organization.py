from pydantic import BaseModel, Field

from app.schemas.common import Timestamps, UUIDModel


class OrganizationBase(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    organization_type: str = Field(min_length=2, max_length=80)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    organization_type: str | None = Field(default=None, min_length=2, max_length=80)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)


class OrganizationRead(OrganizationBase, UUIDModel, Timestamps):
    pass

