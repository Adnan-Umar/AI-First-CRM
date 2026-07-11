from datetime import date
from typing import Any

from app.agents.helpers import find_interaction, format_interaction_record, interaction_to_dict
from app.agents.llm import create_structured_llm, get_groq_api_key
from app.agents.schemas import EditInteractionOutput
from app.agents.state import AgentState
from app.repositories.interaction import interaction_repository

DEMO_REPLY = (
    "I'm running in demo mode. Please set GROQ_API_KEY in the server .env file "
    "to enable AI-assisted interaction editing."
)


def edit_interaction_tool(state: AgentState) -> dict[str, Any]:
    if not get_groq_api_key():
        return {"reply": DEMO_REPLY, "extracted_fields": {"action": "edit_interaction"}}

    try:
        structured_llm = create_structured_llm(EditInteractionOutput)
    except Exception as exc:
        return {"reply": f"Error initializing Edit Interaction tool: {exc}", "extracted_fields": None}

    system_prompt = (
        "You are the Edit Interaction tool in an AI-First CRM.\n"
        "Identify which interaction the user wants to change and which fields to update.\n"
        "Only set fields the user explicitly wants to change.\n"
        "Use interaction_id when provided; otherwise use doctor_name and/or interaction_date.\n\n"
        f"Today's date: {state['today']}"
    )

    try:
        parsed: EditInteractionOutput = structured_llm.invoke(
            [
                ("system", system_prompt),
                ("human", state["message"]),
            ]
        )
    except Exception as exc:
        return {"reply": f"I couldn't parse the edit request: {exc}", "extracted_fields": None}

    interaction = find_interaction(
        state["db"],
        interaction_id=parsed.interaction_id,
        doctor_name=parsed.doctor_name,
        interaction_date=parsed.interaction_date,
    )

    if interaction is None:
        return {
            "reply": (
                parsed.reply
                if parsed.reply
                else "I couldn't find a matching interaction to edit. Please specify the doctor or date."
            ),
            "extracted_fields": {"action": "edit_interaction", "updated": False},
        }

    updates: dict[str, Any] = {}
    if parsed.visit_type is not None:
        updates["visit_type"] = parsed.visit_type
    if parsed.date is not None:
        try:
            updates["date"] = date.fromisoformat(parsed.date)
        except ValueError:
            pass
    if parsed.products_discussed is not None:
        updates["products_discussed"] = parsed.products_discussed
    if parsed.notes is not None:
        updates["notes"] = parsed.notes
    if parsed.follow_up_date is not None:
        try:
            updates["follow_up_date"] = date.fromisoformat(parsed.follow_up_date)
        except ValueError:
            pass
    if parsed.objective is not None:
        updates["objective"] = parsed.objective
    if parsed.summary is not None:
        updates["summary"] = parsed.summary
    if parsed.outcome is not None:
        updates["outcome"] = parsed.outcome

    if not updates:
        return {
            "reply": parsed.reply or "No changes were detected. Tell me which fields to update.",
            "extracted_fields": {
                "action": "edit_interaction",
                "updated": False,
                "interaction": interaction_to_dict(interaction),
            },
        }

    updated = interaction_repository.update(state["db"], interaction, updates)
    refreshed = interaction_repository.get(state["db"], updated.id)
    record = refreshed or updated
    return {
        "reply": parsed.reply or "Interaction updated successfully.",
        "extracted_fields": {
            "action": "edit_interaction",
            "updated": True,
            "interaction": interaction_to_dict(record),
            "record": format_interaction_record(record),
        },
    }
