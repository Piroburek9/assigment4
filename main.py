import os
from dotenv import load_dotenv
from langsmith import traceable
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
pip install -U google-genai langsmith


from models import GraphState, TicketCategory, TicketSummary
from prompts import CATEGORIZATION_PROMPT, SUMMARY_PROMPT, DRAFT_REPLY_PROMPT

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

categorize_llm = llm.with_structured_output(TicketCategory)
summarize_llm = llm.with_structured_output(TicketSummary)

def ingest_ticket(state: GraphState) -> GraphState:
    print(f"--- INGESTING TICKET: {state.ticket_id} ---")
    return state

@traceable
def categorize_ticket(state: GraphState) -> GraphState:
    print("--- CATEGORIZING TICKET ---")
    prompt = CATEGORIZATION_PROMPT.format(subject=state.subject, body=state.body)
    category_result = categorize_llm.invoke(prompt)
    state.category = category_result
    return state

@traceable
def summarize_ticket(state: GraphState) -> GraphState:
    print("--- SUMMARIZING TICKET ---")
    prompt = SUMMARY_PROMPT.format(
        subject=state.subject, 
        body=state.body,
        department=state.category.department,
        urgency=state.category.urgency
    )
    summary_result = summarize_llm.invoke(prompt)
    state.summary = summary_result
    return state

@traceable
def draft_critical_reply(state: GraphState) -> GraphState:
    print("--- DRAFTING CRITICAL REPLY ---")
    prompt = DRAFT_REPLY_PROMPT.format(
        subject=state.subject,
        body=state.body,
        suggested_action=state.summary.suggested_action
    )
    reply_result = llm.invoke(prompt)
    state.draft_reply = reply_result.content
    return state

def check_urgency(state: GraphState) -> str:
    if state.category.urgency.upper() == "CRITICAL":
        return "draft_reply"
    return "end"

workflow = StateGraph(GraphState)

workflow.add_node("ingest", ingest_ticket)
workflow.add_node("categorize", categorize_ticket)
workflow.add_node("summarize", summarize_ticket)
workflow.add_node("draft_reply", draft_critical_reply)

workflow.add_edge(START, "ingest")
workflow.add_edge("ingest", "categorize")
workflow.add_edge("categorize", "summarize")

workflow.add_conditional_edges(
    "summarize",
    check_urgency,
    {
        "draft_reply": "draft_reply",
        "end": END
    }
)

workflow.add_edge("draft_reply", END)

app = workflow.compile()

if __name__ == "__main__":
    test_ticket = GraphState(
        ticket_id="TKT-9942",
        subject="SERVER DOWN - Entire production database deleted!",
        body="Help! One of our junior devs accidentally dropped the main production database table. The website is throwing 500 errors everywhere and we are losing thousands of dollars a minute. Please restore from backup immediately!"
    )

    print("\nStarting LangGraph Pipeline...")
    final_state = app.invoke(test_ticket)
    
    print("\n" + "="*40)
    print("🎯 PIPELINE RESULTS")
    print("="*40)
    print(f"Category:  {final_state['category'].department}")
    print(f"Urgency:   {final_state['category'].urgency}")
    print(f"Sentiment: {final_state['summary'].sentiment}")
    print(f"Root Cause:{final_state['summary'].root_cause}")
    print(f"Action:    {final_state['summary'].suggested_action}")
    
    if final_state.get('draft_reply'):
        print("\n📧 DRAFT REPLY:")
        print(final_state['draft_reply'])
