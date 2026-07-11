from typing import Any

from app.agents.context import (
    build_extracted_fields,
    format_doctors_list,
    format_form_context,
)
from app.agents.llm import create_structured_llm, get_groq_api_key
from app.agents.schemas import LogInteractionOutput
from app.agents.state import AgentState

DEMO_REPLY = (
    "I'm running in demo mode. Please set GROQ_API_KEY in the server .env file "
    "to enable AI-assisted interaction logging."
)


def log_interaction_tool(state: AgentState) -> dict[str, Any]:
    if not get_groq_api_key():
        extracted_fields = build_extracted_fields(
            current_form=state["current_form"],
            doctor_id=state["current_form"].get("doctorId") or None,
            visit_type=state["current_form"].get("visitType"),
            interaction_date=state["current_form"].get("date") or state["today"],
            products_discussed=None,
            notes=state["current_form"].get("notes"),
            follow_up_date=state["current_form"].get("followUpDate") or None,
            objective=None,
            summary=None,
            outcome=None,
            today=state["today"],
        )
        return {
            "reply": state.get("reply") or DEMO_REPLY,
            "extracted_fields": extracted_fields,
        }

    try:
        structured_llm = create_structured_llm(LogInteractionOutput)
    except Exception as exc:
        return {"reply": f"Error initializing Log Interaction tool: {exc}", "extracted_fields": None}

    doctors_list = format_doctors_list(state["available_doctors"])
    form_context = format_form_context(state["current_form"])

    system_prompt = (
        "You are the Log Interaction tool in an AI-First CRM.\n"
        "Extract or update structured visit details from the user's message.\n"
        "Keep existing form values unless the user clearly overrides them.\n"
        "Map doctor mentions to IDs from the available list.\n"
        "Parse relative dates against today's date.\n"
        "Synthesize objective, summary, and outcome when notes are provided.\n\n"
        f"Today's date: {state['today']}\n\n"
        f"Available doctors:\n{doctors_list}\n\n"
        f"Current form values:\n{form_context}"
    )

    try:
        result: LogInteractionOutput = structured_llm.invoke(
            [
                ("system", system_prompt),
                ("human", state["message"]),
            ]
        )
    except Exception as exc:
        return {
            "reply": f"I couldn't parse the interaction automatically: {exc}",
            "extracted_fields": None,
        }

    extracted_fields = build_extracted_fields(
        current_form=state["current_form"],
        doctor_id=result.doctor_id,
        visit_type=result.visit_type,
        interaction_date=result.date,
        products_discussed=result.products_discussed,
        notes=result.notes,
        follow_up_date=result.follow_up_date,
        objective=result.objective,
        summary=result.summary,
        outcome=result.outcome,
        today=state["today"],
    )

    return {"reply": result.reply, "extracted_fields": extracted_fields}