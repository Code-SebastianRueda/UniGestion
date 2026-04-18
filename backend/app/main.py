"""
Plataforma de Gestión de Recursos Humanos (HR Management Platform)

Esta aplicación FastAPI proporciona una plataforma completa para la gestión de recursos humanos,
incluyendo reclutamiento inteligente de candidatos, gestión de empleados, nómina, vacaciones
y generación de documentos.

Características principales:
- Registro y autenticación de usuarios (candidatos, empleados, RH)
- Subida y análisis de CVs con extracción de texto
- Matching inteligente de candidatos usando algoritmos de IA y embeddings
- Gestión de empleados: información, vacaciones, nómina
- Generación de certificados laborales y documentos PDF
- Dashboards basados en roles con interfaces HTML

Autor: Proyecto de Gestión de Proyectos - Politécnico Grancolombiano
"""

import os
from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app import models
from app.schemas import CandidateCreate
from utils import extract_text_from_pdf, extract_text_from_docx
from app.parser import parse_cv
from app.matching import calculate_score
from app.chat_parser import parse_chat_to_requirements
from app.embeddings import get_embedding, similarity
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.response_generator import generate_response
from app.documents import generate_certificate
from fastapi.responses import FileResponse
from app.matching import calculate_score, generate_response, parse_requirements as parse_requirements



models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estructura para almacenar sesiones de chat por usuario
# Cada sesión mantiene historial de conversación, resultados previos y requisitos guardados
chat_sessions = {}

# estructura:
# {
#   user_id: {
#       "history": [],
#       "last_results": [],
#       "last_requirements": {}
#   }
# }

def detect_intent(message: str):
    """
    Detecta la intención del mensaje del usuario para refinar búsquedas de candidatos.

    Args:
        message (str): Mensaje del usuario en minúsculas

    Returns:
        str: Tipo de intención detectada ("refine" o "new_search")
    """
    message = message.lower()

    if "solo" in message or "top" in message or "mejores" in message:
        return "refine"

    return "new_search"


# ==============================
# CONFIGURACIÓN DE BASE DE DATOS
# ==============================

def get_db():
    """
    Proporciona una sesión de base de datos para las dependencias de FastAPI.

    Yields:
        Session: Sesión de SQLAlchemy que se cierra automáticamente al finalizar
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def create_admin():
    """
    Crea un usuario administrador por defecto al iniciar la aplicación.

    Este evento se ejecuta una sola vez cuando la aplicación FastAPI inicia.
    Crea el usuario RH admin si no existe.
    """
    db = SessionLocal()

    existing = db.query(models.User).filter(
        models.User.email == "admin@rh.com"
    ).first()

    if not existing:
        admin = models.User(
            id="1000000000",
            name="Admin RH",
            email="admin@rh.com",
            password="123456",
            role="rh"
        )
        db.add(admin)
        db.commit()

    db.close()

# ==============================
# GESTIÓN DE CANDIDATOS
# ==============================

@app.post("/candidates")
def create_candidate(candidate: CandidateCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo candidato en el sistema.

    Verifica si el email ya existe para evitar duplicados.

    Args:
        candidate (CandidateCreate): Datos del candidato (name, email, phone)
        db (Session): Sesión de base de datos

    Returns:
        dict: Candidato creado o error si el email ya existe
    """
    existing = db.query(models.Candidate).filter(
        models.Candidate.email == candidate.email
    ).first()

    if existing:
        return {"error": "Email ya existe", "candidate_id": existing.id}

    new_candidate = models.Candidate(**candidate.dict())
    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)

    return new_candidate


# ==============================
# SUBIDA DE CV
# ==============================

