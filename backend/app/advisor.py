"""Server-side context assembly and LLM call for the AI Advisor.

The Advisor is read-only: it explains, compares, and prioritizes using data
already computed elsewhere (the deterministic matching engine in
app.matching, plus real scholarship/application/document records). It never
re-derives eligibility, never invents scholarship facts, and never changes
any OmerPath state. The frontend never talks to the LLM provider directly -
only app.llm_provider does, using a server-side API key. This module has no
provider-specific code, so the provider/model in app.llm_provider can be
swapped later without changing anything here.
"""
import json
import logging
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.advisor_errors import AdvisorConfigError, AdvisorNotFoundError, AdvisorProviderError  # noqa: F401 - re-exported for app.routes.advisor
from app.llm_provider import generate_json_reply
from app.matching import compute_match
from app.models.academic_profile import AcademicProfile
from app.models.application import Application
from app.models.document import Document
from app.models.profile import Profile
from app.models.saved_scholarship import SavedScholarship
from app.models.scholarship import Scholarship

logger = logging.getLogger("omerpath.advisor")

MAX_HISTORY_MESSAGES = 8

SYSTEM_PROMPT = """You are the OmerPath Advisor, a scholarship and application assistant built into the OmerPath platform.

You help students with:
- explaining scholarship eligibility and match results
- comparing scholarships
- identifying unmet or unknown eligibility criteria
- prioritizing which scholarships or applications to focus on
- application next steps and progress guidance
- document readiness and identifying missing documents
- interpreting deadlines and requirements when verified data exists

You are NOT a generic chatbot. Politely redirect if asked about anything unrelated to the student's OmerPath scholarships, applications, documents, or profile.

Ground rules - never break these:
1. Only use facts given to you in the OMERPATH DATA section below. Never invent scholarship requirements, deadlines, funding amounts, or application status.
2. Eligibility status (eligible/ineligible/unknown) and fit scores are computed by OmerPath's own deterministic matching engine and handed to you already computed. Explain and contextualize them - never recompute your own eligibility judgment and never contradict them.
3. Clearly distinguish what is KNOWN, UNMET, and UNKNOWN. If a criterion's status is "unknown", say it is unknown - never state or imply the student is eligible when the underlying criterion is unknown.
4. If the data needed to answer isn't present below, say so plainly rather than guessing.
5. When discussing a specific scholarship's requirements or deadline, mention its official source if one is present in the data.
6. You cannot take any action. You cannot submit applications, change application status, save or unsave scholarships, upload or delete documents, or edit profile information. If asked to do one of these, explain that you can only advise, not act.
7. Keep answers concise and directly useful.
8. Never print raw scholarship IDs, application IDs, user IDs, or any other internal database identifier in your answer text. Refer to scholarships and applications by their name only (e.g. "your Gates Cambridge application", not an ID). IDs belong only in "referenced_scholarship_ids" / "referenced_application_ids" - never inside "answer", "warnings", or "unknowns".
9. Fit score and eligibility status measure different things - never let one imply the other. A high fit score does NOT mean "eligible" or "likely accepted"; it means the recorded criteria that could be scored line up well. When you state a fit score, call it a "fit score" (never "match", "eligibility percentage", or "chance of acceptance"), and if eligibility_status for that scholarship is "unknown", explicitly add that eligibility remains unconfirmed because one or more required criteria are unknown - do not invent a confidence number for eligibility itself. If eligibility_status is "ineligible", say so plainly even if the fit score is high.
10. When your answer includes both OmerPath-recorded facts (status, progress, eligibility, fit score, saved status, uploaded documents, verified scholarship requirements) and your own advice (recommended next steps, strategy, suggested documents to prepare, prioritization), clearly separate the two using plain-text section labels on their own line - "OmerPath facts:" followed by the facts, then "Advisor suggestions:" followed by your advice. Do not use markdown symbols (no "**", "#", or "*" bullets) - use plain lines and "- " for list items. Only include a section if the answer actually contains that kind of content; do not force an empty section.

Populate "warnings" with anything the student should double-check (e.g. confirming a deadline on the official source). Populate "unknowns" with specific facts you could not determine from the data. Only put scholarship or application IDs in "referenced_scholarship_ids" / "referenced_application_ids" if that exact ID literally appears in the OMERPATH DATA section.

Respond with a single JSON object only - no prose outside the JSON, no markdown code fences. The JSON object must have exactly these keys:
- "answer": string
- "warnings": array of strings (may be empty)
- "unknowns": array of strings (may be empty)
- "referenced_scholarship_ids": array of strings (may be empty)
- "referenced_application_ids": array of strings (may be empty)"""


