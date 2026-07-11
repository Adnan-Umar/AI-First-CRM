from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.interaction import Interaction
from app.repositories.base import BaseRepository


class InteractionRepository(BaseRepository[Interaction]):
    def __init__(self) -> None:
        super().__init__(Interaction)

    def get(self, db: Session, resource_id: UUID) -> Interaction | None:
        stmt = (
            select(Interaction)
            .options(joinedload(Interaction.hcp))
            .where(Interaction.id == resource_id)
        )
        return db.execute(stmt).scalars().first()

    def list(self, db: Session, offset: int = 0, limit: int = 50) -> list[Interaction]:
        stmt = (
            select(Interaction)
            .options(joinedload(Interaction.hcp))
            .order_by(Interaction.date.desc(), Interaction.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())


interaction_repository = InteractionRepository()
