"""
Generador de CVs de prueba para el sistema de RRHH.

Crea CVs ficticios en formato PDF con datos realistas de profesores
universitarios para testing del sistema de matching de candidatos.
"""

import random
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ==============================
# DATOS BASE PARA GENERACIÓN
# ==============================

nombres = [
    "Juan Pérez", "María Gómez", "Carlos Ruiz",
    "Laura Martínez", "Andrés Torres", "Sofía Ramírez",
    "Daniel Castro", "Valentina Herrera"
]

universidades = [
    "Universidad Nacional", "Universidad de los Andes",
    "Universidad Javeriana", "Politécnico Grancolombiano",
    "Universidad Distrital", "Universidad EAN"
]

areas = [
    "Filosofía", "Matemáticas", "Programación",
    "Estadística", "Inteligencia Artificial",
    "Bases de datos", "Ética", "Lógica"
]

skills_pool = [
    "Python", "SQL", "Machine Learning",
    "Docencia", "Investigación",
    "Análisis de datos", "Docker",
    "Pensamiento crítico", "Excel"
]

idiomas_pool = [
    "Español",
    "Inglés (B1)", "Inglés (B2)", "Inglés (C1)"
]

titulos = [
    "Licenciado en {}", "Ingeniero en {}",
    "Profesional en {}"
]

posgrados = [
    "Maestría en {}", "Doctorado en {}"
]

# ==============================
# FUNCIONES GENERADORAS
# ==============================

def generar_formacion(area):
    """
    Genera formación académica aleatoria para un área específica.

    Args:
        area (str): Área de especialización

    Returns:
        list: Lista de títulos académicos con universidad y año
    """
    uni = random.choice(universidades)
    titulo = random.choice(titulos).format(area)
    posgrado = random.choice(posgrados).format(area)

    return [
        f"{titulo} - {uni} - {random.randint(2005, 2015)}",
        f"{posgrado} - {uni} - {random.randint(2016, 2022)}"
    ]

def generar_experiencia():
    """
    Genera experiencia docente aleatoria.

    Returns:
        list: Lista de experiencias laborales
    """
    exp = []
    total_years = 0

    for _ in range(random.randint(1, 3)):
        uni = random.choice(universidades)
        years = random.randint(1, 5)
        total_years += years

        exp.append(f"Profesor - {uni} - {years} años")

    return exp

def generar_lista(items, n=3):
    """
    Genera una lista aleatoria de elementos únicos.

    Args:
        items (list): Lista de elementos disponibles
        n (int): Número de elementos a seleccionar

    Returns:
        list: Lista aleatoria de elementos
    """
    return [random.choice(items) for _ in range(n)]

# ==============================
# GENERACIÓN DE PDF
# ==============================

def generar_cv_pdf(file_path):
    """
    Genera un CV completo en formato PDF con datos aleatorios.

    Args:
        file_path (str): Ruta donde guardar el PDF
    """
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(file_path)

    nombre = random.choice(nombres)
    email = nombre.lower().replace(" ", ".") + "@email.com"
    telefono = f"3{random.randint(100000000, 999999999)}"
    area_principal = random.choice(areas)

    perfil = f"Profesor universitario con experiencia en {area_principal} y enfoque en docencia e investigación."

    formacion = generar_formacion(area_principal)
    experiencia = generar_experiencia()
    areas_ensenanza = generar_lista(areas, 3)
    habilidades = generar_lista(skills_pool, 4)
    idiomas = generar_lista(idiomas_pool, 2)

    content = []

    def add(title, text):
        """Helper para añadir secciones al PDF"""
        content.append(Paragraph(f"<b>{title}</b>", styles["Heading3"]))
        content.append(Spacer(1, 6))
        content.append(Paragraph(text, styles["Normal"]))
        content.append(Spacer(1, 12))

    add("NOMBRE", nombre)
    add("EMAIL", email)
    add("TELÉFONO", telefono)

    add("PERFIL", perfil)

    add("FORMACIÓN ACADÉMICA", "<br/>".join(formacion))
    add("EXPERIENCIA DOCENTE", "<br/>".join(experiencia))
    add("ÁREAS DE ENSEÑANZA", "<br/>".join(areas_ensenanza))
    add("HABILIDADES", "<br/>".join(habilidades))
    add("IDIOMAS", "<br/>".join(idiomas))

    doc.build(content)

# ==============================
# GENERACIÓN MASIVA
# ==============================

def generar_cvs(cantidad=20, carpeta="generated_pdfs"):
    """
    Genera múltiples CVs en PDF para testing.

    Args:
        cantidad (int): Número de CVs a generar
        carpeta (str): Directorio donde guardar los PDFs
    """
    os.makedirs(carpeta, exist_ok=True)

    for i in range(cantidad):
        file_path = os.path.join(carpeta, f"cv_{i+1}.pdf")
        generar_cv_pdf(file_path)

    print(f"✅ {cantidad} CVs en PDF generados en '{carpeta}'")

# ==============================
# EJECUCIÓN PRINCIPAL
# ==============================

if __name__ == "__main__":
    generar_cvs(30)