"""
Algoritmo de matching de candidatos con requisitos de puesto.

Implementa el sistema de puntuación para encontrar candidatos que mejor
coincidan con los requisitos del puesto, usando keywords, sinónimos y
puntuación por experiencia.
"""

import unicodedata

# ==============================
# UTILIDADES
# ==============================

def normalize(text):
    """
    Normaliza texto removiendo acentos y convirtiendo a minúsculas.

    Args:
        text (str): Texto a normalizar

    Returns:
        str: Texto normalizado sin acentos
    """
    if not text:
        return ""
    text = text.lower()
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

# ==============================
# ALGORITMO DE MATCHING
# ==============================

def calculate_score(profile, requirements):
    """
    Calcula la puntuación de coincidencia entre un perfil de candidato
    y los requisitos del puesto.

    Sistema de puntuación:
    - Skills: +10 puntos por coincidencia
    - Áreas: +7 puntos por coincidencia
    - Texto del resumen: +3 puntos por coincidencia
    - Experiencia: +0.1 puntos por año

    Args:
        profile: Perfil del candidato (de CandidateProfile)
        requirements (dict): Requisitos del puesto

    Returns:
        float: Puntuación de coincidencia (0 si no hay matches)
    """
    keywords = [normalize(k) for k in requirements.get("keywords", [])]

    skills = [normalize(s) for s in (profile.skills or [])]
    areas = [normalize(a) for a in (profile.areas or [])]
    summary = normalize(profile.summary or "")

    match_score = 0

    for word in keywords:
        expanded = [word] + SYNONYMS.get(word, [])

        for w in expanded:
            # 🔥 MATCH FUERTE EN SKILLS
            for skill in skills:
                if w in skill:
                    match_score += 10   # 🔥 fuerte

            # 🔥 MATCH EN ÁREAS
            for area in areas:
                if w in area:
                    match_score += 7

            # 🔥 MATCH EN TEXTO
            if w in summary:
                match_score += 3

    # 🚨 FILTRO DURO
    if match_score == 0:
        return 0

    # experiencia solo desempata
    experience_score = (profile.experience_years or 0) * 0.1

    return round(match_score + experience_score, 2)

# ==============================
# GENERACIÓN DE RESPUESTAS
# ==============================

def generate_response(results, requirements):
    """
    Genera una respuesta formateada para mostrar los resultados del matching.

    Args:
        results (list): Lista de candidatos ordenados por puntuación
        requirements (dict): Requisitos originales

    Returns:
        str: Respuesta formateada con emojis y lista de candidatos
    """
    if not results:
        return "No encontré candidatos."

    response = "🔎 Candidatos encontrados:\n\n"

    for i, c in enumerate(results, 1):
        response += (
            f"{i}. {c['name']}\n"
            f"   Experiencia: {c['experience']} años\n"
            f"   Skills: {', '.join(c['skills'][:3]) if c['skills'] else 'N/A'}\n\n"
        )

    return response

# ==============================
# CONFIGURACIÓN DE MATCHING
# ==============================

# Palabras comunes a excluir del análisis de keywords
STOPWORDS = ["de", "la", "el", "un", "una", "necesito", "profesor", "docente"]

# Diccionario de sinónimos para mejorar el matching
SYNONYMS = {
    "algebra": ["matematicas"],
    "matematicas": ["algebra"],
    "programacion": ["python", "desarrollo"],
    "ia": ["inteligencia artificial", "machine learning"]
}

def parse_requirements(message: str):
    """
    Convierte un mensaje en lenguaje natural en requisitos estructurados.

    Filtra stopwords y extrae keywords para el matching.

    Args:
        message (str): Mensaje del usuario

    Returns:
        dict: Requisitos con lista de keywords
    """
    message = message.lower()
    words = message.split()

    keywords = [w for w in words if w not in STOPWORDS]

    return {
        "keywords": keywords
    }