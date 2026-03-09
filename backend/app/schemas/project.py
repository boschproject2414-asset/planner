from datetime import date
from pydantic import BaseModel


class ProjectOut(BaseModel):
    id: int
    project_code: str
    customer: str
    gate_state: str
    baseline_finish: date | None

    class Config:
        from_attributes = True


class ScheduleRecalcResponse(BaseModel):
    critical_path: list[int]
    forecast_finish: int
