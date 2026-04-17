"""
Generador de respuestas formateadas para el sistema de matching.

Crea respuestas atractivas y profesionales para mostrar los resultados
del matching de candidatos a los usuarios de RH.
"""

def generate_response(results, requirements):
    """
    Genera una respuesta formateada con los resultados del matching.

    Crea un mensaje profesional con emojis y formato legible que incluye
    información clave de cada candidato encontrado.

    Args:
        results (list): Lista de candidatos ordenados por puntuación
        requirements (dict): Requisitos originales de la búsqueda

    Returns:
        str: Respuesta formateada con lista de candidatos y recomendación
    """
    if not results:
        return "No encontré candidatos que cumplan con los criterios."

    response = "🔎 He encontrado los siguientes candidatos:\n\n"

    for i, c in enumerate(results, 1):
        skills = ", ".join(c["skills"][:3]) if c["skills"] else "No especificadas"
        areas = ", ".join(c["areas"][:2]) if c["areas"] else "No especificadas"

        response += (
            f"{i}. {c['name']}\n"
            f"   🧠 Experiencia: {c['experience']} años\n"
            f"   📊 Score: {c['score']}\n"
            f"   🛠️ Skills: {skills}\n"
            f"   📚 Áreas: {areas}\n\n"
        )

    best = results[0]

    response += (
        f"⭐ El candidato más recomendado es {best['name']} "
        f"por su mayor nivel de compatibilidad con el perfil solicitado."
    )

    return response