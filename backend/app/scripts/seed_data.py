from datetime import date

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.models import (
    ActivityMaster,
    Dependency,
    Gate,
    Material,
    MaterialOrder,
    MaterialRequirement,
    Project,
    ProjectActivity,
    ProjectTrolley,
    Role,
    Trolley,
    User,
)


def run() -> None:
    db = SessionLocal()
    if db.query(Project).first():
        print("Already seeded")
        return

    db.add_all([Role(name="admin"), Role(name="engineer")])
    admin = User(
        name="Admin",
        email="admin@atlas.local",
        role="admin",
        hashed_password=get_password_hash("admin123"),
        active=True,
    )
    db.add(admin)
    trolley = Trolley(trolley_code="TR-001", location="PS-ETW Bay", status="active")
    db.add(trolley)
    p = Project(
        project_code="PS-ETW-001",
        customer="Bosch",
        oem="OEM-A",
        engine_type="Diesel",
        engine_serial="EN123",
        status="active",
        baseline_start=date.today(),
        gate_state="G1",
    )
    db.add(p)
    db.flush()

    db.add(ProjectTrolley(project_id=p.id, trolley_id=trolley.id, active_from=date.today(), active_to=None))

    masters = [
        ActivityMaster(phase="Mechanical", main_activity="Receipt", sub_activity="Engine receipt", default_effort_hours=8),
        ActivityMaster(phase="Mechanical", main_activity="Mounting", sub_activity="Mount engine", default_effort_hours=16),
        ActivityMaster(phase="Mechanical", main_activity="Readiness", sub_activity="Mechanical ready", default_effort_hours=4, gate_suggestion="G2"),
        ActivityMaster(phase="Electrical", main_activity="Harness", sub_activity="Harness and power", default_effort_hours=8),
        ActivityMaster(phase="Electrical", main_activity="Sensors", sub_activity="Sensors/ECU/CAN", default_effort_hours=16),
        ActivityMaster(phase="Electrical", main_activity="Readiness", sub_activity="Startup clearance", default_effort_hours=4, gate_suggestion="G4"),
    ]
    db.add_all(masters)
    db.flush()

    acts = [ProjectActivity(project_id=p.id, activity_master_id=m.id, planned_start=date.today()) for m in masters]
    db.add_all(acts)
    db.flush()

    deps = [
        (acts[0].id, acts[1].id),
        (acts[1].id, acts[2].id),
        (acts[2].id, acts[3].id),
        (acts[3].id, acts[4].id),
        (acts[4].id, acts[5].id),
    ]
    db.add_all([
        Dependency(project_id=p.id, predecessor_project_activity_id=a, successor_project_activity_id=b, relationship_type="FS", lag_hours=0)
        for a, b in deps
    ])

    for gate in ["G1", "G2", "G3", "G4"]:
        db.add(Gate(project_id=p.id, gate_code=gate, status="pending"))

    material = Material(part_number="PHE-001", description="PHE line", category="internal", criticality="high", default_lead_days=5)
    db.add(material)
    db.flush()
    req = MaterialRequirement(
        project_id=p.id,
        project_activity_id=acts[1].id,
        material_id=material.id,
        quantity=1,
        need_by_date=date.today(),
        ownership="etw",
        status="planned",
    )
    db.add(req)
    db.flush()
    db.add(MaterialOrder(material_requirement_id=req.id, status="ordered", supplier_name="Supplier-A"))

    db.commit()
    print("Seed complete")


if __name__ == "__main__":
    run()
