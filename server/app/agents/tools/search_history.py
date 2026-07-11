from datetime import date
from typing import Any

from app.agents.helpers import interaction_to_dict, search_interactions
from app.agents.llm import create_structured_llm, get_groq_api_key
from app.agents.schemas import SearchHistoryOutput
from app.agents.state import AgentState

DEMO_REPLY = (
    "I'm running in demo mode. Please set GROQ_API_KEY in the server .env file "
    "to enable AI-assisted history search."
)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def search_history_tool(state: AgentState) -> dict[str, Any]:
    if not get_groq_api_key():
        interactions = search_interactions(state["db"], limit=10)
        if not interactions:
            return {"reply": DEMO_REPLY, "extracted_fields": {"action": "search_history", "results": []}}
        lines = [
            f"- {item.date.isoformat()} | {item.visit_type} | "
            f"Dr. {item.hcp.first_name} {item.hcp.last_name if item.hcp else 'Unknown'}"
            for item in interactions
        ]
        return {
            "reply": DEMO_REPLY + "\n\nRecent interactions:\n" + "\n".join(lines),
            "extracted_fields": {
                "action": "search_history",
                "results": [interaction_to_dict(item) for item in interactions],
            },
        }

    try:
        structured_llm = create_structured_llm(SearchHistoryOutput)
    except Exception as exc:
        return {"reply": f"Error initializing Search History tool: {exc}", "extracted_fields": None}

    system_prompt = (
        "You are the Search Interaction History tool in an AI-First CRM.\n"
        "Extract search filters from the user's message.\n"
        "Leave filters empty when not specified.\n\n"
        f"Today's date: {state['today']}"
    )

    try:
        parsed: SearchHistoryOutput = structured_llm.invoke(
            [
                ("system", system_prompt),
                ("human", state["message"]),
            ]
        )
    except Exception as exc:
        return {"reply": f"I couldn't parse the search request: {exc}", "extracted_fields": None}

    interactions = search_interactions(
        state["db"],
        doctor_name=parsed.doctor_name,
        visit_type=parsed.visit_type,
        date_from=_parse_date(parsed.date_from),
        date_to=_parse_date(parsed.date_to),
        limit=20,
    )

    results = [interaction_to_dict(item) for item in interactions]
    if not interactions:
        reply = parsed.reply or "No interactions matched your search criteria."
    else:
        lines = [
            f"- {item.date.isoformat()} | {item.visit_type} | "
            f"Dr. {item.hcp.first_name} {item.hcp.last_name if item.hcp else 'Unknown'} | "
            f"{item.objective or item.summary or 'No summary'}"
            for item in interactions
        ]
        reply = (parsed.reply or "Here are the matching interactions:") + "\n\n" + "\n".join(lines)

    return {
        "reply": reply,
        "extracted_fields": {
            "action": "search_history",
            "filters": {
                "doctorName": parsed.doctor_name,
                "visitType": parsed.visit_type,
                "dateFrom": parsed.date_from,
                "dateTo": parsed.date_to,
            },
            "results": results,
        },
    }
