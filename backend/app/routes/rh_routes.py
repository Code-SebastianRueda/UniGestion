"""
RH (Human Resources) routes.
Handles dashboard, candidate management, vacation approvals, and chat AI.
"""
import json
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from ..database import get_db
from ..models import (
    User, Resume, CandidateProfile, EmployeeProfile,
    Vacation, Payroll, InternalRequest
)
from ..auth import decode_token
from ..matching import search_candidates, generate_embedding

router = APIRouter(prefix="/api/rh", tags=["RH"])


def get_current_rh_user(request: Request, db: Session) -> User:
    """Verify current user is RH."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No autenticado")
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user or user.role != "rh":
        raise HTTPException(status_code=403, detail="Acceso denegado - Solo RH")
    return user


class ChatMessage(BaseModel):
    message: str
    history: Optional[List[dict]] = []


class VacationAction(BaseModel):
    action: str  # "approved" or "rejected"


class RequestAction(BaseModel):
    action: str  # "approved", "rejected", "completed"
    response: Optional[str] = ""


class ConvertToEmployee(BaseModel):
    user_id: int
    employee_id: str
    department: str
    position: str
    salary: float


# --- DASHBOARD ---

@router.get("/dashboard")
def get_dashboard(request: Request, db: Session = Depends(get_db)):
    """Get RH dashboard statistics."""
    user = get_current_rh_user(request, db)

    total_employees = db.query(User).filter(User.role == "employee").count()
    total_candidates = db.query(User).filter(User.role == "candidate").count()
    pending_vacations = db.query(Vacation).filter(Vacation.status == "pending").count()
    pending_requests = db.query(InternalRequest).filter(InternalRequest.status == "pending").count()
    total_rh = db.query(User).filter(User.role == "rh").count()

    return {
        "total_employees": total_employees,
        "total_candidates": total_candidates,
        "pending_vacations": pending_vacations,
        "pending_requests": pending_requests,
        "total_rh": total_rh,
        "total_users": total_employees + total_candidates + total_rh
    }


# --- CANDIDATES MANAGEMENT ---

@router.get("/candidates")
def list_candidates(request: Request, db: Session = Depends(get_db)):
    """List all candidates with their resume info."""
    user = get_current_rh_user(request, db)

    candidates = db.query(User).filter(User.role == "candidate").all()
    result = []

    for c in candidates:
        resume = db.query(Resume).filter(Resume.user_id == c.id).first()
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == c.id).first()

        item = {
            "id": c.id,
            "email": c.email,
            "full_name": c.full_name,
            "created_at": str(c.created_at),
            "has_resume": resume is not None,
            "skills": [],
            "areas": [],
            "years_experience": profile.years_experience if profile else 0
        }

        if resume:
            item["skills"] = json.loads(resume.parsed_skills) if resume.parsed_skills else []
            item["areas"] = json.loads(resume.parsed_areas) if resume.parsed_areas else []
            item["summary"] = resume.professional_summary

        result.append(item)

    return result


@router.post("/convert-employee")
def convert_to_employee(data: ConvertToEmployee, request: Request, db: Session = Depends(get_db)):
    """Convert a candidate to employee."""
    user = get_current_rh_user(request, db)

    candidate = db.query(User).filter(User.id == data.user_id, User.role == "candidate").first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidato no encontrado")

    # Update role
    candidate.role = "employee"

    # Create employee profile
    emp_profile = EmployeeProfile(
        user_id=candidate.id,
        employee_id=data.employee_id,
        department=data.department,
        position=data.position,
        salary=data.salary,
        hire_date=date.today()
    )
    db.add(emp_profile)
    db.commit()

    return {"message": f"{candidate.full_name} convertido a empleado exitosamente"}


# --- VACATIONS MANAGEMENT ---

@router.get("/vacations")
def list_vacations(request: Request, db: Session = Depends(get_db)):
    """List all vacation requests."""
    user = get_current_rh_user(request, db)

    vacations = db.query(Vacation).order_by(Vacation.created_at.desc()).all()
    result = []

    for v in vacations:
        emp = db.query(User).filter(User.id == v.user_id).first()
        result.append({
            "id": v.id,
            "employee_name": emp.full_name if emp else "N/A",
            "start_date": str(v.start_date),
            "end_date": str(v.end_date),
            "days_requested": v.days_requested,
            "reason": v.reason,
            "status": v.status,
            "created_at": str(v.created_at)
        })

    return result


@router.put("/vacations/{vacation_id}")
def manage_vacation(vacation_id: int, data: VacationAction, request: Request, db: Session = Depends(get_db)):
    """Approve or reject a vacation request."""
    user = get_current_rh_user(request, db)

    vacation = db.query(Vacation).filter(Vacation.id == vacation_id).first()
    if not vacation:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    vacation.status = data.action
    vacation.reviewed_by = user.id
    vacation.review_date = datetime.utcnow()
    db.commit()

    return {"message": f"Vacación {data.action}"}


# --- INTERNAL REQUESTS MANAGEMENT ---

@router.get("/requests")
def list_requests(request: Request, db: Session = Depends(get_db)):
    """List all internal requests."""
    user = get_current_rh_user(request, db)

    requests_list = db.query(InternalRequest).order_by(InternalRequest.created_at.desc()).all()
    result = []

    for r in requests_list:
        emp = db.query(User).filter(User.id == r.user_id).first()
        result.append({
            "id": r.id,
            "employee_name": emp.full_name if emp else "N/A",
            "request_type": r.request_type,
            "subject": r.subject,
            "description": r.description,
            "status": r.status,
            "response": r.response,
            "created_at": str(r.created_at)
        })

    return result


@router.put("/requests/{request_id}")
def manage_request(request_id: int, data: RequestAction, request: Request, db: Session = Depends(get_db)):
    """Approve, reject or complete an internal request."""
    user = get_current_rh_user(request, db)

    req = db.query(InternalRequest).filter(InternalRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    req.status = data.action
    req.response = data.response
    req.reviewed_by = user.id
    db.commit()

    return {"message": f"Solicitud {data.action}"}


# --- AI CHAT ---

@router.post("/chat")
def chat_search(data: ChatMessage, request: Request, db: Session = Depends(get_db)):
    """
    AI-powered chat for candidate search.
    Supports natural language queries with conversational context.
    """
    user = get_current_rh_user(request, db)

    query = data.message.strip()
    if not query:
        return {"response": "Por favor, escribe una consulta para buscar candidatos.", "candidates": []}

    # Get all candidates with resumes
    candidates_data = []
    candidates = db.query(User).filter(User.role == "candidate").all()

    for c in candidates:
        resume = db.query(Resume).filter(Resume.user_id == c.id).first()
        if resume and resume.parsed_skills:
            profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == c.id).first()
            candidates_data.append({
                "user_id": c.id,
                "full_name": c.full_name,
                "email": c.email,
                "parsed_skills": resume.parsed_skills,
                "parsed_experience": resume.parsed_experience,
                "parsed_education": resume.parsed_education,
                "parsed_areas": resume.parsed_areas,
                "parsed_languages": resume.parsed_languages,
                "professional_summary": resume.professional_summary,
                "embedding_vector": resume.embedding_vector,
                "years_experience": profile.years_experience if profile else 0
            })

    if not candidates_data:
        return {
            "response": "No hay candidatos con CV procesado en el sistema. Los candidatos deben subir su hoja de vida primero.",
            "candidates": []
        }

    # Build context from history
    context = query
    if data.history:
        recent_context = " ".join([h.get("content", "") for h in data.history[-3:] if h.get("role") == "user"])
        if recent_context:
            context = f"{recent_context} {query}"

    # Search using AI matching
    results = search_candidates(context, candidates_data, top_k=5, threshold=0.2)

    if not results:
        response_text = f"No encontré candidatos que coincidan con '{query}'. Intenta con otros términos o habilidades específicas."
    else:
        response_text = f"Encontré {len(results)} candidato(s) relevantes para tu búsqueda:\n\n"
        for i, r in enumerate(results, 1):
            response_text += f"**{i}. {r['full_name']}** (Score: {r['score']}%)\n"
            response_text += f"   • Skills: {', '.join(r['skills'][:5])}\n"
            response_text += f"   • Áreas: {', '.join(r['areas'][:3])}\n"
            response_text += f"   • Experiencia: {r['years_experience']} años\n"
            response_text += f"   • Resumen: {r['summary'][:100]}...\n\n"

    return {
        "response": response_text,
        "candidates": results
    }


# --- EMPLOYEES LIST ---

@router.get("/employees")
def list_employees(request: Request, db: Session = Depends(get_db)):
    """List all employees."""
    user = get_current_rh_user(request, db)

    employees = db.query(User).filter(User.role == "employee").all()
    result = []

    for e in employees:
        profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == e.id).first()
        result.append({
            "id": e.id,
            "email": e.email,
            "full_name": e.full_name,
            "employee_id": profile.employee_id if profile else "N/A",
            "department": profile.department if profile else "N/A",
            "position": profile.position if profile else "N/A",
            "hire_date": str(profile.hire_date) if profile and profile.hire_date else "N/A"
        })

    return result
