"""One-time controlled enrichment update, not a reseed.

Applies eligibility facts verified via direct fetch of official sources during
the matching-milestone audit (2026-08-23):
- Fulbright: foreign.fulbrightonline.org/apply
- Gates Cambridge: gatescambridge.org/apply/eligibility/

Run manually, once, from backend/: PYTHONPATH=. ../.venv/Scripts/python.exe scripts/enrich_scholarships_2026_08_23.py
Idempotent - re-running just re-applies the same values.
"""
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models.scholarship import Scholarship

VERIFIED_AT = datetime(2026, 8, 23, tzinfo=timezone.utc)

UPDATES = {
    "fulbright": {
        "excluded_nationalities": ["United States"],
        "language_test_type": "IELTS",
        "min_language_test_score": "6.5",
        "eligibility_notes": (
            "Non-U.S. citizens only (dual citizens not eligible). Must reside in the "
            "country of nomination at time of application - apply through the Fulbright "
            "Commission/Foundation or U.S. Embassy in that country; process and deadlines "
            "vary by country. Language proficiency: TOEFL PBT >=550, or TOEFL iBT 79-80, "
            "or IELTS >=6.5 overall (any one of these three is accepted)."
        ),
        "last_verified_at": VERIFIED_AT,
    },
    "gates-cambridge": {
        "excluded_nationalities": ["United Kingdom"],
        "eligibility_notes": (
            "Open to citizens of any country outside the United Kingdom. Eligible "
            "courses: PhD (full-time or part-time), MLitt (full-time), and one-year "
            "full-time postgraduate courses only. Not eligible: undergraduate degrees, "
            "MASt, most part-time degrees (PhD excepted), and professional programmes "
            "such as MBA, EMBA, MFin, PGCE. Minimum GPA, IELTS/TOEFL score, and age are "
            "not stated on the official eligibility page as separate scholarship-specific "
            "requirements - English proficiency is assessed through Cambridge's general "
            "admissions process instead."
        ),
        "last_verified_at": VERIFIED_AT,
    },
}


def run() -> None:
    db = SessionLocal()
    try:
        for scholarship_id, fields in UPDATES.items():
            scholarship = db.get(Scholarship, scholarship_id)
            if scholarship is None:
                print(f"WARNING: {scholarship_id} not found, skipped")
                continue
            for field, value in fields.items():
                setattr(scholarship, field, value)
        db.commit()
        print(f"Updated {len(UPDATES)} scholarship records.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
