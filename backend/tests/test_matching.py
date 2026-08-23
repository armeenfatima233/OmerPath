"""Pure unit tests for app.matching.compute_match - no DB, no network, no
Supabase. Profile/AcademicProfile/Scholarship are constructed in memory and
never added to a session, so these run instantly and deterministically.
"""
from app.matching import compute_match
from app.models.academic_profile import AcademicProfile
from app.models.profile import Profile
from app.models.scholarship import Scholarship


def make_scholarship(**overrides) -> Scholarship:
    defaults = dict(
        id="test-scholarship",
        name="Test Scholarship",
        provider_name="Test Provider",
        coverage=[],
        degree_levels=[],
        fields_of_study=[],
        destinations=[],
        eligible_nationalities=None,
        excluded_nationalities=None,
        eligible_residences=None,
        min_gpa=None,
        language_test_type=None,
        min_language_test_score=None,
        min_experience=None,
        required_documents=[],
        fit_reasons=[],
        attention_points=[],
        status="active",
    )
    defaults.update(overrides)
    return Scholarship(**defaults)


def make_profile(**overrides) -> Profile:
    defaults = dict(id=None, first_name="Test", last_name="User", nationality=None, country_of_residence=None)
    defaults.update(overrides)
    return Profile(**defaults)


def make_academic_profile(**overrides) -> AcademicProfile:
    defaults = dict(
        user_id=None, current_degree=None, field_of_study=None, target_degree=None, gpa=None,
        language_test_type=None, language_test_score=None, experience_summary=None,
        preferred_destinations=[],
    )
    defaults.update(overrides)
    return AcademicProfile(**defaults)


def test_eligible_when_every_hard_criterion_is_met():
    scholarship = make_scholarship(
        degree_levels=["Master's"],
        eligible_nationalities=["Pakistani"],
        eligible_residences=["Pakistan"],
        language_test_type="IELTS",
        min_language_test_score="6.5",
    )
    profile = make_profile(nationality="Pakistani", country_of_residence="Pakistan")
    academic_profile = make_academic_profile(target_degree="Master's", language_test_type="IELTS", language_test_score="7.0")

    result = compute_match(profile, academic_profile, scholarship)

    assert result.eligibility_status == "eligible"
    assert result.unmet_criteria == []
    assert result.unknown_criteria == []
    assert len(result.matched_criteria) == 4


def test_ineligible_when_nationality_is_excluded():
    scholarship = make_scholarship(excluded_nationalities=["United States"])
    profile = make_profile(nationality="United States")
    academic_profile = make_academic_profile()

    result = compute_match(profile, academic_profile, scholarship)

    assert result.eligibility_status == "ineligible"
    assert any("United States" in reason for reason in result.unmet_criteria)


def test_ineligible_when_degree_level_not_accepted():
    scholarship = make_scholarship(degree_levels=["PhD"])
    profile = make_profile()
    academic_profile = make_academic_profile(target_degree="Master's")

    result = compute_match(profile, academic_profile, scholarship)

    assert result.eligibility_status == "ineligible"
    assert any("degree" in reason.lower() for reason in result.unmet_criteria)


def test_ineligible_wins_even_when_other_criteria_are_unknown():
    # Residence is always "unknown" here (no eligible_residences on the
    # scholarship) - ineligible must still win over unknown, never average out.
    scholarship = make_scholarship(excluded_nationalities=["United States"])
    profile = make_profile(nationality="United States", country_of_residence=None)
    academic_profile = make_academic_profile()

    result = compute_match(profile, academic_profile, scholarship)

    assert result.eligibility_status == "ineligible"


def test_unknown_when_profile_and_academic_profile_are_none():
    scholarship = make_scholarship(degree_levels=["Master's"])

    result = compute_match(None, None, scholarship)

    assert result.eligibility_status == "unknown"
    assert result.unmet_criteria == []
    assert len(result.unknown_criteria) > 0


def test_unknown_when_scholarship_has_no_restrictions_recorded():
    scholarship = make_scholarship(degree_levels=["Master's"])  # no nationality/residence/language data
    profile = make_profile(nationality="Pakistani", country_of_residence="Pakistan")
    academic_profile = make_academic_profile(target_degree="Master's")

    result = compute_match(profile, academic_profile, scholarship)

    # Degree matches, but nothing else can be evaluated -> unknown, not eligible.
    assert result.eligibility_status == "unknown"
    assert "Degree level" not in [c for c in result.unknown_criteria]


def test_language_test_type_mismatch_is_unknown_not_unmet():
    scholarship = make_scholarship(language_test_type="IELTS", min_language_test_score="6.5")
    academic_profile = make_academic_profile(language_test_type="TOEFL", language_test_score="110")
    profile = make_profile()

    result = compute_match(profile, academic_profile, scholarship)

    assert any("recorded test" in reason or "can't be compared" in reason for reason in result.unknown_criteria)
    assert not any("language" in reason.lower() and "requires" in reason.lower() for reason in result.unmet_criteria)


def test_language_score_below_minimum_is_unmet():
    scholarship = make_scholarship(language_test_type="IELTS", min_language_test_score="7.0")
    academic_profile = make_academic_profile(language_test_type="IELTS", language_test_score="6.0")
    profile = make_profile()

    result = compute_match(profile, academic_profile, scholarship)

    assert result.eligibility_status == "ineligible"
    assert any("IELTS" in reason for reason in result.unmet_criteria)


def test_match_score_is_none_when_no_factors_are_evaluable():
    scholarship = make_scholarship()  # nothing set
    profile = make_profile()
    academic_profile = make_academic_profile()

    result = compute_match(profile, academic_profile, scholarship)

    assert result.match_score is None


def test_match_score_reflects_only_evaluable_factors():
    scholarship = make_scholarship(degree_levels=["Master's"])
    profile = make_profile()
    academic_profile = make_academic_profile(target_degree="Master's")

    result = compute_match(profile, academic_profile, scholarship)

    # Only "degree alignment" was evaluable, and it matched -> 100.
    assert result.match_score == 100


def test_match_score_and_eligibility_are_independent():
    # High/complete score is possible even when eligibility can't be confirmed,
    # because residence is never scored, only gated. This is the exact
    # "fit score 100 / eligibility unknown" case surfaced during manual testing.
    scholarship = make_scholarship(
        degree_levels=["Master's"],
        excluded_nationalities=["United Kingdom"],
        language_test_type="IELTS",
        min_language_test_score="6.5",
    )
    profile = make_profile(nationality="United States", country_of_residence=None)
    academic_profile = make_academic_profile(target_degree="Master's", language_test_type="IELTS", language_test_score="7.5")

    result = compute_match(profile, academic_profile, scholarship)

    assert result.match_score == 100
    assert result.eligibility_status == "unknown"


def test_compute_match_is_deterministic():
    scholarship = make_scholarship(degree_levels=["Master's"], excluded_nationalities=["United States"])
    profile = make_profile(nationality="United States")
    academic_profile = make_academic_profile(target_degree="Master's")

    first = compute_match(profile, academic_profile, scholarship)
    second = compute_match(profile, academic_profile, scholarship)

    assert first == second
