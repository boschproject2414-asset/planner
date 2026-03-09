import pandas as pd

from app.db.session import SessionLocal
from app.models.models import ActivityMaster


def run(path: str) -> None:
    df = pd.read_excel(path)
    db = SessionLocal()
    for _, row in df.iterrows():
        db.add(
            ActivityMaster(
                phase=str(row.get("Phase", "Mechanical")),
                main_activity=str(row.get("Main Activity", "Unknown")),
                sub_activity=str(row.get("Sub Activity", "Unknown")),
                default_effort_hours=float(row.get("Effort Hours", 0) or 0),
                gate_suggestion=str(row.get("Gate", "")) or None,
                requires_customer_parts=bool(row.get("Customer Parts", False)),
            )
        )
    db.commit()
    print(f"Imported {len(df)} rows")


if __name__ == "__main__":
    import sys

    run(sys.argv[1])
