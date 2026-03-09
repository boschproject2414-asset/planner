from datetime import date

from pydantic import BaseModel


class V2ProjectCreate(BaseModel):
    project_code: str
    name: str
    customer: str | None = None


class V2ActivityCreate(BaseModel):
    project_id: int
    phase: str
    activity_name: str
    sub_activity: str | None = None
    planned_start: date | None = None
    planned_finish: date | None = None
    base_effort_hours: float = 8


class V2DailyLogCreate(BaseModel):
    project_id: int
    trolley_id: int
    log_date: date
    created_by: str
    summary: str | None = None
    blockers: str | None = None
    next_plan: str | None = None


class V2BaselineCreate(BaseModel):
    name: str
