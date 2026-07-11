from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.hcp import HealthcareProfessional
from app.models.interaction import Interaction


def search_interactions(
    db: Session,
    *,
    doctor_name: str | None = None,
    visit_type: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = 20,
) -> list[Interaction]:
    stmt = (
        select(Interaction)
        .join(HealthcareProfessional, Interaction.hcp_id == HealthcareProfessional.id)
        .options(joinedload(Interaction.hcp))
        .order_by(Interaction.date.desc(), Interaction.created_at.desc())
        .limit(limit)
    )

    if doctor_name:
        pattern = f"%{doctor_name.strip()}%"
        stmt = stmt.where(
            or_(
                HealthcareProfessional.first_name.ilike(pattern),
                HealthcareProfessional.last_name.ilike(pattern),
            )
        )

    if visit_type:
        stmt = stmt.where(Interaction.visit_type.ilike(visit_type.strip()))

    if date_from:
        stmt = stmt.where(Interaction.date >= date_from)

    if date_to:
        stmt = stmt.where(Interaction.date <= date_to)

    return list(db.execute(stmt).unique().scalars().all())


def find_interaction(
    db: Session,
    *,
    interaction_id: str | None = None,
    doctor_name: str | None = None,
    interaction_date: str | None = None,
) -> Interaction | None:
    if interaction_id:
        try:
            parsed_id = UUID(interaction_id)
        except ValueError:
            return None
        stmt = (
            select(Interaction)
            .options(joinedload(Interaction.hcp))
            .where(Interaction.id == parsed_id)
        )
        return db.execute(stmt).scalars().first()

    parsed_date: date | None = None
    if interaction_date:
        try:
            parsed_date = date.fromisoformat(interaction_date)
        except ValueError:
            parsed_date = None

    results = search_interactions(
        db,
        doctor_name=doctor_name,
        date_from=parsed_date,
        date_to=parsed_date,
        limit=1,
    )
    if results:
        return results[0]

    if doctor_name:
        results = search_interactions(db, doctor_name=doctor_name, limit=1)
        if results:
            return results[0]

    return None


def format_interaction_record(interaction: Interaction) -> str:
    hcp = interaction.hcp
    doctor = f"Dr. {hcp.first_name} {hcp.last_name}" if hcp else "Unknown HCP"
    products = ", ".join(interaction.products_discussed or [])
    return (
        f"ID: {interaction.id}\n"
        f"Doctor: {doctor}\n"
        f"Date: {interaction.date.isoformat()}\n"
        f"Channel: {interaction.visit_type}\n"
        f"Products: {products or 'N/A'}\n"
        f"Objective: {interaction.objective or 'N/A'}\n"
        f"Summary: {interaction.summary or interaction.notes or 'N/A'}\n"
        f"Outcome: {interaction.outcome or 'N/A'}\n"
        f"Follow-up: {interaction.follow_up_date.isoformat() if interaction.follow_up_date else 'N/A'}"
    )


def interaction_to_dict(interaction: Interaction) -> dict[str, Any]:
    hcp = interaction.hcp
    return {
        "id": str(interaction.id),
        "hcpName": f"{hcp.first_name} {hcp.last_name}" if hcp else "Unknown",
        "channel": interaction.visit_type,
        "date": interaction.date.isoformat(),
        "objective": interaction.objective,
        "summary": interaction.summary,
        "outcome": interaction.outcome,
        "notes": interaction.notes,
        "productsDiscussed": interaction.products_discussed,
        "followUpDate": interaction.follow_up_date.isoformat() if interaction.follow_up_date else None,
    }
