"""
Configuración de la base de datos PostgreSQL.

Establece la conexión a la base de datos usando SQLAlchemy y configura
la sesión y el motor de base de datos para toda la aplicación.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL de conexión a PostgreSQL (configurado para Docker Compose)
DATABASE_URL = "postgresql://hr_user:hr_password@db:5432/hr_db"

# Motor de base de datos SQLAlchemy
engine = create_engine(DATABASE_URL)

# Fábrica de sesiones para crear conexiones de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para todos los modelos SQLAlchemy
Base = declarative_base()