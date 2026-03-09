from datetime import datetime

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.models import (
    ActivityMaster,
    Anomaly,
    DailyLog,
    Dependency,
    Gate,
    MaterialOrder,
    MaterialRequirement,
    Project,
    ProjectActivity,
    User,
)
from app.schemas.activity import ActivityStartRequest, GateApproveRequest
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.daily_log import DailyLogCreate
from app.schemas.project import ProjectOut, ScheduleRecalcResponse
from app.services.audit import log_audit
from app.services.rules import ensure_activity_can_start
from app.services.scheduling import ActivityNode, compute_schedule

router = APIRouter()


@router.get("/health")
def healthcheck():
    return {"status": "ok", "ts": datetime.utcnow().isoformat()}


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email, User.active.is_(True)))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.scalars(select(Project)).all()


@router.post("/daily_logs")
def create_daily_log(payload: DailyLogCreate, db: Session = Depends(get_db)):
    dup = db.scalar(
        select(DailyLog).where(
            and_(
                DailyLog.project_id == payload.project_id,
                DailyLog.trolley_id == payload.trolley_id,
                DailyLog.log_date == payload.log_date,
            )
        )
    )
    if dup:
        raise HTTPException(status_code=400, detail="EOD log already exists")
    log = DailyLog(**payload.model_dump())
    db.add(log)
    db.flush()
    log_audit(
        db,
        actor_user_id=payload.created_by,
        entity_type="daily_logs",
        entity_id=log.id,
        action="create",
        before_json=None,
        after_json=payload.model_dump(mode="json"),
    )
    db.commit()
    db.refresh(log)
    return {"id": log.id}


@router.post("/project_activities/{activity_id}/start")
def start_activity(activity_id: int, payload: ActivityStartRequest, db: Session = Depends(get_db)):
    activity = db.scalar(select(ProjectActivity).where(ProjectActivity.id == activity_id))
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    ensure_activity_can_start(db, activity, str(payload.actual_start))

    before = {"status": activity.status, "actual_start": str(activity.actual_start) if activity.actual_start else None}
    activity.status = "in_progress"
    activity.actual_start = payload.actual_start
    db.flush()
    log_audit(
        db,
        actor_user_id=payload.actor_user_id,
        entity_type="project_activities",
        entity_id=activity.id,
        action="update",
        before_json=before,
        after_json={"status": activity.status, "actual_start": str(activity.actual_start)},
    )
    db.commit()
    return {"id": activity.id, "status": activity.status}


@router.post("/projects/{project_id}/gates/{gate_code}/approve")
def approve_gate(project_id: int, gate_code: str, payload: GateApproveRequest, db: Session = Depends(get_db)):
    gate = db.scalar(select(Gate).where(Gate.project_id == project_id, Gate.gate_code == gate_code))
    if not gate:
        raise HTTPException(status_code=404, detail="Gate not found")
    before = {"status": gate.status, "approved_at": str(gate.approved_at) if gate.approved_at else None}
    gate.status = "approved"
    gate.approved_by = payload.actor_user_id
    gate.approved_at = datetime.utcnow()
    gate.comment = payload.comment
    db.flush()

    project = db.scalar(select(Project).where(Project.id == project_id))
    if project:
        project.gate_state = gate_code

    log_audit(
        db,
        actor_user_id=payload.actor_user_id,
        entity_type="gates",
        entity_id=gate.id,
        action="approve",
        before_json=before,
        after_json={"status": gate.status, "approved_at": gate.approved_at.isoformat()},
    )
    db.commit()
    return {"gate": gate.gate_code, "status": gate.status}


