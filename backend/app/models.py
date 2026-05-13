"""
SQLAlchemy models for the HR Platform.
Defines all database tables and relationships.
"""
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, Date,
    ForeignKey, Enum, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .database import Base


class UserRole(str, enum.Enum):
    CANDIDATE = "candidate"
    EMPLOYEE = "employee"
    RH = "rh"


class VacationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class RequestType(str, enum.Enum):
    PERMISSION = "permisos"
    CERTIFICATE = "certificados"
    DATA_UPDATE = "actualización datos"
    GENERAL = "solicitudes generales"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.CANDIDATE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    resume = relationship("Resume", back_populates="user", uselist=False)
    candidate_profile = relationship("CandidateProfile", back_populates="user", uselist=False)
    employee_profile = relationship("EmployeeProfile", back_populates="user", uselist=False)
    vacations = relationship("Vacation", back_populates="user", foreign_keys="[Vacation.user_id]")
    payrolls = relationship("Payroll", back_populates="user")
    requests = relationship("InternalRequest", back_populates="user", foreign_keys="[InternalRequest.user_id]")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_path = Column(String(500))
    raw_text = Column(Text)
    parsed_skills = Column(Text)  # JSON string
    parsed_experience = Column(Text)  # JSON string
    parsed_education = Column(Text)  # JSON string
    parsed_languages = Column(Text)  # JSON string
    parsed_areas = Column(Text)  # JSON string
    professional_summary = Column(Text)
    embedding_vector = Column(Text)  # JSON string of float array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="resume")


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    phone = Column(String(50))
    city = Column(String(100))
    country = Column(String(100))
    linkedin = Column(String(255))
    portfolio = Column(String(255))
    years_experience = Column(Integer, default=0)
    desired_position = Column(String(255))
    availability = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="candidate_profile")


class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    employee_id = Column(String(50), unique=True)
    department = Column(String(100))
    position = Column(String(255))
    hire_date = Column(Date)
    salary = Column(Float)
    phone = Column(String(50))
    address = Column(Text)
    emergency_contact = Column(String(255))
    emergency_phone = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="employee_profile")


class Vacation(Base):
    __tablename__ = "vacations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_requested = Column(Integer, nullable=False)
    reason = Column(Text)
    status = Column(String(50), default=VacationStatus.PENDING)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="vacations", foreign_keys=[user_id])


class Payroll(Base):
    __tablename__ = "payrolls"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    period = Column(String(50), nullable=False)  # e.g., "2024-01"
    salary = Column(Float, nullable=False)
    bonuses = Column(Float, default=0.0)
    deductions = Column(Float, default=0.0)
    net_salary = Column(Float, nullable=False)
    payment_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="payrolls")


class InternalRequest(Base):
    __tablename__ = "internal_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    request_type = Column(String(100), nullable=False)
    subject = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default=RequestStatus.PENDING)
    response = Column(Text)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="requests", foreign_keys=[user_id])