@dataclass
class AdvisorResult:
    answer: str
    warnings: list[str]
    unknowns: list[str]
    referenced_scholarships: list[dict]
    referenced_applications: list[dict]


def _fmt_list(values) -> str:
    return ", ".join(values) if values else "none recorded"


def _render_scholarship_block(scholarship: Scholarship, match, saved: bool) -> str:
    lines = [
        f"- id: {scholarship.id}",
        f"  name: {scholarship.name}",
        f"  provider: {scholarship.provider_name}",
        f"  funding_type: {scholarship.funding_type or 'unspecified'}",
        f"  degree_levels: {_fmt_list(scholarship.degree_levels)}",
        f"  fields_of_study: {_fmt_list(scholarship.fields_of_study)}",
        f"  destinations: {_fmt_list(scholarship.destinations)}",
        "  deadline: "
        + (scholarship.deadline_at.isoformat() if scholarship.deadline_at else "not recorded")
        + (f" ({scholarship.deadline_note})" if scholarship.deadline_note else ""),
        f"  official_source_url: {scholarship.official_source_url or 'not recorded'}",
        f"  required_documents: {_fmt_list(scholarship.required_documents)}",
        f"  saved_by_student: {'true' if saved else 'false'}",
    ]
    if match is not None:
        lines.extend([
            f"  eligibility_status: {match.eligibility_status}",
            f"  fit_score: {match.match_score if match.match_score is not None else 'not enough data'} (measures recorded-criteria alignment only, NOT eligibility)",
            f"  matched_criteria: {_fmt_list(match.matched_criteria)}",
            f"  unmet_criteria: {_fmt_list(match.unmet_criteria)}",
            f"  unknown_criteria: {_fmt_list(match.unknown_criteria)}",
        ])
    return "\n".join(lines)


def _render_application_block(application: Application, scholarship_name: str) -> str:
    return "\n".join([
        f"- id: {application.id}",
        f"  scholarship: {scholarship_name} (scholarship_id: {application.scholarship_id})",
        f"  status: {application.status}",
        f"  progress: {application.progress}%",
        f"  next_action: {application.next_action or 'not recorded'}",
    ])


def _render_document_block(document: Document) -> str:
    return f"- {document.document_type}: {document.original_filename} (uploaded {document.created_at.date().isoformat()})"


