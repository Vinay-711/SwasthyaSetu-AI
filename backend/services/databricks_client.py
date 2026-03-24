import os
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any

_USE_DATABRICKS = bool(os.getenv("DATABRICKS_HOST") and os.getenv("DATABRICKS_TOKEN"))
LOCAL_DB_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "local_db.json")
)


def _load_db() -> Dict[str, Any]:
    """Load the local JSON database."""
    if not os.path.exists(LOCAL_DB_FILE):
        return {"patients": {}, "notifications": {}}
    try:
        with open(LOCAL_DB_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"patients": {}, "notifications": {}}


def _save_db(data: Dict[str, Any]) -> None:
    """Save to the local JSON database."""
    with open(LOCAL_DB_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _get_sdk():
    if not _USE_DATABRICKS:
        return None
    from databricks.sdk import WorkspaceClient  # type: ignore[import-untyped]
    return WorkspaceClient(
        host=os.getenv("DATABRICKS_HOST"),
        token=os.getenv("DATABRICKS_TOKEN"),
    )


def create_patient(data: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a new patient record (Delta Lake or JSON fallback)."""
    patient_id = str(uuid.uuid4())[:8].upper()  # type: ignore[has-type]
    record = {
        "patient_id": patient_id,
        "created_at": datetime.utcnow().isoformat(),
        **data,
    }

    if _USE_DATABRICKS:
        # In a real deployment, use spark.sql or SDK to write to Delta
        pass

    db = _load_db()
    db["patients"][patient_id] = record
    _save_db(db)
    return record


def get_patient(patient_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a patient record by ID."""
    db = _load_db()
    return db["patients"].get(patient_id)


def save_notification(notification: Dict[str, Any]) -> None:
    """Persist a notification record."""
    pid = notification.get("patient_id", "unknown")
    db = _load_db()
    if pid not in db["notifications"]:
        db["notifications"][pid] = []
    db["notifications"][pid].append(notification)
    _save_db(db)


def get_notifications(patient_id: str) -> list:
    """Retrieve notification history for a patient."""
    db = _load_db()
    return db["notifications"].get(patient_id, [])
