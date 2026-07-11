from typing import Any

from app.agents.helpers import find_interaction, format_interaction_record
from app.agents.llm import CONTEXT_MODEL, create_llm, create_structured_llm, get_groq_api_key
from app.agents.schemas import FollowUpPlanOutput
from app.agents.state import AgentState

DEMO_REPLY = (
    "I'm running in demo mode. Please set GROQ_API_KEY in the server .env file "
    "to enable follow-up plan generation."
)


def _build_context_from_form(form: dict[str, Any]) -> str:
    return (
        f"Doctor ID: {form.get('doctorId', 'Unknown')}\n"
        f"Visit Type: {form.get('visitType', 'Unknown')}\n"
        f"Date: {form.get('date', 'Unknown')}\n"
        f"Products: {form.get('productsDiscussed', 'None')}\n"
        f"Notes: {form.get('notes', 'None')}\n"
        f"Follow-up Date: {form.get('followUpDate', 'None')}"
    )


def follow_up_plan_tool(state: AgentState) -> dict[str, Any]:
    if not get_groq_api_key():
        return {"reply": DEMO_REPLY, "extracted_fields": {"action": "follow_up_plan"}}

    try:
        structured_llm = create_structured_llm(FollowUpPlanOutput)
    except Exception as exc:
        return {"reply": f"Error initializing Follow-up Plan tool: {exc}", "extracted_fields": None}

    try:
        parsed: FollowUpPlanOutput = structured_llm.invoke(
            [
                (
                    "system",
                    "Extract which doctor or interaction the follow-up plan should be based on.",
                ),
                ("human", state["message"]),
            ]
        )
    except Exception as exc:
        return {"reply": f"I couldn't parse the follow-up request: {exc}", "extracted_fields": None}

    interaction = find_interaction(
        state["db"],
        interaction_id=parsed.interaction_id,
        doctor_name=parsed.doctor_name,
    )

    if interaction:
        context = format_interaction_record(interaction)
    else:
        context = _build_context_from_form(state["current_form"])

    try:
        llm = create_llm(temperature=0.3, model=CONTEXT_MODEL)
        plan_response = llm.invoke(
            [
                (
                    "system",
                    "You are a pharmaceutical sales coach. Create a practical follow-up plan with:\n"
                    "1. Key objectives\n2. Talking points\n3. Recommended channel and timing\n"
                    "4. Risks or objections to prepare for\n5. Success metrics",
                ),
                (
                    "human",
                    f"User request:\n{state['message']}\n\nInteraction context:\n{context}",
                ),
            ]
        )
        content = plan_response.content
        reply = content if isinstance(content, str) else str(content)
    except Exception as exc:
        reply = parsed.reply or f"I couldn't generate a follow-up plan: {exc}"

    return {
        "reply": reply,
        "extracted_fields": {
            "action": "follow_up_plan",
            "doctorName": parsed.doctor_name,
            "interactionId": parsed.interaction_id,
        },
    }
