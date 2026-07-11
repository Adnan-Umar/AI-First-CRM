from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    def get(self, db: Session, resource_id: UUID) -> ModelType | None:
        stmt = select(self.model).where(self.model.id == resource_id)
        return db.execute(stmt).scalars().first()

    def list(self, db: Session, offset: int = 0, limit: int = 50) -> list[ModelType]:
        stmt = select(self.model).offset(offset).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def create(self, db: Session, data: dict[str, Any]) -> ModelType:
        resource = self.model(**data)
        db.add(resource)
        db.commit()
        db.refresh(resource)
        return resource

    def update(self, db: Session, resource: ModelType, data: dict[str, Any]) -> ModelType:
        for key, value in data.items():
            setattr(resource, key, value)
        db.add(resource)
        db.commit()
        db.refresh(resource)
        return resource

    def delete(self, db: Session, resource: ModelType) -> None:
        db.delete(resource)
        db.commit()

