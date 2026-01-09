from datetime import datetime
from pathlib import Path
import json
from typing import Optional, List, Dict

# Directory where drafts are persisted
DRAFT_DIR = Path("drafts")
DRAFT_DIR.mkdir(exist_ok=True)

# Allowed workflow states
ALLOWED_STATUSES = {
    "SAVE_DRAFT",
    "PENDING_APPROVAL",
    "ADMIN_DRAFT",
    "APPROVED",
    "SENT",
    "ESCALATED"
}


def save_draft(
    ticket_id: str,
    email: Dict[str, str],
    body: str,
    confidence: float,
    status: str = "SAVE_DRAFT",
    gmail_draft_id: Optional[str] = None
) -> str:
    """
    Persist a ticket draft to disk.
    This is the single source of truth for approval + Gmail workflow.
    """

    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid draft status: {status}")

    data = {
        "ticket_id": ticket_id,
        "email": email,  # {"to": "...", "subject": "..."}
        "draft": body,
        "confidence": confidence,
        "status": status,
        "gmail_draft_id": gmail_draft_id,
        "timestamp": datetime.utcnow().isoformat()
    }

    path = DRAFT_DIR / f"draft_{ticket_id}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return str(path)


def load_draft(ticket_id: str) -> Optional[Dict]:
    """
    Load a draft by ticket_id.
    """
    path = DRAFT_DIR / f"draft_{ticket_id}.json"

    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_pending_approvals() -> List[Dict]:
    """
    Return drafts that still require human action.
    """
    drafts: List[Dict] = []

    for path in DRAFT_DIR.glob("draft_*.json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

            if data.get("status") in {
                "PENDING_APPROVAL",
                "SAVE_DRAFT",
                "ADMIN_DRAFT"
            }:
                drafts.append(data)

    return drafts


def update_status(ticket_id: str, new_status: str) -> None:
    """
    Update the workflow status of an existing draft.
    """

    if new_status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid status transition: {new_status}")

    draft = load_draft(ticket_id)
    if not draft:
        raise FileNotFoundError(f"Draft not found for ticket_id={ticket_id}")

    draft["status"] = new_status
    draft["timestamp"] = datetime.utcnow().isoformat()

    path = DRAFT_DIR / f"draft_{ticket_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(draft, f, indent=2)
