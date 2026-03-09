from sqlalchemy.orm import Session

from app.models.models import AuditLog


def log_audit(
    db: Session,
    *,
    actor_user_id: int | None,
    entity_type: str,
    entity_id: int,
    action: str,
    before_json: dict | None,
    after_json: dict | None,
) -> None:
    db.add(
        AuditLog(
            actor_user_id=actor_user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            before_json=before_json,
            after_json=after_json,
        )
    )
