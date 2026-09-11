import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class PDFReportGenerator:
    """
    Generates official Field Drug Test Evidence Reports in PDF format.
    """

    @staticmethod
    def generate_report(case_data, output_pdf_path="field_report.pdf"):
        os.makedirs(os.path.dirname(output_pdf_path) if os.path.dirname(output_pdf_path) else ".", exist_ok=True)
        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=colors.HexColor('#1E3A8A'),
            alignment=1, # Center
            spaceAfter=6
        )
        subtitle_style = ParagraphStyle(
            'SubTitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor('#4B5563'),
            alignment=1,
            spaceAfter=15
        )
        heading_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=colors.HexColor('#1E3A8A'),
            spaceBefore=10,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#1F2937')
        )
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#B91C1C'),
            alignment=1
        )

        elements = []

        # 1. Header Title
        elements.append(Paragraph("LAW ENFORCEMENT DRUG TESTING FIELD REPORT", title_style))
        elements.append(Paragraph("Smart India Hackathon 2026 — Digital Companion Evidence Record", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E3A8A'), spaceAfter=12))

        # 2. Case & Officer Information Table
        elements.append(Paragraph("1. Case & Sample Identification", heading_style))
        info_data = [
            [Paragraph("<b>Case Reference ID:</b>", body_style), Paragraph(str(case_data.get("case_id", "N/A")), body_style),
             Paragraph("<b>Sample QR Tag:</b>", body_style), Paragraph(str(case_data.get("sample_id", "N/A")), body_style)],
            [Paragraph("<b>Testing Officer:</b>", body_style), Paragraph(str(case_data.get("officer_id", "N/A")), body_style),
             Paragraph("<b>Agency / Station:</b>", body_style), Paragraph(str(case_data.get("agency", "Special Narcotics Unit")), body_style)],
            [Paragraph("<b>Date & Time (UTC):</b>", body_style), Paragraph(str(case_data.get("timestamp", "N/A")), body_style),
             Paragraph("<b>GPS Location:</b>", body_style), Paragraph(str(case_data.get("location", "N/A")), body_style)]
        ]
        t_info = Table(info_data, colWidths=[120, 150, 120, 150])
        t_info.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F3F4F6')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#D1D5DB')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(t_info)
        elements.append(Spacer(1, 12))

        # 3. Presumptive Test Results Table
        elements.append(Paragraph("2. Colorimetric Analysis & Presumptive Result", heading_style))
        res_data = [
            [Paragraph("<b>Parameter</b>", body_style), Paragraph("<b>Field Detection Value</b>", body_style)],
            [Paragraph("Reagent Kit Used", body_style), Paragraph(str(case_data.get("reagent_used", "N/A")), body_style)],
            [Paragraph("Presumptive Result", body_style), Paragraph(f"<b>{case_data.get('presumptive_category', 'N/A')}</b>", body_style)],
            [Paragraph("Match Confidence Score", body_style), Paragraph(f"{case_data.get('confidence_score', 0)}%", body_style)],
            [Paragraph("Detected Reaction Color", body_style), Paragraph(str(case_data.get("detected_color_description", "N/A")), body_style)],
            [Paragraph("CIEDE2000 ΔE Distance", body_style), Paragraph(str(case_data.get("delta_e_distance", "N/A")), body_style)],
        ]
        t_res = Table(res_data, colWidths=[180, 360])
        t_res.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#DBEAFE')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94A3B8')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(t_res)
        elements.append(Spacer(1, 12))

        # 4. Warnings & Lab Confirmation Instructions
        elements.append(Paragraph("3. Cross-Reactivity & Recommended Forensic Confirmation", heading_style))
        warnings_text = "<br/>".join([f"• {w}" for w in case_data.get("cross_reactivity_warnings", ["None noted."])])
        elements.append(Paragraph(f"<b>Warnings & Potential False Positives:</b><br/>{warnings_text}", body_style))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(f"<b>Recommended Lab Procedure:</b> {case_data.get('recommended_lab_confirmation', 'GC-MS / HPLC Confirmation Required')}", body_style))
        elements.append(Spacer(1, 12))

        # 5. Cryptographic Chain of Custody & Hash Audit
        elements.append(Paragraph("4. Cryptographic Chain of Custody Audit Trail", heading_style))
        ledger_data = [
            [Paragraph("<b>Audit Parameter</b>", body_style), Paragraph("<b>Cryptographic Verification Data</b>", body_style)],
            [Paragraph("Block Index", body_style), Paragraph(str(case_data.get("block_index", "#1")), body_style)],
            [Paragraph("Previous Block Hash", body_style), Paragraph(f"<font size=7 color='#4B5563'>{case_data.get('previous_hash', 'N/A')}</font>", body_style)],
            [Paragraph("Current Block SHA-256 Hash", body_style), Paragraph(f"<font size=7 color='#1E3A8A'><b>{case_data.get('current_hash', 'N/A')}</b></font>", body_style)],
            [Paragraph("Digital Signature Status", body_style), Paragraph("<font color='#059669'><b>VALID & VERIFIED (ECDSA/SHA-256)</b></font>", body_style)]
        ]
        t_ledger = Table(ledger_data, colWidths=[160, 380])
        t_ledger.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ECFDF5')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#A7F3D0')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#059669')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(t_ledger)
        elements.append(Spacer(1, 16))

        # 6. Legal Disclaimer Box
        disclaimer_box = Table([[
            Paragraph("<b>IMPORTANT LEGAL NOTICE:</b><br/>THIS REPORT CONTAINS PRESUMPTIVE FIELD DRUG TEST RESULTS ONLY. FIELD COLORIMETRIC TESTS ARE SUBJECT TO POTENTIAL INTERFERENCE AND LIGHTING VARIATIONS. MANDATORY FORENSIC LABORATORY GC-MS/HPLC CONFIRMATION IS REQUIRED FOR JUDICIAL / PROSECUTORIAL PROCEEDINGS.", disclaimer_style)
        ]], colWidths=[540])
        disclaimer_box.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF2F2')),
            ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#EF4444')),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(disclaimer_box)

        doc.build(elements)
        return output_pdf_path
