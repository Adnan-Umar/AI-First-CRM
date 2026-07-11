from typing import Any

from app.agents.context import format_doctors_list, format_form_context
from app.agents.llm import create_structured_llm, get_groq_api_key
from app.agents.schemas import AgentIntent, RouteDecision
from app.agents.state import AgentState

DEMO_REPLY = (
    "I'm running in demo mode. Please set GROQ_API_KEY in the server .env file "
    "to enable full AI routing."
)


def _fallback_intent(message: str) -> AgentIntent:
    lowered = message.lower()
    if any(word in lowered for word in ("edit", "update", "change", "modify", "correct")):
        return "edit_interaction"
    if any(word in lowered for word in ("search", "find", "show", "list", "history", "past")):
        return "search_history"
    if "follow-up" in lowered or "follow up" in lowered or "next steps" in lowered:
        return "follow_up_plan"
    if "summarize" in lowered or "summary" in lowered or "recap" in lowered:
        return "summarize_interaction"
    return "log_interaction"


def route_intent(state: AgentState) -> dict[str, Any]:
    if not get_groq_api_key():
        return {
            "intent": _fallback_intent(state["message"]),
            "reply": DEMO_REPLY,
        }

    try:
        structured_llm = create_structured_llm(RouteDecision)
    except Exception as exc:
        return {
            "intent": _fallback_intent(state["message"]),
            "reply": f"Error initializing AI router: {exc}",
        }

    doctors_list = format_doctors_list(state["available_doctors"])
    form_context = format_form_context(state["current_form"])

    system_prompt = (
        "You are the intent router for an AI-First CRM used by pharmaceutical sales reps.\n"
        "Choose exactly one tool based on the user's message:\n"
        "- log_interaction: user is logging or describing a new HCP visit\n"
        "- edit_interaction: user wants to change an existing interaction record\n"
        "- search_history: user wants to find or review past interactions\n"
        "- follow_up_plan: user wants a follow-up action plan for an HCP or visit\n"
        "- summarize_interaction: user wants a concise recap of a visit\n\n"
        f"Today's date: {state['today']}\n\n"
        f"Available doctors:\n{doctors_list}\n\n"
        f"Current form context:\n{form_context}"
    )

    try:
        decision: RouteDecision = structured_llm.invoke(
            [
                ("system", system_prompt),
                ("human", state["message"]),
            ]
        )
        return {"intent": decision.intent}
    except Exception:
        return {"intent": _fallback_intent(state["message"])}


def route_to_tool(state: AgentState) -> AgentIntent:
    return state["intent"] or "log_interaction"
