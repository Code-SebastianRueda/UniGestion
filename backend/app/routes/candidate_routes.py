"""
Candidate routes.
Handles candidate profile management and CV upload.
"""
import os
import json
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Resume, CandidateProfile
from ..auth import decode_token
from ..matching import parse_cv_text, generate_embedding, build_candidate_text

router = APIRouter(prefix="/api/candidates", tags=["Candidates"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


def get_current_user_id(request: Request) -> int:
    """Extract user ID from JWT token."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No autenticado")
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    return int(payload["sub"])


@router.post("/upload-cv")
async def upload_cv(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and process a CV PDF file."""
    user_id = get_current_user_id(request)

    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF")

    # Save file
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, f"cv_{user_id}_{file.filename}")
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Extract text from PDF
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        raw_text = ""
        for page in reader.pages:
            raw_text += page.extract_text() or ""
    except Exception as e:
        raw_text = "Error extracting text from PDF"

    # Parse CV
    parsed = parse_cv_text(raw_text)

    # Generate embedding
    candidate_text = f"Habilidades: {', '.join(parsed['skills'])} | Experiencia: {', '.join(parsed['experience'])} | Educación: {', '.join(parsed['education'])} | Áreas: {', '.join(parsed['areas'])} | {parsed['summary']}"
    embedding = generate_embedding(candidate_text)

    # Save or update resume
    existing_resume = db.query(Resume).filter(Resume.user_id == user_id).first()
    if existing_resume:
        existing_resume.file_path = file_path
        existing_resume.raw_text = raw_text
        existing_resume.parsed_skills = json.dumps(parsed["skills"])
        existing_resume.parsed_experience = json.dumps(parsed["experience"])
        existing_resume.parsed_education = json.dumps(parsed["education"])
        existing_resume.parsed_languages = json.dumps(parsed["languages"])
        existing_resume.parsed_areas = json.dumps(parsed["areas"])
        existing_resume.professional_summary = parsed["summary"]
        existing_resume.embedding_vector = json.dumps(embedding)
    else:
        resume = Resume(
            user_id=user_id,
            file_path=file_path,
            raw_text=raw_text,
            parsed_skills=json.dumps(parsed["skills"]),
            parsed_experience=json.dumps(parsed["experience"]),
            parsed_education=json.dumps(parsed["education"]),
            parsed_languages=json.dumps(parsed["languages"]),
            parsed_areas=json.dumps(parsed["areas"]),
            professional_summary=parsed["summary"],
            embedding_vector=json.dumps(embedding)
        )
        db.add(resume)

    db.commit()

    return {
        "message": "CV procesado exitosamente",
        "parsed": parsed
    }


@router.get("/profile")
def get_candidate_profile(request: Request, db: Session = Depends(get_db)):
    """Get current candidate's profile."""
    user_id = get_current_user_id(request)
    user = db.query(User).filter(User.id == user_id).first()
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
    resume = db.query(Resume).filter(Resume.user_id == user_id).first()

    result = {
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        },
        "profile": None,
        "resume": None
    }

    if profile:
        result["profile"] = {
            "phone": profile.phone,
            "city": profile.city,
            "country": profile.country,
            "linkedin": profile.linkedin,
            "portfolio": profile.portfolio,
            "years_experience": profile.years_experience,
            "desired_position": profile.desired_position,
            "availability": profile.availability
        }

    if resume:
        result["resume"] = {
            "skills": json.loads(resume.parsed_skills) if resume.parsed_skills else [],
            "experience": json.loads(resume.parsed_experience) if resume.parsed_experience else [],
            "education": json.loads(resume.parsed_education) if resume.parsed_education else [],
            "languages": json.loads(resume.parsed_languages) if resume.parsed_languages else [],
            "areas": json.loads(resume.parsed_areas) if resume.parsed_areas else [],
            "summary": resume.professional_summary
        }

    return result


@router.put("/profile")
def update_candidate_profile(request: Request, db: Session = Depends(get_db)):
    """Update candidate profile information."""
    user_id = get_current_user_id(request)
    # This would accept body data - simplified for now
    return {"message": "Perfil actualizado"}


@router.get("/all")
def get_all_candidates(request: Request, db: Session = Depends(get_db)):
    """Get all candidates (RH only)."""
    user_id = get_current_user_id(request)
    user = db.query(User).filter(User.id == user_id).first()
    if user.role != "rh":
        raise HTTPException(status_code=403, detail="Acceso denegado")

    candidates = db.query(User).filter(User.role == "candidate").all()
    result = []
    for c in candidates:
        resume = db.query(Resume).filter(Resume.user_id == c.id).first()
        item = {
            "id": c.id,
            "email": c.email,
            "full_name": c.full_name,
            "has_resume": resume is not None
        }
        if resume:
            item["skills"] = json.loads(resume.parsed_skills) if resume.parsed_skills else []
            item["areas"] = json.loads(resume.parsed_areas) if resume.parsed_areas else []
        result.append(item)

    return result
