from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import DBSession
from app.repositories.interaction import interaction_repository
from app.repositories.hcp import hcp_repository
from app.schemas.interaction import InteractionCreate, InteractionRead, InteractionUpdate

router = APIRouter()


def _validate_hcp_id(db: DBSession, hcp_id: UUID) -> None:
    hcp = hcp_repository.get(db, hcp_id)
    if hcp is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="hcp_id does not reference an existing healthcare professional.",
        )


@router.post("/", response_model=InteractionRead, status_code=status.HTTP_201_CREATED)
def create_interaction(payload: InteractionCreate, db: DBSession) -> InteractionRead:
    _validate_hcp_id(db, payload.hcp_id)
    
    # Extract data dict
    data = payload.model_dump()

    if data.get("notes") and not data.get("summary"):
        data["summary"] = data.get("notes")[:200]
    if not data.get("objective"):
        products = data.get("products_discussed") or []
        data["objective"] = (
            f"Discuss products: {', '.join(products)}" if products else "HCP engagement"
        )
    if not data.get("outcome"):
        data["outcome"] = "Follow-up planned."

    interaction = interaction_repository.create(db, data)
    created = interaction_repository.get(db, interaction.id)
    return InteractionRead.model_validate(created or interaction)


@router.get("/", response_model=list[InteractionRead])
def list_interactions(
    db: DBSession,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[InteractionRead]:
    interactions = interaction_repository.list(db, offset=offset, limit=limit)
    return [InteractionRead.model_validate(item) for item in interactions]


@router.get("/{id}", response_model=InteractionRead)
def get_interaction(id: UUID, db: DBSession) -> InteractionRead:
    interaction = interaction_repository.get(db, id)
    if interaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found.")
    return InteractionRead.model_validate(interaction)


@router.put("/{id}", response_model=InteractionRead)
def update_interaction(id: UUID, payload: InteractionUpdate, db: DBSession) -> InteractionRead:
    interaction = interaction_repository.get(db, id)
    if interaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found.")
        
    data = payload.model_dump(exclude_unset=True)
    if "hcp_id" in data and data["hcp_id"] is not None:
        _validate_hcp_id(db, data["hcp_id"])
        
    updated = interaction_repository.update(db, interaction, data)
    refreshed = interaction_repository.get(db, updated.id)
    return InteractionRead.model_validate(refreshed or updated)
