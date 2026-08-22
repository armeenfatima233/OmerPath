"""Deterministic, explainable scholarship matching.

No ML, no LLM, no randomness, no persistence - a pure function of the
user's profile/academic-profile and a scholarship's structured eligibility
fields. Identical inputs always produce identical output.

Two separate concerns, deliberately kept apart:

1. Hard eligibility (ELIGIBLE / INELIGIBLE / UNKNOWN) - only degree level,
   nationality, residence, and language (when both sides use the exact same
   test type on its universal scale, e.g. IELTS-vs-IELTS) are evaluated as
   hard rules. GPA and professional experience are deliberately NOT hard
   rules: scholarship-side data may now exist, but the user's own recorded
   value has no verified scale/unit attached to it, so a numeric comparison
   would risk a false ineligible verdict. They remain score-only signals.

   A rule is only ever "unmet" if it was genuinely evaluated (both sides had
   usable data) and failed. Missing data on either side is always "unknown",
   never treated as a pass.

2. Match score (0-100, or None if nothing was evaluable) - built only from
   factors where both sides actually have data. Factors with no data on
   either side are excluded from the score entirely, never counted as zero.
"""
from dataclasses import dataclass, field

from app.models.academic_profile import AcademicProfile
from app.models.profile import Profile
from app.models.scholarship import Scholarship

Verdict = str  # "met" | "unmet" | "unknown"


@dataclass
class Criterion:
    key: str
    label: str
    verdict: Verdict
    detail: str


@dataclass
class MatchResult:
    scholarship_id: str
    eligibility_status: str  # "eligible" | "ineligible" | "unknown"
    match_score: int | None
    matched_criteria: list[str] = field(default_factory=list)
    unmet_criteria: list[str] = field(default_factory=list)
    unknown_criteria: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


def _norm(value: str | None) -> str | None:
    return value.strip().lower() if value else None


def _set_membership(value: str | None, options: list[str] | None) -> bool:
    if value is None or not options:
        return False
    normalized = _norm(value)
    return any(_norm(option) == normalized for option in options)


