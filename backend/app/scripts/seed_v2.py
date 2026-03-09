from datetime import date

from app.db.session import SessionLocal
from app.models.v2_models import V2Activity, V2Dependency, V2MaterialRequirement, V2Project, V2Template, V2TemplateActivity, V2Trolley


def run() -> None:
    db = SessionLocal()
    if db.query(V2Project).first():
        print("V2 already seeded")
        return
    t = V2Template(name="PS-ETW Default", description="Seed template")
    db.add(t)
    db.flush()
    ta = [
        V2TemplateActivity(template_id=t.id, phase="Mechanical", activity_name="Engine receipt", default_effort_hours=8),
        V2TemplateActivity(template_id=t.id, phase="Mechanical", activity_name="Mounting", default_effort_hours=16),
        V2TemplateActivity(template_id=t.id, phase="Electrical", activity_name="Harness", default_effort_hours=8),
    ]
    db.add_all(ta)
    tr = V2Trolley(trolley_code="TR-V2-01", location="Bay A", status="active")
    db.add(tr)
    p = V2Project(project_code="ATLAS-V2-001", name="Atlas Sample", customer="Bosch", status="active", start_target=date.today())
    db.add(p)
    db.flush()
    acts = [
        V2Activity(project_id=p.id, template_activity_id=ta[0].id, phase="Mechanical", activity_name="Engine receipt", planned_start=date.today(), planned_finish=date.today(), base_effort_hours=8),
        V2Activity(project_id=p.id, template_activity_id=ta[1].id, phase="Mechanical", activity_name="Mounting", planned_start=date.today(), planned_finish=date.today(), base_effort_hours=16),
        V2Activity(project_id=p.id, template_activity_id=ta[2].id, phase="Electrical", activity_name="Harness", planned_start=date.today(), planned_finish=date.today(), base_effort_hours=8),
    ]
    db.add_all(acts)
    db.flush()
    db.add(V2Dependency(project_id=p.id, predecessor_activity_id=acts[0].id, successor_activity_id=acts[1].id, type="FS", lag_hours=0))
    db.add(V2Dependency(project_id=p.id, predecessor_activity_id=acts[1].id, successor_activity_id=acts[2].id, type="FS", lag_hours=0))
    db.add(V2MaterialRequirement(project_id=p.id, activity_id=acts[1].id, part_number="P-001", description="Bracket", ownership="internal", criticality="high", need_by_date=date.today(), status="ordered"))
    db.commit()
    print("V2 seed complete")


if __name__ == "__main__":
    run()
