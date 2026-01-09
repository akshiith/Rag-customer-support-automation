def detect_intent(query: str) -> str:
    q = query.lower()

    if "password" in q or "reset" in q:
        return "password_reset"
    if "refund" in q or "return" in q:
        return "refund_request"
    if "payment" in q:
        return "payment_issue"

    return "general_support"
