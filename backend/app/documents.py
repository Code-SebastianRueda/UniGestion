"""
Document generation module.
Generates professional PDF documents using ReportLab.
"""
import os
from datetime import date, datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
COMPANY_NAME = "UniGestión HR Platform"
COMPANY_ADDRESS = "Av. Principal #123, Ciudad Empresarial"
COMPANY_PHONE = "+57 300 123 4567"


def _get_logo():
    """Get logo image if exists, otherwise return None."""
    if os.path.exists(LOGO_PATH):
        return Image(LOGO_PATH, width=1.5*inch, height=0.75*inch)
    return None


def _get_styles():
    """Get custom paragraph styles."""
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=20,
        textColor=colors.HexColor('#1a237e')
    ))
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY
    ))
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    ))
    return styles


def generate_payroll_pdf(employee_data: dict, payroll_data: dict) -> BytesIO:
    """
    Generate a professional payroll slip PDF.
    
    Args:
        employee_data: Dict with employee info (name, id, department, position)
        payroll_data: Dict with payroll info (period, salary, bonuses, deductions, net_salary)
    
    Returns:
        BytesIO buffer with the PDF content
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*cm, bottomMargin=1*cm)
    elements = []
    styles = _get_styles()

    # Header with logo
    logo = _get_logo()
    if logo:
        elements.append(logo)
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(COMPANY_NAME, styles['CustomTitle']))
    elements.append(Paragraph(COMPANY_ADDRESS, styles['Normal']))
    elements.append(Spacer(1, 20))

    # Title
    elements.append(Paragraph("COMPROBANTE DE NÓMINA", styles['CustomTitle']))
    elements.append(Spacer(1, 15))

    # Employee info table
    emp_data = [
        ["Empleado:", employee_data.get("full_name", "N/A")],
        ["ID Empleado:", employee_data.get("employee_id", "N/A")],
        ["Departamento:", employee_data.get("department", "N/A")],
        ["Cargo:", employee_data.get("position", "N/A")],
        ["Período:", payroll_data.get("period", "N/A")],
    ]
    emp_table = Table(emp_data, colWidths=[2.5*inch, 4*inch])
    emp_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(emp_table)
    elements.append(Spacer(1, 25))

    # Payroll details table
    payroll_table_data = [
        ["Concepto", "Valor"],
        ["Salario Base", f"${payroll_data.get('salary', 0):,.2f}"],
        ["Bonificaciones", f"${payroll_data.get('bonuses', 0):,.2f}"],
        ["Deducciones", f"-${payroll_data.get('deductions', 0):,.2f}"],
        ["", ""],
        ["SALARIO NETO", f"${payroll_data.get('net_salary', 0):,.2f}"],
    ]
    pay_table = Table(payroll_table_data, colWidths=[3.5*inch, 3*inch])
    pay_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8eaf6')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
    ]))
    elements.append(pay_table)
    elements.append(Spacer(1, 30))

    # Payment date
    elements.append(Paragraph(
        f"Fecha de pago: {payroll_data.get('payment_date', date.today().isoformat())}",
        styles['CustomBody']
    ))
    elements.append(Spacer(1, 40))

    # Footer
    elements.append(Paragraph(
        f"Documento generado automáticamente por {COMPANY_NAME} - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        styles['Footer']
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_certificate_pdf(employee_data: dict) -> BytesIO:
    """
    Generate a professional work certificate PDF.
    
    Args:
        employee_data: Dict with employee info
    
    Returns:
        BytesIO buffer with the PDF content
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    styles = _get_styles()

    # Header
    logo = _get_logo()
    if logo:
        elements.append(logo)
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(COMPANY_NAME, styles['CustomTitle']))
    elements.append(Paragraph(COMPANY_ADDRESS, styles['Normal']))
    elements.append(Paragraph(COMPANY_PHONE, styles['Normal']))
    elements.append(Spacer(1, 40))

    # Title
    elements.append(Paragraph("CERTIFICADO LABORAL", styles['CustomTitle']))
    elements.append(Spacer(1, 30))

    # Body
    full_name = employee_data.get("full_name", "N/A")
    employee_id = employee_data.get("employee_id", "N/A")
    position = employee_data.get("position", "N/A")
    department = employee_data.get("department", "N/A")
    hire_date = employee_data.get("hire_date", "N/A")

    body_text = f"""
    El departamento de Recursos Humanos de <b>{COMPANY_NAME}</b> certifica que:
    <br/><br/>
    <b>{full_name}</b>, identificado(a) con código de empleado <b>{employee_id}</b>,
    se encuentra vinculado(a) a nuestra organización desde el <b>{hire_date}</b>,
    desempeñando el cargo de <b>{position}</b> en el departamento de <b>{department}</b>.
    <br/><br/>
    El presente certificado se expide a solicitud del interesado(a) para los fines
    que estime convenientes.
    <br/><br/>
    Dado en la ciudad, a los {date.today().day} días del mes de {date.today().strftime('%B')} de {date.today().year}.
    """
    elements.append(Paragraph(body_text, styles['CustomBody']))
    elements.append(Spacer(1, 60))

    # Signature
    elements.append(Paragraph("_" * 40, styles['Normal']))
    elements.append(Paragraph("<b>Departamento de Recursos Humanos</b>", styles['Normal']))
    elements.append(Paragraph(COMPANY_NAME, styles['Normal']))
    elements.append(Spacer(1, 40))

    # Footer
    elements.append(Paragraph(
        f"Documento generado automáticamente - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        styles['Footer']
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