def _parse_float(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return float(value.strip())
    except ValueError:
        return None


def _check_degree_level(academic_profile: AcademicProfile | None, scholarship: Scholarship) -> Criterion:
    target = academic_profile.target_degree if academic_profile else None
    levels = scholarship.degree_levels or []
    if not levels:
        return Criterion("degree_level", "Degree level", "unknown", "Scholarship does not specify eligible degree levels.")
    if not target:
        return Criterion("degree_level", "Degree level", "unknown", "Your target degree is not set in your academic profile.")
    if _set_membership(target, levels):
        return Criterion("degree_level", "Degree level", "met", f"Your target degree ({target}) is accepted.")
    return Criterion("degree_level", "Degree level", "unmet", f"Scholarship accepts {', '.join(levels)}; your target degree is {target}.")


def _check_nationality(profile: Profile | None, scholarship: Scholarship) -> Criterion:
    nationality = profile.nationality if profile else None
    if not nationality:
        return Criterion("nationality", "Nationality", "unknown", "Your nationality is not set in your profile.")
    if _set_membership(nationality, scholarship.excluded_nationalities):
        return Criterion("nationality", "Nationality", "unmet", f"Scholarship excludes applicants with nationality: {nationality}.")
    if scholarship.eligible_nationalities:
        if _set_membership(nationality, scholarship.eligible_nationalities):
            return Criterion("nationality", "Nationality", "met", f"Your nationality ({nationality}) is on the eligible list.")
        return Criterion("nationality", "Nationality", "unmet", f"Scholarship restricts eligibility to specific nationalities; {nationality} is not listed.")
    if scholarship.excluded_nationalities:
        return Criterion("nationality", "Nationality", "met", f"Your nationality ({nationality}) is not on the excluded list.")
    return Criterion("nationality", "Nationality", "unknown", "Scholarship has not specified nationality restrictions in our records.")


def _check_residence(profile: Profile | None, scholarship: Scholarship) -> Criterion:
    residence = profile.country_of_residence if profile else None
    if not residence:
        return Criterion("residence", "Country of residence", "unknown", "Your country of residence is not set in your profile.")
    if not scholarship.eligible_residences:
        return Criterion("residence", "Country of residence", "unknown", "Scholarship has not specified residency restrictions in our records.")
    if _set_membership(residence, scholarship.eligible_residences):
        return Criterion("residence", "Country of residence", "met", f"Your country of residence ({residence}) is eligible.")
    return Criterion("residence", "Country of residence", "unmet", f"Scholarship restricts eligibility to specific countries of residence; {residence} is not listed.")


def _check_language(academic_profile: AcademicProfile | None, scholarship: Scholarship) -> Criterion:
    if not scholarship.language_test_type or not scholarship.min_language_test_score:
        return Criterion("language", "Language requirement", "unknown", "Scholarship has not specified a verified language requirement in our records.")
    user_type = academic_profile.language_test_type if academic_profile else None
    user_score = academic_profile.language_test_score if academic_profile else None
    if not user_type or not user_score:
        return Criterion("language", "Language requirement", "unknown", "Your language test details are not set in your academic profile.")
    if _norm(user_type) != _norm(scholarship.language_test_type):
        return Criterion(
            "language", "Language requirement", "unknown",
            f"Scholarship requires {scholarship.language_test_type}; your recorded test ({user_type}) can't be compared on the same scale.",
        )
    required = _parse_float(scholarship.min_language_test_score)
    actual = _parse_float(user_score)
    if required is None or actual is None:
        return Criterion("language", "Language requirement", "unknown", "Language scores could not be compared.")
    if actual >= required:
        return Criterion("language", "Language requirement", "met", f"Your {user_type} score ({actual}) meets the minimum ({required}).")
    return Criterion("language", "Language requirement", "unmet", f"Scholarship requires {user_type} {required}+; your recorded score is {actual}.")


def _hard_eligibility(criteria: list[Criterion]) -> str:
    if any(c.verdict == "unmet" for c in criteria):
        return "ineligible"
    if all(c.verdict == "met" for c in criteria):
        return "eligible"
    return "unknown"


def _score_factors(
    profile: Profile | None,
    academic_profile: AcademicProfile | None,
    scholarship: Scholarship,
    degree_criterion: Criterion,
    language_criterion: Criterion,
) -> list[tuple[str, float]]:
    """Returns (label, contribution 0.0-1.0) for every factor that could
    actually be evaluated. Factors with no data on either side are simply
    omitted - never counted as zero."""
    factors: list[tuple[str, float]] = []

    if degree_criterion.verdict in ("met", "unmet"):
        factors.append(("Target degree alignment", 1.0 if degree_criterion.verdict == "met" else 0.0))

    if language_criterion.verdict in ("met", "unmet"):
        factors.append(("Language readiness", 1.0 if language_criterion.verdict == "met" else 0.0))

    preferred = (academic_profile.preferred_destinations if academic_profile else None) or []
    destinations = scholarship.destinations or []
    if preferred and destinations:
        overlap = any(_set_membership(d, preferred) for d in destinations)
        factors.append(("Preferred destination", 1.0 if overlap else 0.0))

    user_fields = [academic_profile.field_of_study] if academic_profile and academic_profile.field_of_study else []
    scholarship_fields = scholarship.fields_of_study or []
    if user_fields and scholarship_fields:
        overlap = any(_set_membership(f, scholarship_fields) for f in user_fields)
        factors.append(("Field of study", 1.0 if overlap else 0.0))

    if scholarship.min_gpa and academic_profile and academic_profile.gpa:
        factors.append(("Academic record recorded", 1.0))

    if scholarship.min_experience and academic_profile and academic_profile.experience_summary:
        factors.append(("Experience recorded", 1.0))

    return factors


def compute_match(profile: Profile | None, academic_profile: AcademicProfile | None, scholarship: Scholarship) -> MatchResult:
    degree_criterion = _check_degree_level(academic_profile, scholarship)
    nationality_criterion = _check_nationality(profile, scholarship)
    residence_criterion = _check_residence(profile, scholarship)
    language_criterion = _check_language(academic_profile, scholarship)

    hard_criteria = [degree_criterion, nationality_criterion, residence_criterion, language_criterion]
    eligibility_status = _hard_eligibility(hard_criteria)

    factors = _score_factors(profile, academic_profile, scholarship, degree_criterion, language_criterion)
    match_score = round(sum(v for _, v in factors) / len(factors) * 100) if factors else None

    matched = [c.detail for c in hard_criteria if c.verdict == "met"]
    unmet = [c.detail for c in hard_criteria if c.verdict == "unmet"]
    unknown = [c.detail for c in hard_criteria if c.verdict == "unknown"]
    reasons = [c.detail for c in hard_criteria] + [f"{label}: {'matches' if v == 1.0 else 'does not match'}" for label, v in factors]

    return MatchResult(
        scholarship_id=scholarship.id,
        eligibility_status=eligibility_status,
        match_score=match_score,
        matched_criteria=matched,
        unmet_criteria=unmet,
        unknown_criteria=unknown,
        reasons=reasons,
    )
