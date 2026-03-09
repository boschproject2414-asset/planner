from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    role: Mapped[str] = mapped_column(String(50))
    hashed_password: Mapped[str] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class UserRole(Base):
    __tablename__ = "user_roles"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_code: Mapped[str] = mapped_column(String(120), unique=True)
    customer: Mapped[str] = mapped_column(String(120))
    oem: Mapped[str] = mapped_column(String(120))
    engine_type: Mapped[str] = mapped_column(String(120))
    engine_serial: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(50), default="planned")
    baseline_start: Mapped[date | None] = mapped_column(Date)
    baseline_finish: Mapped[date | None] = mapped_column(Date)
    gate_state: Mapped[str] = mapped_column(String(10), default="G1")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Trolley(Base):
    __tablename__ = "trolleys"
    id: Mapped[int] = mapped_column(primary_key=True)
    trolley_code: Mapped[str] = mapped_column(String(50), unique=True)
    location: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(50), default="available")


class ProjectTrolley(Base):
    __tablename__ = "project_trolleys"
    __table_args__ = (UniqueConstraint("trolley_id", "active_to", name="uq_trolley_active"),)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    trolley_id: Mapped[int] = mapped_column(ForeignKey("trolleys.id"), primary_key=True)
    active_from: Mapped[date] = mapped_column(Date)
    active_to: Mapped[date | None] = mapped_column(Date)


class ActivityMaster(Base):
    __tablename__ = "activity_master"
    id: Mapped[int] = mapped_column(primary_key=True)
    phase: Mapped[str] = mapped_column(String(50))
    main_activity: Mapped[str] = mapped_column(String(255))
    sub_activity: Mapped[str] = mapped_column(String(255))
    default_effort_hours: Mapped[float] = mapped_column(Float, default=0)
    gate_suggestion: Mapped[str | None] = mapped_column(String(10))
    requires_customer_parts: Mapped[bool] = mapped_column(Boolean, default=False)


class ProjectActivity(Base):
    __tablename__ = "project_activities"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    activity_master_id: Mapped[int] = mapped_column(ForeignKey("activity_master.id"))
    status: Mapped[str] = mapped_column(String(50), default="not_started")
    planned_start: Mapped[date | None] = mapped_column(Date)
    planned_finish: Mapped[date | None] = mapped_column(Date)
    actual_start: Mapped[date | None] = mapped_column(Date)
    actual_finish: Mapped[date | None] = mapped_column(Date)
    percent_complete: Mapped[float] = mapped_column(Float, default=0)
    assigned_team: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(Text)
    optimistic_hours: Mapped[float | None] = mapped_column(Float)
    most_likely_hours: Mapped[float | None] = mapped_column(Float)
    pessimistic_hours: Mapped[float | None] = mapped_column(Float)


class Dependency(Base):
    __tablename__ = "dependencies"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    predecessor_project_activity_id: Mapped[int] = mapped_column(ForeignKey("project_activities.id"))
    successor_project_activity_id: Mapped[int] = mapped_column(ForeignKey("project_activities.id"))
    relationship_type: Mapped[str] = mapped_column(String(2), default="FS")
    lag_hours: Mapped[float] = mapped_column(Float, default=0)


class Gate(Base):
    __tablename__ = "gates"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    gate_code: Mapped[str] = mapped_column(String(2))
    status: Mapped[str] = mapped_column(String(30), default="pending")
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime)
    comment: Mapped[str | None] = mapped_column(Text)


class DailyLog(Base):
    __tablename__ = "daily_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    trolley_id: Mapped[int] = mapped_column(ForeignKey("trolleys.id"))
    log_date: Mapped[date] = mapped_column(Date)
    shift: Mapped[str] = mapped_column(String(20), default="day")
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    summary: Mapped[str] = mapped_column(Text)
    blockers: Mapped[str | None] = mapped_column(Text)
    next_plan: Mapped[str | None] = mapped_column(Text)
    attachments_json: Mapped[dict | None] = mapped_column(JSON)


class DailyLogActivityUpdate(Base):
    __tablename__ = "daily_log_activity_updates"
    id: Mapped[int] = mapped_column(primary_key=True)
    daily_log_id: Mapped[int] = mapped_column(ForeignKey("daily_logs.id"))
    project_activity_id: Mapped[int] = mapped_column(ForeignKey("project_activities.id"))
    hours_spent: Mapped[float] = mapped_column(Float, default=0)
    progress_delta: Mapped[float] = mapped_column(Float, default=0)
    comment: Mapped[str | None] = mapped_column(Text)


class Material(Base):
    __tablename__ = "materials"
    id: Mapped[int] = mapped_column(primary_key=True)
    part_number: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(30))
    criticality: Mapped[str] = mapped_column(String(10))
    default_lead_days: Mapped[int] = mapped_column(Integer, default=0)


class MaterialRequirement(Base):
    __tablename__ = "material_requirements"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project_activity_id: Mapped[int | None] = mapped_column(ForeignKey("project_activities.id"))
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"))
    quantity: Mapped[float] = mapped_column(Float)
    need_by_date: Mapped[date] = mapped_column(Date)
    ownership: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30), default="planned")


class MaterialOrder(Base):
    __tablename__ = "material_orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    material_requirement_id: Mapped[int] = mapped_column(ForeignKey("material_requirements.id"))
    ordered_on: Mapped[date | None] = mapped_column(Date)
    promised_on: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30), default="planned")
    tracking_ref: Mapped[str | None] = mapped_column(String(120))
    supplier_name: Mapped[str | None] = mapped_column(String(120))


class Issue(Base):
    __tablename__ = "issues"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    trolley_id: Mapped[int] = mapped_column(ForeignKey("trolleys.id"))
    project_activity_id: Mapped[int | None] = mapped_column(ForeignKey("project_activities.id"))
    issue_type: Mapped[str] = mapped_column(String(30))
    severity: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(30), default="open")
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RootCause(Base):
    __tablename__ = "root_causes"
    id: Mapped[int] = mapped_column(primary_key=True)
    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"))
    method: Mapped[str] = mapped_column(String(20))
    category: Mapped[str] = mapped_column(String(80))
    five_whys_json: Mapped[dict | None] = mapped_column(JSON)
    corrective_actions_json: Mapped[dict | None] = mapped_column(JSON)
    verified_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime)


class Risk(Base):
    __tablename__ = "risks"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(255))
    probability: Mapped[float] = mapped_column(Float)
    impact: Mapped[float] = mapped_column(Float)
    mitigation: Mapped[str | None] = mapped_column(Text)
    linked_activity_id: Mapped[int | None] = mapped_column(ForeignKey("project_activities.id"))
    status: Mapped[str] = mapped_column(String(30), default="open")


class Anomaly(Base):
    __tablename__ = "anomalies"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    anomaly_type: Mapped[str] = mapped_column(String(40))
    entity_type: Mapped[str] = mapped_column(String(40))
    entity_id: Mapped[int] = mapped_column(Integer)
    score: Mapped[float] = mapped_column(Float)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    explanation: Mapped[str] = mapped_column(Text)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[int] = mapped_column(Integer)
    action: Mapped[str] = mapped_column(String(20))
    before_json: Mapped[dict | None] = mapped_column(JSON)
    after_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
