from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ScheduleRequest(BaseModel):
  meeting_id: str


@router.post("/schedule")
async def schedule_meeting(body: ScheduleRequest):
  return {"status": "ok", "meeting_id": body.meeting_id}
