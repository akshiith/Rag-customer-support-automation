def decide_action(intent: str, confidence: float) -> str:
    """
    Automation rules:
    - Sensitive intents never auto-send
    - Confidence gates automation
    """

    # Sensitive flows
    if intent in {"refund_request", "payment_issue"}:
        if confidence >= 0.6:
            return "SAVE_DRAFT"
        return "ESCALATE"

    # Low-risk flows
    if intent == "password_reset":
        if confidence >= 0.75:
            return "PENDING_APPROVAL"
        elif confidence >= 0.4:
            return "SAVE_DRAFT"
        return "ESCALATE"

    return "ESCALATE"
