from pydantic import BaseModel, Field
from typing import Optional

class TicketCategory(BaseModel):
    department: str = Field(description="Department: Billing / Technical / Account / Other")
    urgency: str = Field(description="Urgency: Critical / High / Normal / Low")

class TicketSummary(BaseModel):
    issue_summary: str = Field(description="A brief 1-sentence summary of the issue")
    root_cause: str = Field(description="Suspected root cause of the problem")
    suggested_action: str = Field(description="Action the support team should take next")
    sentiment: str = Field(description="Customer sentiment: Angry / Neutral / Satisfied")

class GraphState(BaseModel):
    ticket_id: str
    subject: str
    body: str
    category: Optional[TicketCategory] = None
    summary: Optional[TicketSummary] = None
    draft_reply: Optional[str] = None
