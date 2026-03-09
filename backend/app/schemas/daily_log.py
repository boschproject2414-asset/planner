from datetime import date
from pydantic import BaseModel


class DailyLogCreate(BaseModel):
    project_id: int
    trolley_id: int
    log_date: date
    shift: str = "day"
    created_by: int
    summary: str
    blockers: str | None = None
    next_plan: str | None = None
    attachments_json: dict | None = None