@router.post("/projects/{project_id}/recalculate_schedule", response_model=ScheduleRecalcResponse)
def recalc_schedule(project_id: int, db: Session = Depends(get_db)):
    activities = db.scalars(select(ProjectActivity).where(ProjectActivity.project_id == project_id)).all()
    gates = db.scalars(select(Gate).where(and_(Gate.project_id == project_id, Gate.status == "approved"))).all()
    approved = {g.gate_code for g in gates}

    if not activities:
        raise HTTPException(status_code=404, detail="No activities")

    master_map = {
        m.id: m
        for m in db.scalars(
            select(ActivityMaster).where(ActivityMaster.id.in_([a.activity_master_id for a in activities]))
        ).all()
    }
    nodes = {
        a.id: ActivityNode(
            id=a.id,
            duration=(a.most_likely_hours or master_map[a.activity_master_id].default_effort_hours or 1),
            phase=master_map[a.activity_master_id].phase,
        )
        for a in activities
    }
    edges = [
        (d.predecessor_project_activity_id, d.successor_project_activity_id)
        for d in db.scalars(select(Dependency).where(Dependency.project_id == project_id)).all()
    ]
    result = compute_schedule(nodes, edges, approved)
    return {
        "critical_path": result["critical_path"],
        "forecast_finish": int(result["project_finish"]),
    }


@router.post("/projects/{project_id}/simulate_schedule_risk")
def simulate_schedule_risk(project_id: int, n: int = 2000, db: Session = Depends(get_db)):
    activities = db.scalars(select(ProjectActivity).where(ProjectActivity.project_id == project_id)).all()
    if not activities:
        raise HTTPException(status_code=404, detail="No activities")

    simulations = []
    for _ in range(n):
        total = 0.0
        for a in activities:
            o = a.optimistic_hours or 0.8 * (a.most_likely_hours or 8)
            m = a.most_likely_hours or 8
            p = a.pessimistic_hours or 1.25 * m
            total += np.random.triangular(o, m, p)
        simulations.append(total)

    return {
        "simulations": n,
        "p50_hours": int(np.percentile(simulations, 50)),
        "p80_hours": int(np.percentile(simulations, 80)),
        "p95_hours": int(np.percentile(simulations, 95)),
    }


@router.get("/projects/{project_id}/material_risks")
def material_risks(project_id: int, db: Session = Depends(get_db)):
    rows = db.execute(
        select(MaterialRequirement.id, MaterialRequirement.need_by_date, MaterialOrder.promised_on, MaterialOrder.status)
        .join(MaterialOrder, MaterialOrder.material_requirement_id == MaterialRequirement.id, isouter=True)
        .where(MaterialRequirement.project_id == project_id)
    ).all()
    out = []
    for rid, need_by, promised, status in rows:
        risk = 0.0
        if promised and need_by and promised > need_by:
            risk = 0.9
        elif status in {"planned", "ordered"}:
            risk = 0.5
        if risk > 0:
            out.append({"material_requirement_id": rid, "risk_score": risk})
    return out


@router.post("/projects/{project_id}/detect_anomalies")
def detect_anomalies(project_id: int, db: Session = Depends(get_db)):
    activities = db.execute(
        select(ProjectActivity.id, ProjectActivity.actual_start, ProjectActivity.actual_finish, ActivityMaster.default_effort_hours)
        .join(ActivityMaster, ActivityMaster.id == ProjectActivity.activity_master_id)
        .where(ProjectActivity.project_id == project_id)
    ).all()

    created = 0
    for aid, actual_start, actual_finish, default_effort in activities:
        if actual_start and actual_finish and default_effort:
            duration_hours = (actual_finish - actual_start).days * 24
            ratio = duration_hours / max(default_effort, 1)
            if ratio > 1.8:
                db.add(
                    Anomaly(
                        project_id=project_id,
                        anomaly_type="duration_outlier",
                        entity_type="project_activity",
                        entity_id=aid,
                        score=ratio,
                        explanation=f"Actual duration ratio {ratio:.2f} exceeds threshold",
                    )
                )
                created += 1

    db.commit()
    return {"anomalies_created": created}


@router.get("/dashboard/portfolio")
def portfolio(db: Session = Depends(get_db)):
    projects = db.scalars(select(Project)).all()
    return [
        {
            "id": p.id,
            "project_code": p.project_code,
            "gate_state": p.gate_state,
            "critical_delays": 0,
            "material_risks": db.scalar(
                select(func.count()).select_from(MaterialRequirement).where(MaterialRequirement.project_id == p.id)
            ),
        }
        for p in projects
    ]
