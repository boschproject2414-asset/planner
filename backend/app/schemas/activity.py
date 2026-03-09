from datetime import date

from pydantic import BaseModel


class ActivityStartRequest(BaseModel):
    actor_user_id: int
    actual_start: date


class GateApproveRequest(BaseModel):
    actor_user_id: int
    comment: str | None = None
