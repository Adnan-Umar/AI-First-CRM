from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import DBSession
from app.repositories.organization import organization_repository
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationRead,
    OrganizationUpdate,
)

router = APIRouter()


@router.post("/", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
def create_organization(payload: OrganizationCreate, db: DBSession) -> OrganizationRead:
    organization = organization_repository.create(db, payload.model_dump())
    return OrganizationRead.model_validate(organization)


@router.get("/", response_model=list[OrganizationRead])
def list_organizations(
    db: DBSession,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[OrganizationRead]:
    organizations = organization_repository.list(db, offset=offset, limit=limit)
    return [OrganizationRead.model_validate(item) for item in organizations]


@router.get("/{organization_id}", response_model=OrganizationRead)
def get_organization(organization_id: UUID, db: DBSession) -> OrganizationRead:
    organization = organization_repository.get(db, organization_id)
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found."
        )
    return OrganizationRead.model_validate(organization)


@router.patch("/{organization_id}", response_model=OrganizationRead)
def update_organization(
    organization_id: UUID,
    payload: OrganizationUpdate,
    db: DBSession,
) -> OrganizationRead:
    organization = organization_repository.get(db, organization_id)
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found."
        )
    organization = organization_repository.update(
        db, organization, payload.model_dump(exclude_unset=True)
    )
    return OrganizationRead.model_validate(organization)


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(organization_id: UUID, db: DBSession) -> None:
    organization = organization_repository.get(db, organization_id)
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found."
        )
    organization_repository.delete(db, organization)
