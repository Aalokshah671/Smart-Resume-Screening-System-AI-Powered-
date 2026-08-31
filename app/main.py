
from typing import List

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.matcher import match_resume_to_jd
from app.parser import extract_text

app = FastAPI(
    title="Smart Resume Screening System",
    description="Matches resumes against a job description and returns a relevance score.",
    version="1.0.0",
)

# Allow the simple frontend (served from anywhere) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResumeResult(BaseModel):
    filename: str
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    years_experience: float
    explanation: str


class MatchResponse(BaseModel):
    job_description_preview: str
    results: List[ResumeResult]


@app.post("/match", response_model=MatchResponse)
async def match_resumes(
    job_description: str = Form(
        ..., description="The full text of the Job Description"
    ),
    resumes: List[UploadFile] = File(
        ..., description="One or more resume files (.pdf, .docx, .txt)"
    ),
):

    results = []

    for resume in resumes:
        file_bytes = await resume.read()
        try:
            resume_text = extract_text(resume.filename, file_bytes)
        except ValueError as e:
            results.append(
                ResumeResult(
                    filename=resume.filename,
                    match_score=0.0,
                    matched_skills=[],
                    missing_skills=[],
                    years_experience=0.0,
                    explanation=str(e),
                )
            )
            continue

        outcome = match_resume_to_jd(job_description, resume_text)
        results.append(
            ResumeResult(
                filename=resume.filename,
                match_score=outcome["match_score"],
                matched_skills=outcome["matched_skills"],
                missing_skills=outcome["missing_skills"],
                years_experience=outcome["years_experience"],
                explanation=outcome["explanation"],
            )
        )

    # Best matches first
    results.sort(key=lambda r: r.match_score, reverse=True)

    return MatchResponse(
        job_description_preview=job_description[:200],
        results=results,
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


# Serve the simple frontend at "/"
app.mount("/", StaticFiles(directory="static", html=True), name="static")