def build_context_text(
    db: Session,
    user_id: UUID,
    focus_scholarship_id: str | None,
    focus_application_id: UUID | None,
) -> tuple[str, dict[str, Scholarship], dict[str, Application]]:
    """Assembles a grounding text block from real, authenticated OmerPath data.

    Returns the rendered text plus lookup maps keyed by id, so the caller can
    resolve any scholarship/application ids the model references back into
    real records instead of trusting anything the model writes.
    """
    profile = db.get(Profile, user_id)
    academic_profile = db.get(AcademicProfile, user_id)

    scholarships = db.scalars(select(Scholarship).where(Scholarship.status == "active")).all()
    scholarship_map = {s.id: s for s in scholarships}
    matches = {s.id: compute_match(profile, academic_profile, s) for s in scholarships}

    saved_ids = set(
        db.scalars(select(SavedScholarship.scholarship_id).where(SavedScholarship.user_id == user_id)).all()
    )

    applications = db.scalars(select(Application).where(Application.user_id == user_id)).all()
    application_map = {str(a.id): a for a in applications}

    documents = db.scalars(select(Document).where(Document.user_id == user_id)).all()

    if focus_scholarship_id is not None and focus_scholarship_id not in scholarship_map:
        raise AdvisorNotFoundError("Scholarship not found.")
    if focus_application_id is not None and str(focus_application_id) not in application_map:
        raise AdvisorNotFoundError("Application not found.")

    sections: list[str] = []

    sections.append(
        "PROFILE:\n"
        + "\n".join([
            f"- nationality: {profile.nationality if profile and profile.nationality else 'not recorded'}",
            f"- country_of_residence: {profile.country_of_residence if profile and profile.country_of_residence else 'not recorded'}",
        ])
    )

    language_test = (
        f"{academic_profile.language_test_type} {academic_profile.language_test_score}"
        if academic_profile and academic_profile.language_test_type and academic_profile.language_test_score
        else "not recorded"
    )
    sections.append(
        "ACADEMIC PROFILE:\n"
        + "\n".join([
            f"- current_degree: {academic_profile.current_degree if academic_profile and academic_profile.current_degree else 'not recorded'}",
            f"- field_of_study: {academic_profile.field_of_study if academic_profile and academic_profile.field_of_study else 'not recorded'}",
            f"- target_degree: {academic_profile.target_degree if academic_profile and academic_profile.target_degree else 'not recorded'}",
            f"- gpa: {academic_profile.gpa if academic_profile and academic_profile.gpa else 'not recorded'}",
            f"- language_test: {language_test}",
            f"- experience_summary: {academic_profile.experience_summary if academic_profile and academic_profile.experience_summary else 'not recorded'}",
            f"- preferred_destinations: {_fmt_list(academic_profile.preferred_destinations) if academic_profile else 'not recorded'}",
        ])
    )

    if scholarships:
        blocks = [_render_scholarship_block(s, matches.get(s.id), s.id in saved_ids) for s in scholarships]
        sections.append(
            "SCHOLARSHIPS (real, OmerPath-curated records; eligibility_status/fit_score/*_criteria are computed by "
            "OmerPath's deterministic matching engine, not by you):\n" + "\n\n".join(blocks)
        )
    else:
        sections.append("SCHOLARSHIPS: none currently available.")

    if applications:
        blocks = [
            _render_application_block(
                a, scholarship_map[a.scholarship_id].name if a.scholarship_id in scholarship_map else "unknown scholarship"
            )
            for a in applications
        ]
        sections.append("APPLICATIONS (real, student-owned):\n" + "\n".join(blocks))
    else:
        sections.append("APPLICATIONS: the student has not started any applications yet.")

    if documents:
        sections.append(
            "DOCUMENTS (metadata only - file contents are not available to you):\n"
            + "\n".join(_render_document_block(d) for d in documents)
        )
    else:
        sections.append("DOCUMENTS: no documents uploaded yet.")

    if focus_scholarship_id is not None:
        sections.append(
            f"CURRENT FOCUS: the student is currently viewing scholarship_id {focus_scholarship_id}. "
            "Prioritize that scholarship in your answer unless the question clearly asks about something else."
        )
    if focus_application_id is not None:
        sections.append(
            f"CURRENT FOCUS: the student is currently viewing application_id {focus_application_id}. "
            "Prioritize that application in your answer unless the question clearly asks about something else."
        )

    return "\n\n".join(sections), scholarship_map, application_map


def run_advisor_chat(
    message: str,
    history: list[dict],
    context_text: str,
    scholarship_map: dict[str, Scholarship],
    application_map: dict[str, Application],
) -> AdvisorResult:
    system_prompt = SYSTEM_PROMPT + "\n\nOMERPATH DATA:\n\n" + context_text

    trimmed_history = history[-MAX_HISTORY_MESSAGES:]
    messages = [{"role": h["role"], "content": h["content"]} for h in trimmed_history]
    messages.append({"role": "user", "content": message})

    raw_text = generate_json_reply(system_prompt, messages)

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        logger.error("Advisor response was not valid JSON")
        raise AdvisorProviderError("The Advisor returned an unusable response.") from exc

    referenced_scholarships = [
        {"id": sid, "name": scholarship_map[sid].name}
        for sid in parsed.get("referenced_scholarship_ids", [])
        if isinstance(sid, str) and sid in scholarship_map
    ]
    referenced_applications = [
        {
            "id": aid,
            "scholarship_id": application_map[aid].scholarship_id,
            "status": application_map[aid].status,
        }
        for aid in parsed.get("referenced_application_ids", [])
        if isinstance(aid, str) and aid in application_map
    ]

    return AdvisorResult(
        answer=parsed.get("answer") or "",
        warnings=[w for w in parsed.get("warnings", []) if isinstance(w, str)],
        unknowns=[u for u in parsed.get("unknowns", []) if isinstance(u, str)],
        referenced_scholarships=referenced_scholarships,
        referenced_applications=referenced_applications,
    )
