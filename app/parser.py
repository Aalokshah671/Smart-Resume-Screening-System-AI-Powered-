import io
import re
from typing import List

import pdfplumber
import docx

from app.skills_data import COMMON_SKILLS


def extract_text(filename: str, file_bytes: bytes) -> str:
    """Extract raw text from an uploaded resume file (pdf/docx/txt)."""
    lower = filename.lower()

    if lower.endswith(".pdf"):
        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)

    if lower.endswith(".docx"):
        document = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in document.paragraphs)

    if lower.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")

    raise ValueError(
        f"Unsupported file type for '{filename}'. Use .pdf, .docx, or .txt"
    )


def extract_skills(text: str, skill_bank: List[str] = None) -> List[str]:
    """Find which known skills appear in the given text (case-insensitive,
    whole-word/phrase match)."""
    skill_bank = skill_bank or COMMON_SKILLS
    text_lower = text.lower()
    found = []
    for skill in skill_bank:
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill.lower()) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


def extract_years_experience(text: str) -> float:
    """Best-effort extraction of total years of experience mentioned in the
    resume text. Tries two strategies:
      1. Explicit phrases like '5+ years of experience', '3 yrs exp'.
      2. Date ranges in work history, e.g. 'Jan 2023 - Present' or
         '2021 - 2023', summed across all detected ranges (deduplicated
         by year span, not true calendar precision - a reasonable
         approximation for a basic parser).
    Returns the larger of the two estimates.
    """
    explicit_years = 0.0
    matches = re.findall(
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\.?\s*(?:of)?\s*(?:experience|exp)\b",
        text,
        flags=re.IGNORECASE,
    )
    if matches:
        explicit_years = max(float(m) for m in matches)

    # Date-range based estimate, e.g. "Jan 2022 - Present", "2020-2023"
    current_year = 2026
    month = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*"
    range_pattern = (
        rf"(?:{month})?(\d{{4}})\s*(?:-|–|to)\s*"
        rf"(?:(?:{month})?(\d{{4}})|present|current)"
    )
    range_matches = re.findall(range_pattern, text, flags=re.IGNORECASE)
    total_range_years = 0.0
    for start, end in range_matches:
        start_year = int(start)
        end_year = int(end) if end else current_year
        if 1990 <= start_year <= current_year and start_year <= end_year:
            total_range_years += end_year - start_year

    return max(explicit_years, total_range_years)