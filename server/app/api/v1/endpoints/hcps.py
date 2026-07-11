from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import DBSession
from app.repositories.hcp import hcp_repository
from app.repositories.organization import organization_repository
from app.schemas.hcp import HCPCreate, HCPRead, HCPUpdate

router = APIRouter()


def _validate_organization_id(db: Session, organization_id: UUID | None) -> None:
    if organization_id is None:
        return
    organization = organization_repository.get(db, organization_id)
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="organization_id does not reference an existing organization.",
        )


@router.post("/", response_model=HCPRead, status_code=status.HTTP_201_CREATED)
def create_hcp(payload: HCPCreate, db: DBSession) -> HCPRead:
    _validate_organization_id(db, payload.organization_id)
    hcp = hcp_repository.create(db, payload.model_dump())
    return HCPRead.model_validate(hcp)


@router.get("/", response_model=list[HCPRead])
def list_hcps(
    db: DBSession,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[HCPRead]:
    hcps = hcp_repository.list(db, offset=offset, limit=limit)
    return [HCPRead.model_validate(item) for item in hcps]


@router.get("/{hcp_id}", response_model=HCPRead)
def get_hcp(hcp_id: UUID, db: DBSession) -> HCPRead:
    hcp = hcp_repository.get(db, hcp_id)
    if hcp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HCP not found.")
    return HCPRead.model_validate(hcp)


@router.patch("/{hcp_id}", response_model=HCPRead)
def update_hcp(hcp_id: UUID, payload: HCPUpdate, db: DBSession) -> HCPRead:
    hcp = hcp_repository.get(db, hcp_id)
    if hcp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HCP not found.")

    data = payload.model_dump(exclude_unset=True)
    if "organization_id" in data:
        _validate_organization_id(db, data["organization_id"])
    hcp = hcp_repository.update(db, hcp, data)
    return HCPRead.model_validate(hcp)


@router.delete("/{hcp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hcp(hcp_id: UUID, db: DBSession) -> None:
    hcp = hcp_repository.get(db, hcp_id)
    if hcp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HCP not found.")
    hcp_repository.delete(db, hcp)
