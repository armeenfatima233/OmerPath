"""One-time controlled seed for the initial scholarship dataset.

This is NOT an ingestion pipeline or scraper. Every record below was either
verified against its official source during this session (status="active",
last_verified_at set) or is carried over from prior prototype data pending
manual verification (status="draft", excluded from public API results until
a human confirms it). No deadline, benefit, or eligibility figure is invented
where it could not be confirmed - those fields are left null with an
explanatory note instead.

Run manually, once, from backend/: ../.venv/Scripts/python.exe scripts/seed_scholarships.py
Re-running is safe - it upserts by id rather than duplicating rows.
"""
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models.scholarship import Scholarship

VERIFIED_AT = datetime(2026, 8, 22, tzinfo=timezone.utc)

SCHOLARSHIPS = [
    {
        "id": "chevening",
        "name": "Chevening Scholarships",
        "provider_name": "UK Government",
        "description": (
            "UK government scholarship programme for future leaders to pursue master's study "
            "in the United Kingdom. Details not independently re-verified this session - "
            "confirm on the official website before relying on this record."
        ),
        "funding_type": "Fully Funded",
        "coverage": [],
        "degree_levels": ["Master's"],
        "fields_of_study": [],
        "destinations": ["United Kingdom"],
        "eligible_nationalities": None,
        "eligible_residences": None,
        "min_gpa": None,
        "language_test_type": None,
        "min_language_test_score": None,
        "min_experience": None,
        "age_min": None,
        "age_max": None,
        "eligibility_notes": (
            "Requires manual verification against the official Chevening website before "
            "publishing as active - this session's live fetch attempt timed out."
        ),
        "required_documents": [],
        "deadline_at": None,
        "deadline_note": "Confirm current application cycle dates on the official website.",
        "application_opens_at": None,
        "official_source_url": "https://www.chevening.org/",
        "application_url": None,
        "source_label": "Official programme website (not independently verified this session)",
        "last_verified_at": None,
        "status": "draft",
        "fit_reasons": [],
        "attention_points": [],
    },
    {
        "id": "erasmus",
        "name": "Erasmus Mundus Joint Master's Programmes",
        "provider_name": "European Union",
        "description": (
            "EU-funded joint master's programmes delivered by consortiums of European "
            "universities. Confirmed via the official EACEA page: master's-level students "
            "from anywhere in the world may apply, though applications typically run "
            "October-January for the following academic year, and exact eligibility and "
            "deadlines are set by each individual consortium."
        ),
        "funding_type": "Fully Funded",
        "coverage": [],
        "degree_levels": ["Master's"],
        "fields_of_study": [],
        "destinations": ["Multiple Countries"],
        "eligible_nationalities": None,
        "eligible_residences": None,
        "min_gpa": None,
        "language_test_type": None,
        "min_language_test_score": None,
        "min_experience": None,
        "age_min": None,
        "age_max": None,
        "eligibility_notes": (
            "Open to master's-level students worldwide. Apply directly through the specific "
            "joint programme consortium - eligibility and deadlines vary by programme."
        ),
        "required_documents": [],
        "deadline_at": None,
        "deadline_note": (
            "Most programmes require applications between October and January for the "
            "following academic year; exact deadlines vary by consortium - confirm on the "
            "specific programme's page."
        ),
        "application_opens_at": None,
        "official_source_url": "https://www.eacea.ec.europa.eu/scholarships/erasmus-mundus-catalogue_en",
        "application_url": None,
        "source_label": "Official EU programme catalogue",
        "last_verified_at": VERIFIED_AT,
        "status": "active",
        "fit_reasons": [],
        "attention_points": [],
    },
    {
        "id": "daad",
        "name": "DAAD Development-Related Postgraduate Courses (EPOS)",
        "provider_name": "DAAD (German Academic Exchange Service)",
        "description": (
            "DAAD-administered postgraduate scholarships for students from developing "
            "countries, delivered through specific participating courses in Germany. The "
            "DAAD scholarship database was confirmed live and official this session, but this "
            "specific programme's current listing was not located within it - confirm before "
            "publishing as active."
        ),
        "funding_type": "Fully Funded",
        "coverage": [],
        "degree_levels": ["Master's"],
        "fields_of_study": [],
        "destinations": ["Germany"],
        "eligible_nationalities": None,
        "eligible_residences": None,
        "min_gpa": None,
        "language_test_type": None,
        "min_language_test_score": None,
        "min_experience": None,
        "age_min": None,
        "age_max": None,
        "eligibility_notes": (
            "Confirmed: this is DAAD's official scholarship database (156 listed options at "
            "time of check). The specific 'Development-Related Postgraduate Courses' "
            "programme was not located within this session's fetch - search the database "
            "directly and confirm current programme details before publishing as active."
        ),
        "required_documents": [],
        "deadline_at": None,
        "deadline_note": "Varies by specific course - confirm via the DAAD scholarship database.",
        "application_opens_at": None,
        "official_source_url": "https://www2.daad.de/deutschland/stipendium/datenbank/en/21148-scholarship-database/",
        "application_url": None,
        "source_label": "Official DAAD scholarship database",
        "last_verified_at": None,
        "status": "draft",
        "fit_reasons": [],
        "attention_points": [],
    },
    {
        "id": "australia-awards",
        "name": "Australia Awards Scholarships",
        "provider_name": "Australian Government",
        "description": (
            "Australian government scholarship programme for students from eligible partner "
            "countries to pursue postgraduate study in Australia. Details not independently "
            "re-verified this session - confirm on the official website before relying on "
            "this record."
        ),
        "funding_type": "Fully Funded",
        "coverage": [],
        "degree_levels": ["Master's"],
        "fields_of_study": [],
        "destinations": ["Australia"],
        "eligible_nationalities": None,
        "eligible_residences": None,
        "min_gpa": None,
        "language_test_type": None,
        "min_language_test_score": None,
        "min_experience": None,
        "age_min": None,
        "age_max": None,
        "eligibility_notes": (
            "Requires manual verification against the official Australia Awards website "
            "before publishing as active - this session's live fetch attempts timed out twice."
        ),
        "required_documents": [],
        "deadline_at": None,
        "deadline_note": "Confirm current application cycle dates on the official website.",
        "application_opens_at": None,
        "official_source_url": "https://www.australiaawards.gov.au/",
        "application_url": None,
        "source_label": "Official programme website (not independently verified this session)",
        "last_verified_at": None,
        "status": "draft",
        "fit_reasons": [],
        "attention_points": [],
    },
    {
        "id": "fulbright",
        "name": "Fulbright Foreign Student Program",
        "provider_name": "U.S. Department of State (administered by IIE)",
        "description": (
            "U.S. government-funded international exchange programme for non-U.S. citizens "
            "to study in the United States, administered by the Institute of International "
            "Education (IIE). Confirmed via the official Fulbright website: applicants must "
            "apply through the Fulbright Commission or U.S. Embassy in their home country, "
            "and deadlines vary by country."
        ),
        "funding_type": "Fully Funded",
        "coverage": [],
        "degree_levels": ["Master's"],
        "fields_of_study": [],
        "destinations": ["United States"],
        "eligible_nationalities": None,
        "eligible_residences": None,
        "min_gpa": None,
        "language_test_type": None,
        "min_language_test_score": None,
        "min_experience": None,
        "age_min": None,
        "age_max": None,
        "eligibility_notes": (
            "Non-U.S. citizens only. Must apply through the Fulbright Commission/Foundation "
            "or U.S. Embassy in the applicant's home country - process and deadlines vary by "
            "country."
        ),
        "required_documents": [],
        "deadline_at": None,
        "deadline_note": "Deadlines vary by home country - confirm with your local Fulbright Commission or U.S. Embassy.",
        "application_opens_at": None,
        "official_source_url": "https://foreign.fulbrightonline.org/",
        "application_url": None,
        "source_label": "Official Fulbright programme website",
        "last_verified_at": VERIFIED_AT,
        "status": "active",
        "fit_reasons": [],
        "attention_points": [],
    },
    {
        "id": "gates-cambridge",
        "name": "Gates Cambridge Scholarship",
        "provider_name": "Gates Cambridge Trust (funded by the Gates Foundation)",
        "description": (
            "Full-cost postgraduate scholarship at the University of Cambridge, funded by the "
            "Gates Cambridge Trust (established 2000 with a gift from the Gates Foundation). "
            "Confirmed via the official website: for outstanding postgraduate students who "
            "demonstrate potential for leadership and a commitment to improving the lives of "
            "others. Specific funding coverage and current deadlines were not available in "
            "this session's fetch - confirm before relying on those details."
        ),
        "funding_type": "Fully Funded",
        "coverage": [],
        "degree_levels": ["Master's", "PhD"],
        "fields_of_study": [],
        "destinations": ["United Kingdom"],
        "eligible_nationalities": None,
        "eligible_residences": None,
        "min_gpa": None,
        "language_test_type": None,
        "min_language_test_score": None,
        "min_experience": None,
        "age_min": None,
        "age_max": None,
        "eligibility_notes": (
            "For outstanding postgraduate students demonstrating leadership potential and "
            "commitment to improving others' lives (per official site). Specific "
            "eligibility/coverage details not available in this session's fetch - confirm via "
            "the official 'Eligibility' page before publishing detailed criteria."
        ),
        "required_documents": [],
        "deadline_at": None,
        "deadline_note": "Confirm current application deadline on the official website's Timeline page.",
        "application_opens_at": None,
        "official_source_url": "https://www.gatescambridge.org/",
        "application_url": None,
        "source_label": "Official Gates Cambridge Trust website",
        "last_verified_at": VERIFIED_AT,
        "status": "active",
        "fit_reasons": [],
        "attention_points": [],
    },
]


def run() -> None:
    db = SessionLocal()
    try:
        for record in SCHOLARSHIPS:
            existing = db.get(Scholarship, record["id"])
            if existing is None:
                db.add(Scholarship(**record))
            else:
                for field, value in record.items():
                    setattr(existing, field, value)
        db.commit()
        print(f"Seeded/updated {len(SCHOLARSHIPS)} scholarship records.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
