from app.models.hcp import HealthcareProfessional
from app.repositories.base import BaseRepository


class HCPRepository(BaseRepository[HealthcareProfessional]):
    def __init__(self) -> None:
        super().__init__(HealthcareProfessional)


hcp_repository = HCPRepository()

