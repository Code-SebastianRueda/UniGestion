"""
Generador de documentos PDF para el sistema de RRHH.

Crea certificados laborales y comprobantes de nómina usando ReportLab.
Incluye logos institucionales y formato profesional.
"""

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.platypus import Image

def generate_certificate(data, path):
    """
    Genera un certificado laboral en formato PDF.

    Crea un documento oficial con información del empleado, cargo,
    fecha de ingreso y salario actual.

    Args:
        data (dict): Información del empleado (name, user_id, position, start_date, salary)
        path (str): Ruta donde guardar el PDF generado
    """
    styles = getSampleStyleSheet()

    title = styles["Title"]
    title.alignment = TA_CENTER

    normal = styles["Normal"]

    doc = SimpleDocTemplate(path)

    content = []
    import os

    BASE_DIR = os.path.dirname(__file__)
    logo_path = os.path.join(BASE_DIR, "assets", "logo.png")

    try:
        logo = Image(logo_path, width=2*inch, height=1*inch)
        content.append(logo)
    except Exception as e:
        print("ERROR CARGANDO LOGO:", e)

    content.append(Spacer(1, 10))

    # EMPRESA
    content.append(Paragraph("<b>POLITÉCNICO GRANCOLOMBIANO</b>", title))
    content.append(Spacer(1, 10))

    # TÍTULO
    content.append(Paragraph("CERTIFICADO LABORAL", title))
    content.append(Spacer(1, 30))

    # TEXTO
    texto = f"""
    Se certifica que <b>{data['name']}</b>, identificado con documento número
    <b>{data['user_id']}</b>, labora en nuestra institución en el cargo de
    <b>{data['position']}</b> desde el día <b>{data['start_date']}</b>.
    <br/><br/>
    Actualmente devenga un salario mensual de <b>${data['salary']}</b>.
    <br/><br/>
    Este documento se expide a solicitud del interesado para los fines que estime convenientes.
    """

    content.append(Paragraph(texto, normal))
    content.append(Spacer(1, 60))

    # FIRMA
    content.append(Paragraph("__________________________________", normal))
    content.append(Spacer(1, 5))
    content.append(Paragraph("<b>Recursos Humanos</b>", normal))
    content.append(Paragraph("Politécnico Grancolombiano", normal))

    doc.build(content)

# ==============================
# GENERACIÓN DE NÓMINA
# ==============================

from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

def generate_payroll_pdf(data, path):
    """
    Genera un comprobante de nómina en formato PDF.

    Crea un documento con el desglose de salario, bonos, deducciones
    y neto a pagar para un período específico.

    Args:
        data (dict): Datos de nómina (period, salary, bonuses, deductions, net_salary)
        path (str): Ruta donde guardar el PDF generado
    """
    styles = getSampleStyleSheet()

    title = styles["Title"]
    title.alignment = TA_CENTER

    normal = styles["Normal"]

    doc = SimpleDocTemplate(path)

    content = []
    import os

    BASE_DIR = os.path.dirname(__file__)
    logo_path = os.path.join(BASE_DIR, "assets", "logo.png")

    try:
        logo = Image(logo_path, width=2*inch, height=1*inch)
        content.append(logo)
    except Exception as e:
        print("ERROR CARGANDO LOGO:", e)

    content.append(Spacer(1, 10))

    # EMPRESA
    content.append(Paragraph("<b>POLITÉCNICO GRANCOLOMBIANO</b>", title))
    content.append(Spacer(1, 10))

    # TÍTULO
    content.append(Paragraph("DESPRENDIBLE DE NÓMINA", title))
    content.append(Spacer(1, 20))

    # PERIODO
    content.append(Paragraph(f"<b>Periodo:</b> {data['period']}", normal))
    content.append(Spacer(1, 20))

    # TABLA
    table_data = [
        ["Concepto", "Valor"],
        ["Salario", f"${data['salary']}"],
        ["Bonificaciones", f"${data['bonuses']}"],
        ["Deducciones", f"${data['deductions']}"],
        ["NETO A PAGAR", f"${data['net_salary']}"]
    ]

    table = Table(table_data, colWidths=[250, 150])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),

        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),

        ("ALIGN",(0,0),(-1,-1),"CENTER"),

        ("GRID", (0,0), (-1,-1), 1, colors.black),

        ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#e5e7eb")),
    ]))

    content.append(table)
    content.append(Spacer(1, 40))

    # FIRMA
    content.append(Paragraph("__________________________________", normal))
    content.append(Spacer(1, 5))
    content.append(Paragraph("<b>Departamento de Recursos Humanos</b>", normal))

    doc.build(content)