from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class V2Project(Base):
    __tablename__ = "v2_projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_code: Mapped[str] = mapped_column(String(120), unique=True)
    name: Mapped[str] = mapped_column(String(160))
    customer: Mapped[str | None] = mapped_column(String(120))
    engine_type: Mapped[str | None] = mapped_column(String(120))
    engine_serial: Mapped[str | None] = mapped_column(String(120))
    start_target: Mapped[date | None] = mapped_column(Date)
    finish_target: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(40), default="planned")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class V2Trolley(Base):
    __tablename__ = "v2_trolleys"
    id: Mapped[int] = mapped_column(primary_key=True)
    trolley_code: Mapped[str] = mapped_column(String(80), unique=True)
    location: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(40), default="available")


class V2ProjectTrolley(Base):
    __tablename__ = "v2_project_trolley"
    project_id: Mapped[int] = mapped_column(ForeignKey("v2_projects.id"), primary_key=True)
    trolley_id: Mapped[int] = mapped_column(ForeignKey("v2_trolleys.id"), primary_key=True)
    active_from: Mapped[date] = mapped_column(Date)
    active_to: Mapped[date | None] = mapped_column(Date)


class V2Template(Base):
    __tablename__ = "v2_templates"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class V2TemplateActivity(Base):
    __tablename__ = "v2_template_activities"
    id: Mapped[int] = mapped_column(primary_key=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("v2_templates.id"))
    phase: Mapped[str] = mapped_column(String(40))
    activity_name: Mapped[str] = mapped_column(String(180))
    sub_activity: Mapped[str | None] = mapped_column(String(180))
    default_effort_hours: Mapped[float] = mapped_column(Float, default=8)
    default_materials_text: Mapped[str | None] = mapped_column(Text)
    default_tools_text: Mapped[str | None] = mapped_column(Text)


class V2Activity(Base):
    __tablename__ = "v2_activities"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("v2_projects.id"))
    template_activity_id: Mapped[int | None] = mapped_column(ForeignKey("v2_template_activities.id"))
    phase: Mapped[str] = mapped_column(String(40))
    activity_name: Mapped[str] = mapped_column(String(180))
    sub_activity: Mapped[str | None] = mapped_column(String(180))
    planned_start: Mapped[date | None] = mapped_column(Date)
    planned_finish: Mapped[date | None] = mapped_column(Date)
    forecast_start: Mapped[date | None] = mapped_column(Date)
    forecast_finish: Mapped[date | None] = mapped_column(Date)
    actual_start: Mapped[date | None] = mapped_column(Date)
    actual_finish: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(40), default="not_started")
    percent_complete: Mapped[float] = mapped_column(Float, default=0)
    priority: Mapped[str | None] = mapped_column(String(20))
    owner: Mapped[str | None] = mapped_column(String(120))
    department: Mapped[str | None] = mapped_column(String(120))
    base_effort_hours: Mapped[float] = mapped_column(Float, default=8)
    notes: Mapped[str | None] = mapped_column(Text)


class V2Dependency(Base):
    __tablename__ = "v2_dependencies"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("v2_projects.id"))
    predecessor_activity_id: Mapped[int] = mapped_column(ForeignKey("v2_activities.id"))
    successor_activity_id: Mapped[int] = mapped_column(ForeignKey("v2_activities.id"))
    type: Mapped[str] = mapped_column(String(2), default="FS")
    lag_hours: Mapped[float] = mapped_column(Float, default=0)


class V2MaterialRequirement(Base):
    __tablename__ = "v2_material_requirements"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("v2_projects.id"))
    activity_id: Mapped[int | None] = mapped_column(ForeignKey("v2_activities.id"))
    part_number: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(String(200))
    ownership: Mapped[str] = mapped_column(String(20))
    criticality: Mapped[str] = mapped_column(String(10), default="med")
    need_by_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30), default="not_ordered")
    supplier_name: Mapped[str | None] = mapped_column(String(120))
    tracking_ref: Mapped[str | None] = mapped_column(String(120))
    promised_date: Mapped[date | None] = mapped_column(Date)
    received_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)


class V2DailyLog(Base):
    __tablename__ = "v2_daily_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("v2_projects.id"))
    trolley_id: Mapped[int] = mapped_column(ForeignKey("v2_trolleys.id"))
    log_date: Mapped[date] = mapped_column(Date)
    created_by: Mapped[str] = mapped_column(String(120))
    summary: Mapped[str | None] = mapped_column(Text)
    blockers: Mapped[str | None] = mapped_column(Text)
    next_plan: Mapped[str | None] = mapped_column(Text)
    attachments_json: Mapped[dict | None] = mapped_column(JSON)


class V2DailyLogUpdate(Base):
    __tablename__ = "v2_daily_log_updates"
    id: Mapped[int] = mapped_column(primary_key=True)
    daily_log_id: Mapped[int] = mapped_column(ForeignKey("v2_daily_logs.id"))
    activity_id: Mapped[int] = mapped_column(ForeignKey("v2_activities.id"))
    hours_spent: Mapped[float] = mapped_column(Float, default=0)
    progress_delta: Mapped[float] = mapped_column(Float, default=0)
    comment: Mapped[str | None] = mapped_column(Text)


class V2DelayEvent(Base):
    __tablename__ = "v2_delay_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("v2_projects.id"))
    activity_id: Mapped[int] = mapped_column(ForeignKey("v2_activities.id"))
    detected_on: Mapped[date] = mapped_column(Date)
    delay_hours: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="open")
    root_cause_category: Mapped[str | None] = mapped_column(String(80))
    root_cause_text: Mapped[str | None] = mapped_column(Text)
    five_whys_json: Mapped[dict | None] = mapped_column(JSON)


class V2ActionItem(Base):
    __tablename__ = "v2_action_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("v2_projects.id"))
    activity_id: Mapped[int | None] = mapped_column(ForeignKey("v2_activities.id"))
    delay_event_id: Mapped[int | None] = mapped_column(ForeignKey("v2_delay_events.id"))
    title: Mapped[str] = mapped_column(String(200))
    owner: Mapped[str | None] = mapped_column(String(120))
    due_date: Mapped[date | None] = mapped_column(Date)
    priority: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(40), default="open")
    notes: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class V2Baseline(Base):
    __tablename__ = "v2_baselines"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("v2_projects.id"))
    name: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    snapshot_json: Mapped[dict] = mapped_column(JSON)
