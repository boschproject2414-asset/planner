from datetime import date, datetime
import io

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.v2_models import (
    V2ActionItem,
    V2Activity,
    V2Baseline,
    V2DailyLog,
    V2DelayEvent,
    V2Dependency,
    V2MaterialRequirement,
    V2Project,
    V2Template,
    V2TemplateActivity,
    V2Trolley,
)
from app.schemas.v2 import V2ActivityCreate, V2BaselineCreate, V2DailyLogCreate, V2ProjectCreate
from app.services.scheduling_v2 import CycleError, recalc_forecast

router_v2 = APIRouter(prefix="/v2", tags=["v2"])


@router_v2.get("/portfolio")
def portfolio(db: Session = Depends(get_db)):
    projects = db.scalars(select(V2Project)).all()
    out = []
    for p in projects:
        delayed = db.scalar(
            select(func.count()).select_from(V2Activity).where(
                V2Activity.project_id == p.id,
                V2Activity.status != "complete",
                V2Activity.planned_finish.is_not(None),
                V2Activity.planned_finish < date.today(),
            )
        )
        material_risks = len(_material_risks(db, p.id))
        out.append({"id": p.id, "project_code": p.project_code, "name": p.name, "delayed": delayed, "material_risks": material_risks})
    return out


@router_v2.post("/projects")
def create_project(payload: V2ProjectCreate, db: Session = Depends(get_db)):
    p = V2Project(**payload.model_dump(), status="active")
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router_v2.get("/projects/{project_id}/home")
def project_home(project_id: int, db: Session = Depends(get_db)):
    project = db.scalar(select(V2Project).where(V2Project.id == project_id))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    logs = db.scalars(select(V2DailyLog).where(V2DailyLog.project_id == project_id).order_by(V2DailyLog.log_date.desc()).limit(5)).all()
    delays = db.scalars(select(V2DelayEvent).where(V2DelayEvent.project_id == project_id, V2DelayEvent.status != "closed").limit(5)).all()
    actions = db.scalars(select(V2ActionItem).where(V2ActionItem.project_id == project_id, V2ActionItem.status != "closed").limit(5)).all()
    return {"project": {"id": project.id, "name": project.name}, "logs": [l.summary for l in logs], "risks": [d.root_cause_category for d in delays], "actions": [a.title for a in actions]}


@router_v2.get("/projects/{project_id}/activities")
def list_activities(project_id: int, db: Session = Depends(get_db)):
    rows = db.scalars(select(V2Activity).where(V2Activity.project_id == project_id)).all()
    return rows


@router_v2.post("/activities")
def create_activity(payload: V2ActivityCreate, db: Session = Depends(get_db)):
    act = V2Activity(**payload.model_dump(), status="not_started")
    db.add(act)
    db.commit()
    db.refresh(act)
    return act


@router_v2.post("/projects/{project_id}/recalculate")
def recalculate(project_id: int, db: Session = Depends(get_db)):
    project = db.scalar(select(V2Project).where(V2Project.id == project_id))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    acts = db.scalars(select(V2Activity).where(V2Activity.project_id == project_id)).all()
    deps = db.scalars(select(V2Dependency).where(V2Dependency.project_id == project_id)).all()
    if not acts:
        return {"updated": 0}
    payload = {
        a.id: {
            "planned_start": a.planned_start or project.start_target or date.today(),
            "duration_days": max(int((a.base_effort_hours or 8) / 8), 1),
        }
        for a in acts
    }
    edges = [(d.predecessor_activity_id, d.successor_activity_id) for d in deps]
    try:
        forecast = recalc_forecast(payload, edges, project.start_target or date.today())
    except CycleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    for a in acts:
        a.forecast_start, a.forecast_finish = forecast[a.id]
        if a.forecast_finish and a.planned_finish and a.status != "complete" and a.forecast_finish > a.planned_finish:
            db.add(V2DelayEvent(project_id=project_id, activity_id=a.id, detected_on=date.today(), delay_hours=(a.forecast_finish - a.planned_finish).days * 8, status="open", root_cause_category="schedule_variance"))
    db.commit()
    return {"updated": len(acts)}


@router_v2.get("/projects/{project_id}/dependencies")
def dependency_table(project_id: int, db: Session = Depends(get_db)):
    deps = db.scalars(select(V2Dependency).where(V2Dependency.project_id == project_id)).all()
    out = []
    for d in deps:
        pred = db.scalar(select(V2Activity).where(V2Activity.id == d.predecessor_activity_id))
        succ = db.scalar(select(V2Activity).where(V2Activity.id == d.successor_activity_id))
        blocked = not pred or pred.status != "complete"
        out.append({"id": d.id, "predecessor": pred.activity_name if pred else None, "successor": succ.activity_name if succ else None, "blocked": blocked})
    return out


def _material_risks(db: Session, project_id: int) -> list[dict]:
    mats = db.scalars(select(V2MaterialRequirement).where(V2MaterialRequirement.project_id == project_id)).all()
    risks = []
    for m in mats:
        stuck = m.status in {"ordered", "not_ordered"} and m.need_by_date and m.need_by_date < date.today()
        late = m.promised_date and m.need_by_date and m.promised_date > m.need_by_date
        if stuck or late:
            risks.append({"id": m.id, "part_number": m.part_number, "risk": "late" if late else "stuck"})
    return risks


@router_v2.get("/projects/{project_id}/material-risks")
def material_risks(project_id: int, db: Session = Depends(get_db)):
    return _material_risks(db, project_id)


