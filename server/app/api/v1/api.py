from fastapi import APIRouter

from app.api.v1.endpoints.ai import router as ai_router
from app.api.v1.endpoints.hcps import router as hcps_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.organizations import router as organizations_router
from app.api.v1.endpoints.users import router as users_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(
    organizations_router, prefix="/organizations", tags=["organizations"]
)
api_router.include_router(hcps_router, prefix="/hcps", tags=["hcps"])
