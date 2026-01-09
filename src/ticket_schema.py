from pydantic import BaseModel
from typing import Optional
from uuid import uuid4

class SupportTicket(BaseModel):
    ticket_id: str
    user_email: str
    subject: str
    message: str
    status: str = "OPEN"

def create_ticket(user_email: str, subject: str, message: str) -> SupportTicket:
    return SupportTicket(
        ticket_id=str(uuid4()),
        user_email=user_email,
        subject=subject,
        message=message,
        status="OPEN"
    )
