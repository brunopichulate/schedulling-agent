import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
  "/health",
  response_model=dict[str, bool],
  summary="Verifies if the API is running successfully",
)
async def health():
  return {"success": True}
