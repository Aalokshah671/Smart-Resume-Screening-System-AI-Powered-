# Smart Resume Screening System (AI-Powered)

A lightweight system that takes a Job Description (JD), matches one or more
resumes against it, and returns a 0–100 relevance score with matched/missing
skills and a short explanation — via a FastAPI backend and a simple web UI.

## Setup

```bash
# 1. Clone / unzip the project, then move into it
cd resume_screener

# 2. (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## How to run the API

```bash
uvicorn app.main:app --reload
```

- API root / UI: http://127.0.0.1:8000/
- Interactive API docs (Swagger): http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

Open http://127.0.0.1:8000/ in a browser to use the included frontend: paste
a JD, upload one or more resumes (`.pdf`, `.docx`, `.txt`), and click
**"Score candidates"**.

### Using the API directly (curl example)

```bash
curl -X POST http://127.0.0.1:8000/match \
  -F "job_description=$(cat sample_data/sample_jd.txt)" \
  -F "resumes=@sample_data/resume_strong_match.txt" \
  -F "resumes=@sample_data/resume_weak_match.txt"
```

Sample JD and resumes are included in `sample_data/` for quick testing.

## API

### `POST /match`

**Form fields:**
| Field | Type | Description |
|---|---|---|
| `job_description` | text | Full text of the job description |
| `resumes` | file(s) | One or more resume files (`.pdf`, `.docx`, `.txt`) |

**Response:**
```json
{
  "job_description_preview": "...",
  "results": [
    {
      "filename": "resume_strong_match.txt",
      "match_score": 56.6,
      "matched_skills": ["python", "fastapi", "docker", "..."],
      "missing_skills": ["tensorflow", "flask", "..."],
      "years_experience": 2.0,
      "explanation": "Moderate match (56.6/100) - some relevant overlap..."
    }
  ]
}
```
Results are sorted best-match-first.

## Approach

**1. Resume parsing (`app/parser.py`)**
Text is extracted per file type — `pdfplumber` for PDFs, `python-docx` for
`.docx`, direct decode for `.txt`. From the raw text:
- **Skills** are extracted by matching against a curated keyword list
  (`app/skills_data.py`, ~70 common tech/AI-ML terms) using word-boundary
  regex matching so, e.g., "R" doesn't falsely match inside "React".
- **Years of experience** is extracted with a best-effort regex for phrases
  like *"3 years of experience"* / *"5+ years experience"*.

**2. Matching logic (`app/matcher.py`)**
I chose **TF-IDF + Cosine Similarity** (the required baseline option) over
embeddings, since it's dependency-light, fast, fully deterministic, and easy
to explain in a review — a reasonable trade-off for a 1-year-experience-level
take-home. The final score blends two signals so it's both *semantically*
aware and *explicitly* explainable:

```
final_score = (0.6 × TF-IDF cosine similarity) + (0.4 × skill overlap ratio)
```

- **TF-IDF cosine similarity** (60%): overall textual relevance between the
  JD and resume — catches relevant experience described in prose, not just
  keyword lists.
- **Skill overlap ratio** (40%): `matched skills / total JD skills` — keeps
  the score grounded and resistant to resumes that are wordy but skill-poor.

The code is structured so an embeddings-based similarity function could be
swapped in for `compute_text_similarity()` without touching the rest of the
pipeline, if that's ever desired.

**3. Output**
For each resume: match score (0–100), matched skills, missing skills, a
2–3 line plain-English explanation, and detected years of experience.

**4. API**
A single `FastAPI` endpoint, `POST /match`, accepting a JD (form text) and
one or more resume files (multipart upload), returning JSON results sorted
best-match-first. CORS is open so the bundled frontend (or any other client)
can call it directly.

**5. Frontend**
A single static HTML/CSS/JS page (`static/index.html`) served by FastAPI
itself at `/` — no build step required. It posts to `/match` and renders
score, matched/missing skill chips, and the explanation per candidate.

## Project structure

```
resume_screener/
├── app/
│   ├── main.py          # FastAPI app + /match endpoint
│   ├── matcher.py        # TF-IDF + cosine similarity + scoring
│   ├── parser.py          # Resume text/skill/experience extraction
│   └── skills_data.py     # Keyword bank for skill extraction
├── static/
│   └── index.html         # Simple frontend UI
├── sample_data/
│   ├── sample_jd.txt
│   ├── resume_strong_match.txt
│   └── resume_weak_match.txt
├── requirements.txt
└── README.md
```

Author: Aalok Shah
