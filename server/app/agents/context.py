from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.repositories.hcp import hcp_repository
from app.schemas.interaction import map_hcp_id_to_uuid, map_uuid_to_hcp_id


def load_available_doctors(db: Session, *, limit: int = 100) -> list[dict[str, str]]:
    hcps = hcp_repository.list(db, limit=limit)
    return [
        {"id": str(hcp.id), "name": f"Dr. {hcp.first_name} {hcp.last_name}"}
        for hcp in hcps
    ]


def normalize_form_for_agent(current_form: dict[str, Any]) -> dict[str, Any]:
    form = dict(current_form)
    doctor_id = form.get("doctorId")
    if doctor_id:
        try:
            form["doctorId"] = str(map_hcp_id_to_uuid(doctor_id))
        except ValueError:
            pass
    return form


def build_extracted_fields(
    *,
    current_form: dict[str, Any],
    doctor_id: str | None,
    visit_type: str | None,
    interaction_date: str | None,
    products_discussed: list[str] | None,
    notes: str | None,
    follow_up_date: str | None,
    objective: str | None,
    summary: str | None,
    outcome: str | None,
    today: str,
) -> dict[str, Any]:
    products = products_discussed or []
    products_str = ", ".join(products) if products else current_form.get("productsDiscussed", "")

    mapped_doc_id = ""
    if doctor_id:
        mapped_doc_id = map_uuid_to_hcp_id(doctor_id)
    elif current_form.get("doctorId"):
        mapped_doc_id = map_uuid_to_hcp_id(current_form["doctorId"])

    return {
        "doctorId": mapped_doc_id,
        "visitType": visit_type or current_form.get("visitType", "In-person"),
        "date": interaction_date or current_form.get("date", today),
        "productsDiscussed": products_str,
        "notes": notes if notes is not None else current_form.get("notes", ""),
        "followUpDate": follow_up_date if follow_up_date is not None else current_form.get("followUpDate", ""),
        "objective": objective or "",
        "summary": summary or "",
        "outcome": outcome or "",
    }


def format_doctors_list(doctors: list[dict[str, str]]) -> str:
    if not doctors:
        return "(No doctors in database)"
    return "\n".join(f"- {doctor['name']} (ID: {doctor['id']})" for doctor in doctors)


def format_form_context(form: dict[str, Any]) -> str:
    return (
        f"- Doctor ID: {form.get('doctorId')}\n"
        f"- Visit Type: {form.get('visitType')}\n"
        f"- Interaction Date: {form.get('date')}\n"
        f"- Products Discussed: {form.get('productsDiscussed')}\n"
        f"- Notes: {form.get('notes')}\n"
        f"- Follow-up Date: {form.get('followUpDate')}"
    )


def today_iso() -> str:
    return date.today().isoformat()
