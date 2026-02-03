from src.api.common import health
from fastapi import APIRouter

common_router = APIRouter(prefix="")

common_router.include_router(health.router, tags=["Health"])

__all__ = ["common_router"]
