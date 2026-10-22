import io
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_certificate_pdf(
    participant_name: str,
    document_id: str,
    event_title: str,
    event_date: str,
    registration_code: str
) -> bytes:
    buffer = io.BytesIO()
    # Orientación horizontal (landscape) tipo diploma universitario
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Estilos personalizados
    title_style = ParagraphStyle(
        'CertTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        alignment=1, # Centrado
        textColor=colors.HexColor('#0F172A')
    )
    subtitle_style = ParagraphStyle(
        'CertSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        leading=18,
        alignment=1,
        textColor=colors.HexColor('#2563EB')
    )
    name_style = ParagraphStyle(
        'CertName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        alignment=1,
        textColor=colors.HexColor('#1E293B')
    )
    body_style = ParagraphStyle(
        'CertBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=18,
        alignment=1,
        textColor=colors.HexColor('#334155')
    )
    meta_style = ParagraphStyle(
        'CertMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        alignment=1,
        textColor=colors.HexColor('#64748B')
    )

    elements = []

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("UNIVERSIDAD NACIONAL AUTÓNOMA", subtitle_style))
    elements.append(Paragraph("CERTIFICADO DE ASISTENCIA Y PARTICIPACIÓN", title_style))
    elements.append(Spacer(1, 15))
    elements.append(Paragraph("Por cuanto se deja constancia formal de que:", body_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>{participant_name.upper()}</b>", name_style))
    elements.append(Paragraph(f"Documento de Identidad: <b>{document_id}</b>", body_style))
    elements.append(Spacer(1, 12))
    elements.append(
        Paragraph(
            f"Ha participado satisfactoriamente y cumplido con el 100% de asistencia obligatoria en el evento académico:",
            body_style
        )
    )
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f"<b>« {event_title} »</b>", subtitle_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Llevado a cabo en fecha: {event_date}", body_style))
    elements.append(Spacer(1, 35))

    # Tabla de firmas y validación
    sign_data = [
        [
            Paragraph("____________________________<br/><b>Comité Organizador</b><br/>Dirección Académica", body_style),
            Paragraph("____________________________<br/><b>Secretaría General</b><br/>Registro y Certificación", body_style)
        ]
    ]
    t = Table(sign_data, colWidths=[330, 330])
    t.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t)

    elements.append(Spacer(1, 25))
    elements.append(
        Paragraph(
            f"Código Único de Validación: <b>{registration_code}</b> | Emitido electrónicamente por el Sistema Universitario de Eventos",
            meta_style
        )
    )

    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
