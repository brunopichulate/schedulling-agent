from fastapi import APIRouter
from src.api.v1 import (
  whatsapp,
)

api_v1_router = APIRouter(prefix="/v1")

# Add channels in here
api_v1_router.include_router(
  whatsapp.router, prefix="/channels/whatsapp", tags=["WhatsApp"]
)

__all__ = ["api_v1_router"]
