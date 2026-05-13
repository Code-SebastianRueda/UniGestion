"""
Seed data script.
Populates the database with demo users, employees, candidates, payroll, and vacations.
"""
import json
from datetime import date, datetime
from sqlalchemy.orm import Session

from .database import SessionLocal, engine, Base
from .models import (
    User, Resume, CandidateProfile, EmployeeProfile,
    Vacation, Payroll, InternalRequest
)
from .auth import hash_password


def seed_database():
    """Populate database with demo data."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if data already exists
        if db.query(User).count() > 0:
            print("Database already seeded. Skipping.")
            return

        print("Seeding database...")

        # --- RH Admin User ---
        rh_user = User(
            email="admin@unigestion.com",
            password_hash=hash_password("admin123"),
            full_name="María García López",
            role="rh"
        )
        db.add(rh_user)
        db.flush()

        rh_profile = EmployeeProfile(
            user_id=rh_user.id,
            employee_id="EMP-001",
            department="Recursos Humanos",
            position="Directora de RH",
            hire_date=date(2020, 1, 15),
            salary=8500000
        )
        db.add(rh_profile)

        # --- Employee Users ---
        employees_data = [
            {
                "email": "empleado@unigestion.com",
                "password": "emp123",
                "name": "Carlos Rodríguez Martínez",
                "emp_id": "EMP-002",
                "dept": "Tecnología",
                "position": "Desarrollador Senior",
                "salary": 6500000,
                "hire_date": date(2021, 3, 1)
            },
            {
                "email": "ana.torres@unigestion.com",
                "password": "emp123",
                "name": "Ana Torres Vega",
                "emp_id": "EMP-003",
                "dept": "Marketing",
                "position": "Coordinadora de Marketing",
                "salary": 5200000,
                "hire_date": date(2021, 6, 15)
            },
            {
                "email": "pedro.silva@unigestion.com",
                "password": "emp123",
                "name": "Pedro Silva Hernández",
                "emp_id": "EMP-004",
                "dept": "Finanzas",
                "position": "Analista Financiero",
                "salary": 4800000,
                "hire_date": date(2022, 2, 1)
            },
        ]

        for emp_data in employees_data:
            user = User(
                email=emp_data["email"],
                password_hash=hash_password(emp_data["password"]),
                full_name=emp_data["name"],
                role="employee"
            )
            db.add(user)
            db.flush()

            profile = EmployeeProfile(
                user_id=user.id,
                employee_id=emp_data["emp_id"],
                department=emp_data["dept"],
                position=emp_data["position"],
                salary=emp_data["salary"],
                hire_date=emp_data["hire_date"]
            )
            db.add(profile)

            # Add payroll records
            for month in range(1, 7):
                bonuses = 200000 if month % 3 == 0 else 0
                deductions = emp_data["salary"] * 0.08
                payroll = Payroll(
                    user_id=user.id,
                    period=f"2024-{month:02d}",
                    salary=emp_data["salary"],
                    bonuses=bonuses,
                    deductions=deductions,
                    net_salary=emp_data["salary"] + bonuses - deductions,
                    payment_date=date(2024, month, 28)
                )
                db.add(payroll)

        # --- Candidate Users ---
        candidates_data = [
            {
                "email": "candidato@unigestion.com",
                "password": "cand123",
                "name": "Juan Pérez Gómez",
                "skills": ["python", "fastapi", "machine learning", "sql", "docker"],
                "experience": ["Desarrollador Python en TechCorp (3 años)", "Data Scientist en DataLab (2 años)"],
                "education": ["Ingeniería de Sistemas - Universidad Nacional", "Maestría en IA - Universidad de los Andes"],
                "areas": ["tecnología", "inteligencia artificial", "data science"],
                "languages": ["español", "inglés"],
                "summary": "Desarrollador Python senior con experiencia en IA y machine learning",
                "years_exp": 5
            },
            {
                "email": "laura.mendez@gmail.com",
                "password": "cand123",
                "name": "Laura Méndez Ríos",
                "skills": ["algebra", "cálculo", "estadística", "pedagogía", "investigación", "python"],
                "experience": ["Profesora de Matemáticas en Universidad Central (4 años)", "Investigadora en COLCIENCIAS (2 años)"],
                "education": ["Licenciatura en Matemáticas - Universidad Pedagógica", "Doctorado en Educación Matemática"],
                "areas": ["educación", "academia", "docencia universitaria", "investigación"],
                "languages": ["español", "inglés", "francés"],
                "summary": "Profesora universitaria especializada en álgebra y cálculo con enfoque pedagógico innovador",
                "years_exp": 6
            },
            {
                "email": "roberto.diaz@gmail.com",
                "password": "cand123",
                "name": "Roberto Díaz Fernández",
                "skills": ["javascript", "react", "node.js", "typescript", "aws", "docker"],
                "experience": ["Frontend Developer en StartupXYZ (2 años)", "Fullstack Developer en MegaCorp (3 años)"],
                "education": ["Ingeniería de Software - Universidad Javeriana"],
                "areas": ["tecnología", "desarrollo de software"],
                "languages": ["español", "inglés"],
                "summary": "Desarrollador fullstack con experiencia en React y Node.js, enfocado en aplicaciones escalables",
                "years_exp": 5
            },
            {
                "email": "sofia.castro@gmail.com",
                "password": "cand123",
                "name": "Sofía Castro Morales",
                "skills": ["contabilidad", "finanzas", "excel", "power bi", "gestión de proyectos"],
                "experience": ["Contadora en Deloitte (3 años)", "Analista Financiera en Bancolombia (2 años)"],
                "education": ["Contaduría Pública - Universidad Externado", "Especialización en Finanzas Corporativas"],
                "areas": ["finanzas", "contabilidad", "consultoría"],
                "languages": ["español", "inglés"],
                "summary": "Contadora pública con experiencia en auditoría y análisis financiero corporativo",
                "years_exp": 5
            },
            {
                "email": "miguel.vargas@gmail.com",
                "password": "cand123",
                "name": "Miguel Vargas Ospina",
                "skills": ["deep learning", "tensorflow", "pytorch", "nlp", "python", "investigación"],
                "experience": ["Investigador en IA - Universidad de Stanford (2 años)", "ML Engineer en Google (1 año)"],
                "education": ["Ingeniería Electrónica - Universidad de Antioquia", "PhD en Computer Science - Stanford"],
                "areas": ["inteligencia artificial", "investigación", "tecnología"],
                "languages": ["español", "inglés", "alemán"],
                "summary": "Investigador en inteligencia artificial con publicaciones en NLP y deep learning",
                "years_exp": 4
            },
        ]

        for cand_data in candidates_data:
            user = User(
                email=cand_data["email"],
                password_hash=hash_password(cand_data["password"]),
                full_name=cand_data["name"],
                role="candidate"
            )
            db.add(user)
            db.flush()

            profile = CandidateProfile(
                user_id=user.id,
                years_experience=cand_data["years_exp"]
            )
            db.add(profile)

            # Create resume with parsed data
            resume = Resume(
                user_id=user.id,
                raw_text=f"CV de {cand_data['name']}",
                parsed_skills=json.dumps(cand_data["skills"]),
                parsed_experience=json.dumps(cand_data["experience"]),
                parsed_education=json.dumps(cand_data["education"]),
                parsed_areas=json.dumps(cand_data["areas"]),
                parsed_languages=json.dumps(cand_data["languages"]),
                professional_summary=cand_data["summary"]
            )
            db.add(resume)

        # --- Demo Vacations ---
        # Get first employee
        first_emp = db.query(User).filter(User.email == "empleado@unigestion.com").first()
        if first_emp:
            vacation = Vacation(
                user_id=first_emp.id,
                start_date=date(2024, 7, 1),
                end_date=date(2024, 7, 10),
                days_requested=10,
                reason="Vacaciones familiares",
                status="pending"
            )
            db.add(vacation)

            vacation2 = Vacation(
                user_id=first_emp.id,
                start_date=date(2024, 3, 15),
                end_date=date(2024, 3, 18),
                days_requested=4,
                reason="Asuntos personales",
                status="approved"
            )
            db.add(vacation2)

        # --- Demo Internal Requests ---
        if first_emp:
            req = InternalRequest(
                user_id=first_emp.id,
                request_type="permisos",
                subject="Permiso médico",
                description="Solicito permiso para cita médica el próximo lunes",
                status="pending"
            )
            db.add(req)

        db.commit()
        print("Database seeded successfully!")
        print("Demo credentials:")
        print("  RH: admin@unigestion.com / admin123")
        print("  Employee: empleado@unigestion.com / emp123")
        print("  Candidate: candidato@unigestion.com / cand123")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