@router_v2.get("/projects/{project_id}/materials")
def materials(project_id: int, db: Session = Depends(get_db)):
    return db.scalars(select(V2MaterialRequirement).where(V2MaterialRequirement.project_id == project_id)).all()


@router_v2.post("/projects/{project_id}/daily-logs")
def create_daily_log(project_id: int, payload: V2DailyLogCreate, db: Session = Depends(get_db)):
    log = V2DailyLog(**payload.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router_v2.get("/projects/{project_id}/delays")
def delays(project_id: int, db: Session = Depends(get_db)):
    return db.scalars(select(V2DelayEvent).where(V2DelayEvent.project_id == project_id)).all()


@router_v2.get("/projects/{project_id}/actions")
def actions(project_id: int, db: Session = Depends(get_db)):
    return db.scalars(select(V2ActionItem).where(V2ActionItem.project_id == project_id)).all()


@router_v2.post("/projects/{project_id}/baselines")
def create_baseline(project_id: int, payload: V2BaselineCreate, db: Session = Depends(get_db)):
    activities = db.scalars(select(V2Activity).where(V2Activity.project_id == project_id)).all()
    snapshot = {
        "activities": [
            {"id": a.id, "planned_start": str(a.planned_start), "planned_finish": str(a.planned_finish), "forecast_finish": str(a.forecast_finish)}
            for a in activities
        ]
    }
    b = V2Baseline(project_id=project_id, name=payload.name, snapshot_json=snapshot)
    db.add(b)
    db.commit()
    db.refresh(b)
    return {"id": b.id, "name": b.name}


@router_v2.get("/projects/{project_id}/baseline-variance")
def baseline_variance(project_id: int, db: Session = Depends(get_db)):
    baseline = db.scalars(select(V2Baseline).where(V2Baseline.project_id == project_id).order_by(V2Baseline.created_at.desc())).first()
    if not baseline:
        return {"variance": []}
    current = {a.id: a for a in db.scalars(select(V2Activity).where(V2Activity.project_id == project_id)).all()}
    variance = []
    for row in baseline.snapshot_json.get("activities", []):
        cid = row["id"]
        if cid in current:
            variance.append({"activity_id": cid, "baseline_finish": row.get("planned_finish"), "forecast_finish": str(current[cid].forecast_finish)})
    return {"variance": variance}


@router_v2.post("/import/preview")
async def import_preview(file: UploadFile = File(...)):
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content)) if file.filename and file.filename.endswith(".csv") else pd.read_excel(io.BytesIO(content))
    cols = list(df.columns)
    return {"columns": cols, "sample": df.head(10).fillna("").to_dict(orient="records")}


@router_v2.post("/projects/{project_id}/import/activities")
async def import_activities(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content)) if file.filename and file.filename.endswith(".csv") else pd.read_excel(io.BytesIO(content))
    created = 0
    for _, r in df.iterrows():
        db.add(V2Activity(project_id=project_id, phase=str(r.get("phase", "Mechanical")), activity_name=str(r.get("activity_name", r.get("Activity", "Task"))), sub_activity=str(r.get("sub_activity", "")) or None, status="not_started", base_effort_hours=float(r.get("base_effort_hours", 8))))
        created += 1
    db.commit()
    return {"created": created}


@router_v2.post("/seed")
def seed_v2(db: Session = Depends(get_db)):
    if db.scalar(select(V2Project).limit(1)):
        return {"status": "already_seeded"}
    t = V2Template(name="PS-ETW Default", description="Seed template")
    db.add(t)
    db.flush()
    rows = [
        V2TemplateActivity(template_id=t.id, phase="Mechanical", activity_name="Engine receipt", sub_activity="Receipt", default_effort_hours=8),
        V2TemplateActivity(template_id=t.id, phase="Mechanical", activity_name="Mounting", sub_activity="Mount engine", default_effort_hours=16),
        V2TemplateActivity(template_id=t.id, phase="Electrical", activity_name="Harness", sub_activity="Harness and power", default_effort_hours=8),
    ]
    db.add_all(rows)
    trolley = V2Trolley(trolley_code="TR-V2-01", location="Bay A", status="active")
    db.add(trolley)
    p = V2Project(project_code="ATLAS-V2-001", name="Atlas Sample", customer="Bosch", status="active", start_target=date.today())
    db.add(p)
    db.flush()
    acts = [
        V2Activity(project_id=p.id, template_activity_id=rows[0].id, phase="Mechanical", activity_name="Engine receipt", planned_start=date.today(), planned_finish=date.today(), base_effort_hours=8),
        V2Activity(project_id=p.id, template_activity_id=rows[1].id, phase="Mechanical", activity_name="Mounting", planned_start=date.today(), planned_finish=date.today(), base_effort_hours=16),
        V2Activity(project_id=p.id, template_activity_id=rows[2].id, phase="Electrical", activity_name="Harness", planned_start=date.today(), planned_finish=date.today(), base_effort_hours=8),
    ]
    db.add_all(acts)
    db.flush()
    db.add(V2Dependency(project_id=p.id, predecessor_activity_id=acts[0].id, successor_activity_id=acts[1].id, type="FS", lag_hours=0))
    db.add(V2Dependency(project_id=p.id, predecessor_activity_id=acts[1].id, successor_activity_id=acts[2].id, type="FS", lag_hours=0))
    db.add(V2MaterialRequirement(project_id=p.id, activity_id=acts[1].id, part_number="P-001", description="Bracket", ownership="internal", criticality="high", need_by_date=date.today(), status="ordered"))
    db.commit()
    return {"status": "seeded", "project_id": p.id}