@app.post("/upload-cv/{user_id}")
def upload_cv(user_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Sube y procesa un CV de candidato.

    Extrae texto del archivo (PDF o DOCX), lo parsea para obtener información estructurada
    y guarda tanto el archivo como los datos parseados en la base de datos.

    Args:
        user_id (str): ID del usuario candidato
        file (UploadFile): Archivo del CV (PDF o DOCX)
        db (Session): Sesión de base de datos

    Returns:
        dict: Confirmación del procesamiento y datos extraídos
    """
    folder = "storage/cvs"
    os.makedirs(folder, exist_ok=True)

    file_path = f"{folder}/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    else:
        text = extract_text_from_docx(file_path)

    resume = models.Resume(
        user_id=user_id,
        file_path=file_path,
        raw_text=text
    )
    db.add(resume)
    db.commit()

    parsed = parse_cv(text)

    profile = models.CandidateProfile(
        user_id=user_id,
        education=parsed["education"],
        experience_years=parsed["experience_years"],
        skills=parsed["skills"],
        areas=parsed["areas"],
        languages=parsed["languages"],
        summary=parsed["summary"]
    )

    db.add(profile)
    db.commit()

    return {"message": "CV procesado correctamente", "parsed": parsed}


# ==============================
# MATCHING DE CANDIDATOS
# ==============================

@app.post("/match")
def match_candidates(requirements: dict, db: Session = Depends(get_db)):
    """
    Encuentra candidatos que coincidan con los requisitos del puesto.

    Calcula puntuaciones para todos los perfiles de candidatos y devuelve
    los mejor calificados, con un umbral mínimo de 0.3.

    Args:
        requirements (dict): Requisitos del puesto (skills, areas, etc.)
        db (Session): Sesión de base de datos

    Returns:
        list: Lista de candidatos ordenados por puntuación descendente
    """
    profiles = db.query(models.CandidateProfile).all()

    results = []

    for profile in profiles:
        score = calculate_score(profile, requirements)

        results.append({
            "user_id": profile.user_id,
            "score": score,
            "skills": profile.skills,
            "areas": profile.areas,
            "experience": profile.experience_years
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    # 🔥 si no hay buenos matches, igual devuelve top 3
    if not any(r["score"] > 0.3 for r in results):
        results = results[:3]
    else:
        results = [r for r in results if r["score"] > 0.3]

    return results

@app.post("/chat-match")
def chat_match(query: dict, db: Session = Depends(get_db)):
    """
    Matching de candidatos basado en consultas en lenguaje natural.

    Interpreta el mensaje del usuario para extraer requisitos del puesto,
    calcula puntuaciones y genera una respuesta formateada para RH.

    Args:
        query (dict): Contiene el mensaje del usuario
        db (Session): Sesión de base de datos

    Returns:
        dict: Respuesta con texto formateado y lista de candidatos
    """
    try:
        message = query.get("message", "")

        # 🧠 interpretar mensaje
        requirements = parse_requirements(message)

        profiles = db.query(models.CandidateProfile).all()

        if not profiles:
            return {
                "response": "No hay candidatos registrados.",
                "results": []
            }

        results = []

        for profile in profiles:

            user = db.query(models.User).filter(
                models.User.id == profile.user_id
            ).first()

            if not user:
                continue

            # 🔥 proteger datos nulos
            skills = profile.skills if profile.skills else []
            areas = profile.areas if profile.areas else []
            experience = profile.experience_years if profile.experience_years else 0
            summary = profile.summary if profile.summary else ""

            # 🧠 score inteligente
            score = calculate_score(profile, requirements)

            results.append({
                "user_id": profile.user_id,
                "name": user.name,
                "score": round(score, 2),
                "skills": skills,
                "areas": areas,
                "experience": experience,
                "summary": summary
            })

        if not results:
            return {
                "response": "No se pudieron procesar candidatos.",
                "results": []
            }

        # 🔥 ordenar por score
        results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)

        # 🔥 separar relevantes
        relevant = [r for r in results if r["score"] >= 5]

        if relevant:
            results = relevant
        else:
            return {
                "response": "No encontré candidatos que coincidan con el perfil solicitado.",
                "results": []
            }

        # 🧠 generar respuesta tipo RH
        response = generate_response(results, requirements)

        return {
            "response": response,
            "results": results
        }

    except Exception as e:
        print("🔥 ERROR EN CHAT:", str(e))
        return {
            "response": "❌ Error interno del servidor",
            "results": []
        }


@app.post("/ai-match")
def ai_match(query: dict, db: Session = Depends(get_db)):
    """
    Matching semántico de candidatos usando embeddings de IA.

    Convierte la consulta y los perfiles de candidatos a vectores de embeddings
    y calcula similitud coseno para encontrar los mejores matches.

    Args:
        query (dict): Contiene el mensaje de consulta
        db (Session): Sesión de base de datos

    Returns:
        dict: Consulta original y lista de resultados ordenados por similitud
    """
    text = query.get("message", "")

    query_vector = get_embedding(text)

    profiles = db.query(models.CandidateProfile).all()

    results = []

    for profile in profiles:

        profile_text = f"""
        Skills: {profile.skills}
        Areas: {profile.areas}
        Education: {profile.education}
        Experience: {profile.experience_years}
        Summary: {profile.summary}
        """

        profile_vector = get_embedding(profile_text)

        score = similarity(query_vector, profile_vector)

        results.append({
            "candidate_id": profile.candidate_id,
            "score": round(float(score), 3),
            "skills": profile.skills,
            "areas": profile.areas
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return {
        "query": text,
        "results": results
    }


@app.get("/employees/{employee_id}/certificate")
def get_certificate(employee_id: int, db: Session = Depends(get_db)):
    """
    Genera y descarga un certificado laboral para un empleado.

    Args:
        employee_id (int): ID del empleado
        db (Session): Sesión de base de datos

    Returns:
        FileResponse: Archivo PDF del certificado laboral
    """
    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()

    if not employee:
        return {"error": "Empleado no encontrado"}

    file_path = f"storage/cert_{employee_id}.pdf"

    generate_certificate(employee, file_path)

    return FileResponse(file_path, media_type='application/pdf', filename="certificado.pdf")



@app.post("/register")
def register(user: dict, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema.

    Crea un usuario con rol de candidato por defecto. Verifica que la identificación
    no esté duplicada.

    Args:
        user (dict): Datos del usuario (id, name, email, password)
        db (Session): Sesión de base de datos

    Returns:
        dict: Usuario creado o error si la ID ya existe
    """
    existing = db.query(models.User).filter(
        models.User.id == user["id"]
    ).first()

    if existing:
        return {"error": "La identificación ya existe"}

    new_user = models.User(
        id=user["id"],  # 🔥 clave primaria
        name=user["name"],
        email=user["email"],
        password=user["password"],
        role="candidate"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    """
    Autentica a un usuario con email y contraseña.

    Args:
        data (dict): Credenciales de login (email, password)
        db (Session): Sesión de base de datos

    Returns:
        dict: Información del usuario autenticado o error
    """
    user = db.query(models.User).filter(
        models.User.email == data["email"],
        models.User.password == data["password"]
    ).first()

    if not user:
        return {"error": "Credenciales inválidas"}

    return {
        "id": user.id,
        "name": user.name,
        "role": user.role
    }


@app.put("/users/{user_id}/role")
def update_role(user_id: int, data: dict, db: Session = Depends(get_db)):
    """
    Actualiza el rol de un usuario existente.

    Args:
        user_id (int): ID del usuario a actualizar
        data (dict): Nuevo rol del usuario
        db (Session): Sesión de base de datos

    Returns:
        dict: Confirmación de actualización o error
    """
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        return {"error": "Usuario no encontrado"}

    user.role = data["role"]

    db.commit()

    return {"message": "Rol actualizado"}

def detect_advanced_intent(message: str):
    """
    Detecta intenciones avanzadas para refinar búsquedas de candidatos.

    Args:
        message (str): Mensaje del usuario en minúsculas

    Returns:
        str: Tipo de intención avanzada detectada
    """
    message = message.lower()

    if "experiencia" in message:
        return "more_experience"

    if "academico" in message or "educacion" in message:
        return "better_education"

    if "habilidades" in message or "skills" in message:
        return "more_skills"

    if "solo" in message or "top" in message:
        return "limit"

    return "new_search"

def refine_by_experience(results):
    """
    Refina resultados ordenándolos por años de experiencia descendente.

    Args:
        results (list): Lista de candidatos con sus datos

    Returns:
        list: Resultados ordenados por experiencia
    """
    return sorted(results, key=lambda x: x["experience"], reverse=True)

def refine_by_skills(results):
    """
    Refina resultados ordenándolos por cantidad de habilidades descendente.

    Args:
        results (list): Lista de candidatos con sus datos

    Returns:
        list: Resultados ordenados por número de skills
    """
    return sorted(results, key=lambda x: len(x["skills"]), reverse=True)

def refine_by_education(results):
    """
    Refina resultados ordenándolos por nivel educativo descendente.

    Args:
        results (list): Lista de candidatos con sus datos

    Returns:
        list: Resultados ordenados por puntuación educativa
    """
    def score_education(summary):
        if not summary:
            return 0

        score = 0

        if "doctorado" in summary.lower():
            score += 3
        if "maestr" in summary.lower():
            score += 2
        if "pregrado" in summary.lower() or "licenciado" in summary.lower():
            score += 1

        return score

    return sorted(results, key=lambda x: score_education(x["summary"]), reverse=True)

@app.get("/employee/{user_id}")
def get_employee(user_id: str, db: Session = Depends(get_db)):

    employee = db.query(models.Employee).filter(
        models.Employee.user_id == user_id
    ).first()

    if not employee:
        return {"error": "Empleado no encontrado"}

    return {
        "id": employee.id,
        "name": employee.name,
        "email": employee.email,
        "position": employee.position,
        "salary": employee.salary,
        "start_date": employee.start_date,
        "phone": employee.phone,
        "address": employee.address
    }


@app.get("/employee/{user_id}")
def get_employee(user_id: str, db: Session = Depends(get_db)):

    print("BUSCANDO USER_ID:", user_id)  # 🔥 DEBUG

    employee = db.query(models.Employee).filter(
        models.Employee.user_id == user_id
    ).first()

    if not employee:
        return {"error": "Empleado no encontrado"}

    return {
        "id": employee.id,
        "name": employee.name,
        "email": employee.email,
        "position": employee.position,
        "salary": employee.salary,
        "start_date": employee.start_date,
        "phone": employee.phone,
        "address": employee.address
    }


@app.get("/vacations/{user_id}")
def get_vacations(user_id: str, db: Session = Depends(get_db)):

    employee = db.query(models.Employee).filter(
        models.Employee.user_id == user_id
    ).first()

    if not employee:
        return {"error": "Empleado no encontrado"}

    vacations = db.query(models.Vacation).filter(
        models.Vacation.employee_id == employee.id
    ).all()

    return [
        {
            "start_date": v.start_date,
            "end_date": v.end_date,
            "days": v.days,
            "status": v.status
        }
        for v in vacations
    ]

@app.post("/vacations/request")
def request_vacation(data: dict, db: Session = Depends(get_db)):

    try:
        print("DATA RECIBIDA:", data)  # 🔥 DEBUG

        user_id = data.get("user_id")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        days = data.get("days")

        # 🔥 VALIDACIONES
        if not user_id or not start_date or not end_date or not days:
            return {"error": "Faltan datos"}

        employee = db.query(models.Employee).filter(
            models.Employee.user_id == user_id
        ).first()

        if not employee:
            print("❌ EMPLOYEE NO ENCONTRADO")
            return {"error": "Empleado no encontrado"}

        vacation = models.Vacation(
            employee_id=employee.id,
            start_date=start_date,
            end_date=end_date,
            days=int(days),  # 🔥 IMPORTANTE
            status="pending"
        )

        db.add(vacation)
        db.commit()

        return {"message": "Solicitud enviada correctamente"}

    except Exception as e:
        print("🔥 ERROR VACACIONES:", str(e))
        return {"error": "Error interno"}
    
@app.get("/rh/vacations")
def get_all_vacations(db: Session = Depends(get_db)):

    vacations = db.query(models.Vacation).all()

    result = []

    for v in vacations:
        employee = db.query(models.Employee).filter(
            models.Employee.id == v.employee_id
        ).first()

        result.append({
            "id": v.id,
            "employee_name": employee.name if employee else "N/A",
            "start_date": v.start_date,
            "end_date": v.end_date,
            "days": v.days,
            "status": v.status
        })

    return result

@app.put("/rh/vacations/{vacation_id}/approve")
def approve_vacation(vacation_id: int, db: Session = Depends(get_db)):

    vacation = db.query(models.Vacation).filter(
        models.Vacation.id == vacation_id
    ).first()

    if not vacation:
        return {"error": "Solicitud no encontrada"}

    vacation.status = "approved"
    db.commit()

    return {"message": "Vacaciones aprobadas"}

@app.put("/rh/vacations/{vacation_id}/reject")
def reject_vacation(vacation_id: int, db: Session = Depends(get_db)):

    vacation = db.query(models.Vacation).filter(
        models.Vacation.id == vacation_id
    ).first()

    if not vacation:
        return {"error": "Solicitud no encontrada"}

    vacation.status = "rejected"
    db.commit()

    return {"message": "Vacaciones rechazadas"}


@app.get("/payroll/{user_id}")
def get_payroll(user_id: str, db: Session = Depends(get_db)):

    employee = db.query(models.Employee).filter(
        models.Employee.user_id == user_id
    ).first()

    if not employee:
        return {"error": "Empleado no encontrado"}

    payrolls = db.query(models.Payroll).filter(
        models.Payroll.employee_id == employee.id
    ).all()

    return [
        {
            "id": p.id,
            "period": p.period,
            "salary": p.salary,
            "bonuses": p.bonuses,
            "deductions": p.deductions,
            "net_salary": p.net_salary
        }
        for p in payrolls
    ]

from fastapi.responses import FileResponse
from app.documents import generate_payroll_pdf
import os

@app.get("/payroll/download/{payroll_id}")
def download_payroll(payroll_id: int, db: Session = Depends(get_db)):

    payroll = db.query(models.Payroll).filter(
        models.Payroll.id == payroll_id
    ).first()

    if not payroll:
        return {"error": "No encontrado"}

    path = f"/tmp/payroll_{payroll_id}.pdf"

    generate_payroll_pdf({
        "period": payroll.period,
        "salary": payroll.salary,
        "bonuses": payroll.bonuses,
        "deductions": payroll.deductions,
        "net_salary": payroll.net_salary
    }, path)

    return FileResponse(path, filename="nomina.pdf")

from app.documents import generate_certificate
from fastapi.responses import FileResponse
import os

@app.get("/employee/certificate/{user_id}")
def download_certificate(user_id: str, db: Session = Depends(get_db)):

    employee = db.query(models.Employee).filter(
        models.Employee.user_id == user_id
    ).first()

    if not employee:
        return {"error": "Empleado no encontrado"}

    path = f"/tmp/certificate_{user_id}.pdf"

    generate_certificate({
        "name": employee.name,
        "user_id": user_id,
        "position": employee.position,
        "start_date": employee.start_date,
        "salary": employee.salary
    }, path)

    return FileResponse(path, filename="certificado_laboral.pdf")

@app.get("/documents/{user_id}")
def get_docs(user_id: str, db: Session = Depends(get_db)):

    employee = db.query(models.Employee).filter(
        models.Employee.user_id == user_id
    ).first()

    docs = db.query(models.Document).filter(
        models.Document.employee_id == employee.id
    ).all()

    return docs

from fastapi.responses import RedirectResponse

@app.get("/")
def root():
    return RedirectResponse(url="/auth.html")

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")