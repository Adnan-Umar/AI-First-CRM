from typing import Literal

from pydantic import BaseModel, Field

AgentIntent = Literal[
    "log_interaction",
    "edit_interaction",
    "search_history",
    "follow_up_plan",
    "summarize_interaction",
]

INTENT_LABELS: dict[AgentIntent, str] = {
    "log_interaction": "Log Interaction",
    "edit_interaction": "Edit Interaction",
    "search_history": "Search Interaction History",
    "follow_up_plan": "Generate Follow-up Plan",
    "summarize_interaction": "Summarize Interaction",
}


class RouteDecision(BaseModel):
    intent: AgentIntent = Field(
        description=(
            "The tool to invoke: log_interaction (capture a new visit), "
            "edit_interaction (modify an existing record), search_history (find past visits), "
            "follow_up_plan (plan next steps), summarize_interaction (condense visit details)."
        )
    )
    reasoning: str = Field(description="Brief reason for choosing this tool.")


class LogInteractionOutput(BaseModel):
    doctor_id: str | None = Field(
        default=None,
        description="UUID of the doctor from the available list, or keep current value.",
    )
    visit_type: str | None = Field(
        default=None,
        description="Visit channel: In-person, Call, or Video.",
    )
    date: str | None = Field(default=None, description="Interaction date in YYYY-MM-DD format.")
    products_discussed: list[str] = Field(
        default_factory=list,
        description="Products discussed during the visit.",
    )
    notes: str | None = Field(default=None, description="Free-form interaction notes.")
    follow_up_date: str | None = Field(default=None, description="Follow-up date in YYYY-MM-DD format.")
    objective: str | None = Field(default=None, description="Purpose of the interaction.")
    summary: str | None = Field(default=None, description="Short professional summary.")
    outcome: str | None = Field(default=None, description="Outcome or next actions.")
    reply: str = Field(description="Friendly response explaining captured fields.")


class EditInteractionOutput(BaseModel):
    interaction_id: str | None = Field(
        default=None,
        description="UUID of the interaction to edit, if explicitly known.",
    )
    doctor_name: str | None = Field(
        default=None,
        description="Doctor name to locate the interaction when ID is unknown.",
    )
    interaction_date: str | None = Field(
        default=None,
        description="Date of the interaction to locate when ID is unknown.",
    )
    visit_type: str | None = None
    date: str | None = None
    products_discussed: list[str] | None = None
    notes: str | None = None
    follow_up_date: str | None = None
    objective: str | None = None
    summary: str | None = None
    outcome: str | None = None
    reply: str = Field(description="Response describing what was updated or why it failed.")


class SearchHistoryOutput(BaseModel):
    doctor_name: str | None = Field(default=None, description="Filter by doctor name.")
    visit_type: str | None = Field(default=None, description="Filter by visit channel.")
    date_from: str | None = Field(default=None, description="Start date YYYY-MM-DD.")
    date_to: str | None = Field(default=None, description="End date YYYY-MM-DD.")
    reply: str = Field(description="Natural language summary of search criteria and results.")


class FollowUpPlanOutput(BaseModel):
    doctor_name: str | None = Field(default=None, description="Doctor for follow-up planning.")
    interaction_id: str | None = Field(default=None, description="Specific interaction UUID if known.")
    reply: str = Field(description="Structured follow-up plan for the sales rep.")


class SummarizeInteractionOutput(BaseModel):
    interaction_id: str | None = Field(default=None, description="Interaction UUID if known.")
    doctor_name: str | None = Field(default=None, description="Doctor name to locate interaction.")
    interaction_date: str | None = Field(default=None, description="Date to locate interaction.")
    reply: str = Field(description="Concise summary of the interaction.")
