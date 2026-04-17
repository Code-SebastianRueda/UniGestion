"""
Parser de lenguaje natural para consultas de reclutamiento.

Convierte mensajes en lenguaje natural de RH en requisitos estructurados
para búsqueda de candidatos. Incluye bases de conocimiento de skills y áreas.
"""

import re

# ==============================
# BASE DE CONOCIMIENTO
# ==============================

# Lista de habilidades técnicas reconocidas en el sistema
SKILLS_DB = [
    "python", "sql", "machine learning",
    "docker", "excel", "investigación"
]

# Áreas académicas de especialización
AREAS_DB = [
    "programación", "matemáticas", "filosofía",
    "inteligencia artificial", "bases de datos",
    "ética", "lógica"
]

# ==============================
# FUNCIONES DE EXTRACCIÓN
# ==============================

def extract_skills(text):
    """
    Extrae habilidades mencionadas en el texto.

    Args:
        text (str): Texto a analizar

    Returns:
        list: Lista de skills encontrados en la base de conocimiento
    """
    text = text.lower()
    return [skill for skill in SKILLS_DB if skill in text]

def extract_areas(text):
    """
    Extrae áreas académicas mencionadas en el texto.

    Args:
        text (str): Texto a analizar

    Returns:
        list: Lista de áreas encontradas en la base de conocimiento
    """
    text = text.lower()
    return [area for area in AREAS_DB if area in text]

def extract_experience(text):
    """
    Extrae años de experiencia requeridos usando expresiones regulares.

    Busca patrones como "5 años" o "3 years".

    Args:
        text (str): Texto a analizar

    Returns:
        int: Número de años de experiencia (0 si no encuentra)
    """
    match = re.search(r'(\d+)\s*(años|years)', text.lower())
    return int(match.group(1)) if match else 0

def extract_education(text):
    """
    Extrae nivel educativo requerido.

    Args:
        text (str): Texto a analizar

    Returns:
        str: Nivel educativo ("doctorado", "maestria", o vacío)
    """
    text = text.lower()

    if "doctorado" in text:
        return "doctorado"
    if "maestr" in text or "magister" in text:
        return "maestria"

    return ""

# ==============================
# PARSER PRINCIPAL
# ==============================

def parse_chat_to_requirements(text):
    """
    Función principal que convierte una consulta en lenguaje natural
    en requisitos estructurados para matching de candidatos.

    Args:
        text (str): Consulta en lenguaje natural (ej: "Necesito programador Python con 3 años")

    Returns:
        dict: Requisitos estructurados con skills, areas, experiencia y educación
    """
    return {
        "skills": extract_skills(text),
        "areas": extract_areas(text),
        "min_experience": extract_experience(text),
        "education": extract_education(text)
    }