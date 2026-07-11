from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import Timestamps, UUIDModel


class UserBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    role: str = Field(min_length=2, max_length=50)
    territory: str | None = Field(default=None, max_length=100)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    email: EmailStr | None = None
    role: str | None = Field(default=None, min_length=2, max_length=50)
    territory: str | None = Field(default=None, max_length=100)


class UserRead(UserBase, UUIDModel, Timestamps):
    pass

