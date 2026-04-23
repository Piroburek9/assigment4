CATEGORIZATION_PROMPT = """
You are an expert customer support routing assistant.
Your job is to analyze the following support ticket and classify its department and urgency.

Ticket Subject: {subject}
Ticket Body: {body}
"""

SUMMARY_PROMPT = """
You are a senior support analyst. Read the support ticket and provide a structured summary, root cause analysis, suggested action, and customer sentiment.

Ticket Subject: {subject}
Ticket Body: {body}
Department: {department}
Urgency: {urgency}
"""

DRAFT_REPLY_PROMPT = """
You are a customer success manager handling a CRITICAL urgency ticket. 
Draft a professional, empathetic, and reassuring reply to the customer. 
Acknowledge their issue, explain that the team is working on it, and set a high-priority expectation.

Ticket Subject: {subject}
Ticket Body: {body}
Suggested Action: {suggested_action}
"""
