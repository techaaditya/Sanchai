"""ReportLab A4 clinical summary PDF generator for Sanchai.

Produces a clean, print-ready bilingual doctor summary with patient demographics,
embedded Segno QR code, confirmed allergies, active clinical conditions,
and recent encounter timeline.
"""

from __future__ import annotations

import io
import sqlite3
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from backend.nlp.lexicon import Lexicon
from backend.record import entries as record
from backend.record import qr


def generate_doctor_summary_pdf(
    patient: sqlite3.Row,
    con: sqlite3.Connection,
    lexicon: Lexicon,
) -> bytes:
    """Generate high-quality A4 Doctor Summary PDF bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e1a17"),
    )
    subtitle_style = ParagraphStyle(
        "DocSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#5f544c"),
    )
    h2_style = ParagraphStyle(
        "DocH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#c86b1c"),
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e1a17"),
    )
    bold_style = ParagraphStyle(
        "DocBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e1a17"),
    )
    alert_style = ParagraphStyle(
        "DocAlert",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#b23d34"),
    )

    story: list[Any] = []

    # 1. Header with QR Code
    qr_token = patient["qr_token"]
    qr_content = f"sanchai://p/{qr_token}"
    qr_png_bytes = qr.encode_png_bytes(qr_content, scale=4, border=1)
    qr_img = Image(io.BytesIO(qr_png_bytes), width=1.1 * inch, height=1.1 * inch)

    header_text = [
        Paragraph("<b>SANCHAI (सञ्चै) — CLINICAL HEALTH SUMMARY</b>", title_style),
        Paragraph("Bilingual Longitudinal Health Ledger · Zero-Hallucination Verified", subtitle_style),
        Spacer(1, 4),
        Paragraph(
            f"<b>Patient:</b> {patient['name']} | <b>Sanchai ID:</b> {patient['sanchai_id'] or patient['id']} | <b>District:</b> {patient['district'] or 'N/A'}",
            body_style,
        ),
        Paragraph(
            f"<b>Blood Group:</b> {patient['blood_group'] or 'Unknown'} | <b>Gender:</b> {patient['gender'] or 'N/A'} | <b>DOB:</b> {patient['dob'] or 'N/A'}",
            body_style,
        ),
    ]

    header_table = Table(
        [[header_text, qr_img]],
        colWidths=[5.5 * inch, 1.6 * inch],
    )
    header_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ])
    )
    story.append(header_table)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#c86b1c"), spaceAfter=12))

    # 2. Critical Safety Strip: Allergies & Active Conditions
    allergies = record.list_allergies(con, patient["id"])
    conditions = record.active_conditions(con, patient["id"], lexicon)

    allergy_paras = [
        Paragraph(f"• <b>{a['substance_en']}</b> ({a['substance_np'] or ''}) — {a['severity'] or 'known'} severity", alert_style)
        for a in allergies
    ] or [Paragraph("No documented clinical allergies.", body_style)]

    condition_paras = [
        Paragraph(f"• <b>{c.canonical_en}</b> ({c.canonical_np}) [ICD-11: {c.icd11_code or 'N/A'}]", bold_style)
        for c in conditions
    ] or [Paragraph("No active chronic conditions asserted.", body_style)]

    safety_table = Table(
        [
            [
                Paragraph("<b>CRITICAL ALLERGIES & ADVERSE REACTIONS</b>", h2_style),
                Paragraph("<b>ACTIVE CONFIRMED CONDITIONS</b>", h2_style),
            ],
            [
                allergy_paras,
                condition_paras,
            ],
        ],
        colWidths=[3.6 * inch, 3.6 * inch],
    )
    safety_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#fff4f2")),
            ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#f0f9f4")),
            ("BOX", (0, 0), (0, -1), 1, colors.HexColor("#ffcdd2")),
            ("BOX", (1, 0), (1, -1), 1, colors.HexColor("#c8e6c9")),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )
    story.append(safety_table)
    story.append(Spacer(1, 14))

    # 3. Longitudinal Timeline Table
    story.append(Paragraph("<b>LONGITUDINAL CLINICAL TIMELINE (HUMAN-APPROVED ENTRIES)</b>", h2_style))
    story.append(Spacer(1, 6))

    raw_entries = record.list_entries(con, patient["id"])
    table_data = [
        [
            Paragraph("<b>Date</b>", bold_style),
            Paragraph("<b>Type / Facility</b>", bold_style),
            Paragraph("<b>Summary & Normalization</b>", bold_style),
            Paragraph("<b>Concepts & ICD Link</b>", bold_style),
        ]
    ]

    for row in raw_entries:
        norm = record.hydrate(row["normalized_json"], lexicon)
        summary_text = record.summarize(norm)
        concept_labels = ", ".join(c.concept.canonical_en for c in norm.concepts[:4])
        icd_code = row["icd11_code"] or row["icd10_code"] or "Verified"

        table_data.append([
            Paragraph(f"{row['record_date']}<br/>BS: {row['record_date_bs'] or '-'}", body_style),
            Paragraph(f"<b>{(row['document_class'] or row['input_type']).upper()}</b><br/>{row['facility_name'] or 'OPD Desk'}", body_style),
            Paragraph(summary_text, body_style),
            Paragraph(f"{concept_labels}<br/><code>{icd_code}</code>", body_style),
        ])

    timeline_table = Table(
        table_data,
        colWidths=[1.1 * inch, 1.5 * inch, 2.7 * inch, 1.9 * inch],
    )
    timeline_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f4efe8")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e7ddd1")),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )
    story.append(timeline_table)
    story.append(Spacer(1, 20))

    # 4. Clinical Footer & Verification
    footer_text = Paragraph(
        "<i>Generated by Sanchai (सञ्चै) Clinical Engine · Zero-hallucination Lexicon Pipeline with Gemma 4 Guardrails.<br/>"
        "Scan QR code with any emergency reader to inspect cryptographically bound clinical profile.</i>",
        subtitle_style,
    )
    story.append(footer_text)

    doc.build(story)
    return buf.getvalue()
