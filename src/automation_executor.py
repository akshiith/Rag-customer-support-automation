from draft_store import save_draft
from email_adapter import build_email
from ticket_schema import create_ticket


def handle_automation(decision: str, query: str, intent: str, context: str):
    """
    Execute automation based on decision
    """

    if decision == "PENDING_APPROVAL":
        email = build_email(
            subject=f"Support Response: {intent.replace('_', ' ').title()}",
            body=context
        )
        return {
            "status": "pending_approval",
            "email_preview": email
        }

    if decision == "SAVE_DRAFT":
        draft_id = save_draft(
            subject=f"Draft: {intent.replace('_', ' ').title()}",
            body=context
        )
        return {
            "status": "draft_saved",
            "draft_id": draft_id
        }

    if decision == "ESCALATE":
        ticket = create_ticket(
            title=f"Escalated Issue: {intent}",
            description=query,
            context=context
        )
        return {
            "status": "escalated",
            "ticket_id": ticket["id"]
        }

    return {"status": "ignored"}
