from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.models import ActivityMaster, Dependency, Gate, ProjectActivity


def ensure_activity_can_start(db: Session, activity: ProjectActivity, actual_start: str) -> None:
    master = db.scalar(select(ActivityMaster).where(ActivityMaster.id == activity.activity_master_id))
    if not master:
        raise HTTPException(status_code=404, detail="Activity master not found")

    if master.phase.lower() == "electrical":
        g2 = db.scalar(
            select(Gate).where(
                and_(
                    Gate.project_id == activity.project_id,
                    Gate.gate_code == "G2",
                    Gate.status == "approved",
                )
            )
        )
        if not g2:
            raise HTTPException(status_code=400, detail="Electrical activities can only start after G2 approval")

    predecessors = db.scalars(
        select(Dependency).where(Dependency.successor_project_activity_id == activity.id)
    ).all()
    for dep in predecessors:
        pred_activity = db.scalar(select(ProjectActivity).where(ProjectActivity.id == dep.predecessor_project_activity_id))
        if not pred_activity or pred_activity.actual_finish is None:
            raise HTTPException(status_code=400, detail="Cannot start activity before predecessor completion")

    if activity.actual_start and str(activity.actual_start) != actual_start:
        raise HTTPException(status_code=400, detail="Activity already started")
