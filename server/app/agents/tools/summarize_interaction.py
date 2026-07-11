from typing import Any

from app.agents.helpers import find_interaction, format_interaction_record
from app.agents.llm import create_llm, create_structured_llm, get_groq_api_key
from app.agents.schemas import SummarizeInteractionOutput
from app.agents.state import AgentState

DEMO_REPLY = (
    "I'm running in demo mode. Please set GROQ_API_KEY in the server .env file "
    "to enable interaction summarization."
)


def _build_context_from_form(form: dict[str, Any]) -> str:
    return (
        f"Doctor ID: {form.get('doctorId', 'Unknown')}\n"
        f"Visit Type: {form.get('visitType', 'Unknown')}\n"
        f"Date: {form.get('date', 'Unknown')}\n"
        f"Products: {form.get('productsDiscussed', 'None')}\n"
        f"Notes: {form.get('notes', 'None')}"
    )


def summarize_interaction_tool(state: AgentState) -> dict[str, Any]:
    if not get_groq_api_key():
        notes = state["current_form"].get("notes") or "No notes available."
        return {
            "reply": DEMO_REPLY + f"\n\nDraft summary from current form:\n{notes[:300]}",
            "extracted_fields": {"action": "summarize_interaction", "summary": notes[:300]},
        }

    try:
        structured_llm = create_structured_llm(SummarizeInteractionOutput)
    except Exception as exc:
        return {"reply": f"Error initializing Summarize Interaction tool: {exc}", "extracted_fields": None}

    try:
        parsed: SummarizeInteractionOutput = structured_llm.invoke(
            [
                (
                    "system",
                    "Identify which interaction the user wants summarized using interaction_id, "
                    "doctor_name, and/or interaction_date when available.",
                ),
                ("human", state["message"]),
            ]
        )
    except Exception as exc:
        return {"reply": f"I couldn't parse the summarize request: {exc}", "extracted_fields": None}

    interaction = find_interaction(
        state["db"],
        interaction_id=parsed.interaction_id,
        doctor_name=parsed.doctor_name,
        interaction_date=parsed.interaction_date,
    )

    if interaction:
        context = format_interaction_record(interaction)
    else:
        context = _build_context_from_form(state["current_form"])

    try:
        llm = create_llm()
        summary_response = llm.invoke(
            [
                (
                    "system",
                    "Summarize the interaction in 3-5 concise bullet points for a CRM record. "
                    "Cover objective, key discussion points, outcome, and follow-up.",
                ),
                (
                    "human",
                    f"User request:\n{state['message']}\n\nInteraction context:\n{context}",
                ),
            ]
        )
        content = summary_response.content
        reply = content if isinstance(content, str) else str(content)
    except Exception as exc:
        reply = parsed.reply or f"I couldn't summarize the interaction: {exc}"

    return {
        "reply": reply,
        "extracted_fields": {
            "action": "summarize_interaction",
            "summary": reply,
            "interactionId": parsed.interaction_id,
            "doctorName": parsed.doctor_name,
        },
    }
