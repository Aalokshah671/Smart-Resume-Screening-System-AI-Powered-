from typing import Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.parser import extract_skills, extract_years_experience


def compute_text_similarity(jd_text: str, resume_text: str) -> float:
    """Return cosine similarity (0-1) between JD and resume using TF-IDF."""
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])
    except ValueError:
        # Happens if text is empty / all stopwords
        return 0.0
    sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return float(sim)


def build_explanation(
    score: float,
    matched_skills: List[str],
    missing_skills: List[str],
    years_experience: float,
) -> str:
    """Generate a short 2-3 line human-readable explanation."""
    lines = []

    if score >= 75:
        lines.append(f"Strong match ({score}/100) - the resume aligns well with the job description.")
    elif score >= 45:
        lines.append(f"Moderate match ({score}/100) - some relevant overlap, but notable gaps remain.")
    else:
        lines.append(f"Weak match ({score}/100) - the resume covers little of what the JD requires.")

    if matched_skills:
        shown = ", ".join(matched_skills[:6])
        lines.append(f"Matched skills: {shown}{'...' if len(matched_skills) > 6 else ''}.")
    else:
        lines.append("No required skills were found in the resume.")

    if missing_skills:
        shown = ", ".join(missing_skills[:6])
        lines.append(f"Missing: {shown}{'...' if len(missing_skills) > 6 else ''}.")

    if years_experience:
        lines.append(f"Detected ~{years_experience:g} years of experience.")

    return " ".join(lines)


def match_resume_to_jd(jd_text: str, resume_text: str) -> Dict:
    """Run full matching pipeline for a single resume against a JD."""
    jd_skills = extract_skills(jd_text)
    resume_skills = extract_skills(resume_text)

    matched_skills = sorted(set(jd_skills) & set(resume_skills))
    missing_skills = sorted(set(jd_skills) - set(resume_skills))

    skill_overlap_ratio = (
        len(matched_skills) / len(jd_skills) if jd_skills else 0.0
    )

    text_similarity = compute_text_similarity(jd_text, resume_text)

    # Blend: 70% explicit skill overlap, 30% semantic similarity
    blended = (0.7 * skill_overlap_ratio) + (0.3 * text_similarity)
    match_score = round(blended * 100, 1)

    years_experience = extract_years_experience(resume_text)

    explanation = build_explanation(
        match_score, matched_skills, missing_skills, years_experience
    )

    return {
        "match_score": match_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "years_experience": years_experience,
        "explanation": explanation,
    }