"""
Generates the report PDF using reportlab (pure Python, no system-level
dependencies - see requirements.txt). Called once, at finalize-time
(apps/reports/services.py::finalize_report) - never regenerated afterwards,
so the PDF is a permanent snapshot of the report as it existed when
finalized, even if the underlying MRIScan/AIAnalysisResult data were
somehow edited later.
"""
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_report_pdf(*, report) -> bytes:
    scan = report.mri_scan
    patient = scan.patient
    doctor_user = report.created_by_doctor.user
    analysis = getattr(scan, "analysis_result", None)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("ReportTitle", parent=styles["Title"], fontSize=18)
    heading_style = ParagraphStyle("SectionHeading", parent=styles["Heading2"], spaceBefore=14, spaceAfter=6)

    story = [
        Paragraph("Alzheimer's MRI Diagnosis Report", title_style),
        Spacer(1, 0.15 * inch),
    ]

    patient_table_data = [
        ["Patient Name", patient.full_name],
        ["National ID", patient.national_id],
        ["Date of Birth", str(patient.date_of_birth)],
        ["Gender", patient.get_gender_display()],
    ]
    story.append(Paragraph("Patient Information", heading_style))
    story.append(_styled_table(patient_table_data))

    scan_table_data = [
        ["Scan Uploaded", scan.created_at.strftime("%Y-%m-%d %H:%M UTC")],
        ["Scan Status", scan.status],
    ]
    story.append(Paragraph("Scan Information", heading_style))
    story.append(_styled_table(scan_table_data))

    if analysis is not None:
        result_table_data = [
            ["Predicted Class", analysis.predicted_class],
            ["Confidence", f"{analysis.confidence_score * 100:.1f}%"],
            ["Model Version", analysis.model_version],
        ]
        for class_name, probability in analysis.class_probabilities.items():
            result_table_data.append([f"P({class_name})", f"{probability * 100:.1f}%"])

        story.append(Paragraph("AI Analysis Result", heading_style))
        story.append(_styled_table(result_table_data))
    else:
        story.append(Paragraph("AI Analysis Result", heading_style))
        story.append(Paragraph("No completed AI analysis is available for this scan.", styles["Normal"]))

    story.append(Paragraph("Doctor's Notes", heading_style))
    notes_text = report.notes.strip() or "(No notes provided.)"
    for paragraph_text in notes_text.split("\n"):
        story.append(Paragraph(paragraph_text or "&nbsp;", styles["Normal"]))

    story.append(Spacer(1, 0.3 * inch))
    full_name = f"{doctor_user.first_name} {doctor_user.last_name}".strip() or doctor_user.username
    footer_text = (
        f"Report finalized by Dr. {full_name} "
        f"({report.created_by_doctor.specialization}, License #{report.created_by_doctor.license_number})"
    )
    story.append(Paragraph(footer_text, styles["Normal"]))

    doc.build(story)
    return buffer.getvalue()


def _styled_table(data):
    table = Table(data, colWidths=[2.2 * inch, 4 * inch])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table
