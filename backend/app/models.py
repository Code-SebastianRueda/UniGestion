"""
Modelos de base de datos para el sistema de gestión de recursos humanos.

Define todas las tablas y relaciones usando SQLAlchemy ORM. Los modelos incluyen:
- Usuarios y autenticación
- Perfiles de candidatos y CVs
- Información de empleados
- Nómina y beneficios
- Gestión de vacaciones
- Documentos y solicitudes

Todos los modelos heredan de Base y usan PostgreSQL como backend.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON

from app.database import Base

# ==============================
# MODELOS DE CANDIDATOS
# ==============================

class Resume(Base):
    """
    Modelo para almacenar CVs subidos por candidatos.

    Almacena la ruta del archivo y el texto extraído para procesamiento posterior.
    """
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))  # ID del usuario candidato
    file_path = Column(String)  # Ruta al archivo PDF/DOCX
    raw_text = Column(Text)  # Texto extraído del CV


class CandidateProfile(Base):
    """
    Perfil estructurado de candidato extraído del CV.

    Contiene información parseada del CV: educación, experiencia, habilidades, etc.
    """
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))  # ID del usuario candidato

    education = Column(JSON)  # Lista de títulos educativos
    experience_years = Column(Integer)  # Años de experiencia
    skills = Column(JSON)  # Lista de habilidades técnicas
    areas = Column(JSON)  # Áreas de especialización académica
    languages = Column(JSON)  # Idiomas
    summary = Column(Text)  # Resumen del perfil

# ==============================
# MODELOS DE USUARIOS Y EMPLEADOS
# ==============================

class User(Base):
    """
    Modelo base de usuarios del sistema.

    Maneja autenticación y roles para candidatos, empleados y RH.
    """
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)  # Número de identificación
    name = Column(String)  # Nombre completo
    email = Column(String, unique=True, index=True)  # Email único
    password = Column(String)  # Contraseña (debería estar hasheada)
    role = Column(String)  # Rol: candidate, rh, employee

    created_at = Column(TIMESTAMP, server_default=func.now())  # Fecha de creación


class Employee(Base):
    """
    Información detallada de empleados activos.

    Extiende la información básica del usuario con datos laborales.
    """
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))  # Referencia al usuario

    name = Column(String)  # Nombre (duplicado para consultas)
    email = Column(String, unique=True)  # Email laboral

    position = Column(String)  # Cargo actual
    salary = Column(Integer)  # Salario base
    start_date = Column(String)  # Fecha de ingreso

    phone = Column(String)  # Teléfono de contacto
    address = Column(String)  # Dirección

    created_at = Column(TIMESTAMP, server_default=func.now())

# ==============================
# MODELOS DE GESTIÓN LABORAL
# ==============================

class Payroll(Base):
    """
    Registros de nómina y pagos a empleados.

    Almacena información de salario, bonos y deducciones por período.
    """
    __tablename__ = "payrolls"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))  # Empleado

    period = Column(String)  # Período de pago (ej: "2024-01")
    salary = Column(Integer)  # Salario base
    bonuses = Column(Integer)  # Bonos adicionales
    deductions = Column(Integer)  # Deducciones
    net_salary = Column(Integer)  # Salario neto

    created_at = Column(TIMESTAMP, server_default=func.now())


class Vacation(Base):
    """
    Solicitudes y registros de vacaciones de empleados.

    Gestiona el flujo de aprobación de días de vacaciones.
    """
    __tablename__ = "vacations"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))  # Empleado solicitante

    start_date = Column(String)  # Fecha de inicio
    end_date = Column(String)  # Fecha de fin
    days = Column(Integer)  # Número de días

    status = Column(String, default="pending")  # Estado: pending, approved, rejected

    created_at = Column(TIMESTAMP, server_default=func.now())


class Document(Base):
    """
    Documentos asociados a empleados.

    Almacena certificados, contratos y otros documentos importantes.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))  # Empleado propietario

    name = Column(String)  # Nombre del documento
    file_path = Column(String)  # Ruta al archivo

    created_at = Column(TIMESTAMP, server_default=func.now())


class Request(Base):
    """
    Solicitudes generales de empleados.

    Para permisos, cambios, quejas u otras peticiones.
    """
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))  # Empleado solicitante

    type = Column(String)  # Tipo de solicitud
    description = Column(Text)  # Descripción detallada

    status = Column(String, default="open")  # Estado: open, resolved

    created_at = Column(TIMESTAMP, server_default=func.now())


class JobHistory(Base):
    """
    Historial de posiciones y salarios de empleados.

    Registra cambios de cargo y ajustes salariales a lo largo del tiempo.
    """
    __tablename__ = "job_history"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))  # Empleado

    position = Column(String)  # Cargo en ese período
    salary = Column(Integer)  # Salario en ese período

    start_date = Column(String)  # Fecha de inicio del cargo
    end_date = Column(String)  # Fecha de fin (null si actual)

