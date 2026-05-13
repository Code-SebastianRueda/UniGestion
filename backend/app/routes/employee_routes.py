"""
Employee routes.
Handles employee portal functionality: profile, vacations, payroll, certificates, requests.
"""
import json
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..models import User, EmployeeProfile, Vacation, Payroll, InternalRequest
from ..auth import decode_token
from ..documents import generate_payroll_pdf, generate_certificate_pdf

router = APIRouter(prefix="/api/employee", tags=["Employee"])


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


class VacationRequest(BaseModel):
    start_date: str
    end_date: str
    reason: str


class InternalRequestCreate(BaseModel):
    request_type: str
    subject: str
    description: str


@router.get("/profile")
def get_employee_profile(request: Request, db: Session = Depends(get_db)):
    """Get employee profile and dashboard data."""
    user_id = get_current_user_id(request)
    user = db.query(User).filter(User.id == user_id).first()

    if user.role not in ["employee", "rh"]:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == user_id).first()

    # Get counts
    vacations_count = db.query(Vacation).filter(
        Vacation.user_id == user_id, Vacation.status == "pending"
    ).count()
    requests_count = db.query(InternalRequest).filter(
        InternalRequest.user_id == user_id, InternalRequest.status == "pending"
    ).count()

    result = {
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        },
        "profile": None,
        "stats": {
            "pending_vacations": vacations_count,
            "pending_requests": requests_count
        }
    }

    if profile:
        result["profile"] = {
            "employee_id": profile.employee_id,
            "department": profile.department,
            "position": profile.position,
            "hire_date": str(profile.hire_date) if profile.hire_date else None,
            "salary": profile.salary,
            "phone": profile.phone,
            "address": profile.address,
            "emergency_contact": profile.emergency_contact,
            "emergency_phone": profile.emergency_phone
        }

    return result


# --- VACATIONS ---

@router.get("/vacations")
def get_vacations(request: Request, db: Session = Depends(get_db)):
    """Get employee's vacation requests."""
    user_id = get_current_user_id(request)
    vacations = db.query(Vacation).filter(Vacation.user_id == user_id).order_by(Vacation.created_at.desc()).all()

    return [{
        "id": v.id,
        "start_date": str(v.start_date),
        "end_date": str(v.end_date),
        "days_requested": v.days_requested,
        "reason": v.reason,
        "status": v.status,
        "created_at": str(v.created_at)
    } for v in vacations]


@router.post("/vacations")
def request_vacation(data: VacationRequest, request: Request, db: Session = Depends(get_db)):
    """Submit a vacation request."""
    user_id = get_current_user_id(request)

    start = date.fromisoformat(data.start_date)
    end = date.fromisoformat(data.end_date)
    days = (end - start).days + 1

    if days <= 0:
        raise HTTPException(status_code=400, detail="Fechas inválidas")

    vacation = Vacation(
        user_id=user_id,
        start_date=start,
        end_date=end,
        days_requested=days,
        reason=data.reason,
        status="pending"
    )
    db.add(vacation)
    db.commit()

    return {"message": "Solicitud de vacaciones enviada", "days": days}


# --- PAYROLL ---

@router.get("/payroll")
def get_payroll_history(request: Request, db: Session = Depends(get_db)):
    """Get employee's payroll history."""
    user_id = get_current_user_id(request)
    payrolls = db.query(Payroll).filter(Payroll.user_id == user_id).order_by(Payroll.period.desc()).all()

    return [{
        "id": p.id,
        "period": p.period,
        "salary": p.salary,
        "bonuses": p.bonuses,
        "deductions": p.deductions,
        "net_salary": p.net_salary,
        "payment_date": str(p.payment_date) if p.payment_date else None
    } for p in payrolls]


@router.get("/payroll/{payroll_id}/pdf")
def download_payroll_pdf(payroll_id: int, request: Request, db: Session = Depends(get_db)):
    """Download payroll slip as PDF."""
    user_id = get_current_user_id(request)
    payroll = db.query(Payroll).filter(Payroll.id == payroll_id, Payroll.user_id == user_id).first()

    if not payroll:
        raise HTTPException(status_code=404, detail="Nómina no encontrada")

    user = db.query(User).filter(User.id == user_id).first()
    profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == user_id).first()

    employee_data = {
        "full_name": user.full_name,
        "employee_id": profile.employee_id if profile else "N/A",
        "department": profile.department if profile else "N/A",
        "position": profile.position if profile else "N/A"
    }

    payroll_data = {
        "period": payroll.period,
        "salary": payroll.salary,
        "bonuses": payroll.bonuses,
        "deductions": payroll.deductions,
        "net_salary": payroll.net_salary,
        "payment_date": str(payroll.payment_date) if payroll.payment_date else str(date.today())
    }

    pdf_buffer = generate_payroll_pdf(employee_data, payroll_data)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=nomina_{payroll.period}.pdf"}
    )


# --- CERTIFICATES ---

@router.get("/certificate")
def download_certificate(request: Request, db: Session = Depends(get_db)):
    """Generate and download work certificate PDF."""
    user_id = get_current_user_id(request)
    user = db.query(User).filter(User.id == user_id).first()
    profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == user_id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Perfil de empleado no encontrado")

    employee_data = {
        "full_name": user.full_name,
        "employee_id": profile.employee_id,
        "department": profile.department,
        "position": profile.position,
        "hire_date": str(profile.hire_date) if profile.hire_date else "N/A"
    }

    pdf_buffer = generate_certificate_pdf(employee_data)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=certificado_laboral_{user.full_name}.pdf"}
    )


# --- INTERNAL REQUESTS ---

@router.get("/requests")
def get_requests(request: Request, db: Session = Depends(get_db)):
    """Get employee's internal requests."""
    user_id = get_current_user_id(request)
    requests_list = db.query(InternalRequest).filter(
        InternalRequest.user_id == user_id
    ).order_by(InternalRequest.created_at.desc()).all()

    return [{
        "id": r.id,
        "request_type": r.request_type,
        "subject": r.subject,
        "description": r.description,
        "status": r.status,
        "response": r.response,
        "created_at": str(r.created_at)
    } for r in requests_list]


@router.post("/requests")
def create_request(data: InternalRequestCreate, request: Request, db: Session = Depends(get_db)):
    """Create an internal request."""
    user_id = get_current_user_id(request)

    new_request = InternalRequest(
        user_id=user_id,
        request_type=data.request_type,
        subject=data.subject,
        description=data.description,
        status="pending"
    )
    db.add(new_request)
    db.commit()

    return {"message": "Solicitud creada exitosamente"}
