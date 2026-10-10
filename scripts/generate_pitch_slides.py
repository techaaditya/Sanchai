"""Script to generate professional 16:9 widescreen presentation PDF slides for Sanchai."""

from pathlib import Path
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# Register Unicode fonts available on Windows
try:
    pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", "C:/Windows/Fonts/arialbd.ttf"))
    pdfmetrics.registerFont(TTFont("Mangal", "C:/Windows/Fonts/mangal.ttf"))
    pdfmetrics.registerFont(TTFont("Mangal-Bold", "C:/Windows/Fonts/mangalb.ttf"))
    FONT_NORMAL = "Arial"
    FONT_BOLD = "Arial-Bold"
    FONT_DEVA = "Mangal"
    FONT_DEVA_BOLD = "Mangal-Bold"
except Exception:
    FONT_NORMAL = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"
    FONT_DEVA = "Helvetica"
    FONT_DEVA_BOLD = "Helvetica-Bold"

PAGE_WIDTH = 960
PAGE_HEIGHT = 540

# Color Palette (Sanchai Clinical Theme)
BG_COLOR = HexColor("#FAF4ED")        # Warm Paper Canvas
CARD_BG = HexColor("#FFFFFF")         # Pure White
BORDER_COLOR = HexColor("#E5DACD")    # Warm Sand Border
TEXT_PRIMARY = HexColor("#1C1917")    # Deep Stone Ink
TEXT_SECONDARY = HexColor("#575047")  # Muted Warm Charcoal
TEXT_MUTED = HexColor("#8C8278")      # Soft Gray
ACCENT_ORANGE = HexColor("#C86B1C")   # Clinical Terracotta
EMERALD_OK = HexColor("#1F8A5B")      # Medical Emerald
BADGE_BG_ORANGE = HexColor("#FDF0E2") # Soft Orange Tint
BADGE_BG_GREEN = HexColor("#E8F6ED")  # Soft Emerald Tint
CRIMSON_DANGER = HexColor("#D9383A")  # Alert Crimson
BADGE_BG_RED = HexColor("#FDECEC")    # Soft Crimson Tint
NAVY_HEADER = HexColor("#0F172A")     # Dark Slate Accent


def draw_background(c: canvas.Canvas):
    """Draws warm paper canvas with subtle top accent stripe."""
    c.setFillColor(BG_COLOR)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=True, stroke=False)
    
    # Top clinical accent stripe
    c.setFillColor(ACCENT_ORANGE)
    c.rect(0, PAGE_HEIGHT - 6, PAGE_WIDTH, 6, fill=True, stroke=False)


def draw_footer(c: canvas.Canvas, current_slide: int, total_slides: int = 7):
    """Draws consistent presentation footer."""
    c.setStrokeColor(BORDER_COLOR)
    c.setLineWidth(1)
    c.line(40, 36, PAGE_WIDTH - 40, 36)

    # Footer Left: Brand
    c.setFont(FONT_BOLD, 9)
    c.setFillColor(TEXT_MUTED)
    c.drawString(40, 22, "SANCHAI · ZERO-HALLUCINATION NEPALI CLINICAL HEALTH LEDGER")

    # Footer Right: Slide Number
    c.drawRightString(PAGE_WIDTH - 40, 22, f"Slide {current_slide} of {total_slides}")


def draw_header(c: canvas.Canvas, badge_text: str, title: str, subtitle: str):
    """Draws slide header with category badge, title, and subtitle."""
    x = 44
    y = PAGE_HEIGHT - 38

    # Category Pill Badge
    badge_w = len(badge_text) * 7.5 + 16
    c.setFillColor(BADGE_BG_ORANGE)
    c.roundRect(x, y - 4, badge_w, 20, 10, fill=True, stroke=False)
    c.setFont(FONT_BOLD, 8.5)
    c.setFillColor(ACCENT_ORANGE)
    c.drawString(x + 8, y + 2, badge_text.upper())

    # Title
    c.setFont(FONT_BOLD, 22)
    c.setFillColor(TEXT_PRIMARY)
    c.drawString(x, y - 32, title)

    # Subtitle
    c.setFont(FONT_NORMAL, 11)
    c.setFillColor(TEXT_SECONDARY)
    c.drawString(x, y - 48, subtitle)


def draw_card(c: canvas.Canvas, x: float, y: float, w: float, h: float, radius: float = 12):
    """Draws a clean white card with subtle border."""
    c.setFillColor(CARD_BG)
    c.setStrokeColor(BORDER_COLOR)
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, radius, fill=True, stroke=True)


# ==============================================================================
# SLIDE 1: Title & Vision
# ==============================================================================
def render_slide_1(c: canvas.Canvas):
    draw_background(c)

    # Decorative Central Card
    card_x, card_y, card_w, card_h = 44, 56, PAGE_WIDTH - 88, PAGE_HEIGHT - 96
    draw_card(c, card_x, card_y, card_w, card_h, radius=16)

    # Large Logo Emblem
    emblem_x, emblem_y, emblem_s = 76, card_y + card_h - 110, 64
    c.setFillColor(ACCENT_ORANGE)
    c.roundRect(emblem_x, emblem_y, emblem_s, emblem_s, 16, fill=True, stroke=False)
    c.setFont(FONT_DEVA_BOLD, 32)
    c.setFillColor(HexColor("#FFFFFF"))
    c.drawCentredString(emblem_x + emblem_s / 2, emblem_y + 14, "स")

    # Brand Title
    c.setFont(FONT_BOLD, 42)
    c.setFillColor(TEXT_PRIMARY)
    c.drawString(emblem_x + emblem_s + 20, emblem_y + 20, "Sanchai")
    
    # Clinical Badge
    c.setFillColor(BADGE_BG_ORANGE)
    c.roundRect(emblem_x + emblem_s + 195, emblem_y + 22, 175, 28, 14, fill=True, stroke=False)
    c.setFont(FONT_BOLD, 11)
    c.setFillColor(ACCENT_ORANGE)
    c.drawCentredString(emblem_x + emblem_s + 282, emblem_y + 31, "NEPALI CLINICAL LEDGER")

    # Tagline / Subtitle
    c.setFont(FONT_BOLD, 17)
    c.setFillColor(NAVY_HEADER)
    c.drawString(emblem_x, emblem_y - 36, "Zero-Hallucination Nepali Clinical Health Ledger & Offline-First AI")

    c.setFont(FONT_NORMAL, 12)
    c.setFillColor(TEXT_SECONDARY)
    c.drawString(emblem_x, emblem_y - 58, "Grounding Multimodal Health Records in Nepal's Real-World Clinical Ecosystem")

    # 4 Highlights Pills Row
    pills = [
        ("0% Hallucinations", "Verified 300-concept clinical ontology"),
        ("Dual-Tier Gemma 4", "Cloud (31B) + Edge Local Fallback (2B QAT)"),
        ("Human Approval Gate", "Clinician review before ledger commit"),
        ("Emergency Triage QR", "Sub-second offline paramedic card"),
    ]

    pill_y = card_y + 90
    pill_w = (card_w - 80 - 3 * 16) / 4
    for i, (title, desc) in enumerate(pills):
        px = card_x + 40 + i * (pill_w + 16)
        c.setFillColor(BG_COLOR)
        c.setStrokeColor(BORDER_COLOR)
        c.setLineWidth(1)
        c.roundRect(px, pill_y, pill_w, 95, 10, fill=True, stroke=True)

        c.setFillColor(ACCENT_ORANGE)
        c.rect(px + 12, pill_y + 68, 6, 6, fill=True, stroke=False)

        c.setFont(FONT_BOLD, 11)
        c.setFillColor(TEXT_PRIMARY)
        c.drawString(px + 24, pill_y + 66, title)

        c.setFont(FONT_NORMAL, 9)
        c.setFillColor(TEXT_SECONDARY)
        words = desc.split(" ")
        line1 = " ".join(words[:3])
        line2 = " ".join(words[3:])
        c.drawString(px + 12, pill_y + 44, line1)
        c.drawString(px + 12, pill_y + 28, line2)

    # Footer note on card
    c.setFont(FONT_BOLD, 10)
    c.setFillColor(EMERALD_OK)
    c.drawString(card_x + 40, card_y + 36, "● PITCH DECK: 3-MINUTE PRESENTATION + 2-MINUTE LIVE DEMONSTRATION")

    c.setFont(FONT_NORMAL, 10)
    c.setFillColor(TEXT_MUTED)
    c.drawRightString(card_x + card_w - 40, card_y + 36, "Powered by Google Gemma 4")

    draw_footer(c, 1)


# ==============================================================================
# SLIDE 2: Problem Statement
# ==============================================================================
def render_slide_2(c: canvas.Canvas):
    draw_background(c)
    draw_header(c, "The Problem in Nepal", "Four Fatal Flaws in Nepal's Healthcare Flow", 
                "Why generic digital health apps and unconstrained chatbots fail in real-world clinical practice")

    cards = [
        ("The 'Plastic Bag' Records", 
         "Faded thermal receipts, handwritten cursive scripts, and fragmented paper slips scattered across clinics. When patients visit a new hospital, past medical history is completely lost.",
         "CRITICAL RISK", CRIMSON_DANGER, BADGE_BG_RED),
        ("The Brand vs. Generic Trap", 
         "Pharmacies dispense commercial brands. A patient taking Cetamol in Kathmandu is prescribed Paracetamol in Pokhara, causing accidental double dosing and acute liver toxicity.",
         "FATAL RISK", CRIMSON_DANGER, BADGE_BG_RED),
        ("Trilingual & Code-Mixed Notes", 
         "Real notes mix Devanagari, Romanized phonetics ('chhati polyo', 'jwaro chhaina'), and medical shorthand. Generic English LLMs miss cultural idioms and misdiagnose symptoms.",
         "HIGH COMPLEXITY", ACCENT_ORANGE, BADGE_BG_ORANGE),
        ("The Mountain Connectivity Barrier", 
         "Landslides, floods, and power outages regularly cut fiber lines to rural health posts (Swasthya Chauki). Cloud-only health apps become completely useless when offline.",
         "TERRAIN BARRIER", ACCENT_ORANGE, BADGE_BG_ORANGE),
    ]

    start_x = 44
    start_y = 60
    card_w = (PAGE_WIDTH - 88 - 18) / 2
    card_h = 168

    coords = [
        (start_x, start_y + card_h + 16),
        (start_x + card_w + 18, start_y + card_h + 16),
        (start_x, start_y),
        (start_x + card_w + 18, start_y),
    ]

    for (title, desc, badge, badge_color, badge_bg), (cx, cy) in zip(cards, coords):
        draw_card(c, cx, cy, card_w, card_h)

        # Badge pill
        c.setFillColor(badge_bg)
        c.roundRect(cx + 20, cy + card_h - 32, 100, 18, 9, fill=True, stroke=False)
        c.setFont(FONT_BOLD, 7.5)
        c.setFillColor(badge_color)
        c.drawCentredString(cx + 70, cy + card_h - 26, badge)

        # Title
        c.setFont(FONT_BOLD, 14)
        c.setFillColor(TEXT_PRIMARY)
        c.drawString(cx + 20, cy + card_h - 56, title)

        # Description wrapped lines
        c.setFont(FONT_NORMAL, 10)
        c.setFillColor(TEXT_SECONDARY)
        
        words = desc.split(" ")
        lines = []
        cur = []
        for w in words:
            if len(" ".join(cur + [w])) < 52:
                cur.append(w)
            else:
                lines.append(" ".join(cur))
                cur = [w]
        if cur:
            lines.append(" ".join(cur))

        line_y = cy + card_h - 80
        for line in lines[:4]:
            c.drawString(cx + 20, line_y, line)
            line_y -= 16

    draw_footer(c, 2)


# ==============================================================================
# SLIDE 3: Architecture & Solution
# ==============================================================================
def render_slide_3(c: canvas.Canvas):
    draw_background(c)
    draw_header(c, "Our Architecture", "The Sanchai Zero-Hallucination Pipeline", 
                "Deterministic clinical scaffolding binding Gemma 4 to verified ontology ground truth")

    # Left Column: The 3 Tiers (Width 520)
    lx, ly, lw, lh = 44, 58, 510, 360
    draw_card(c, lx, ly, lw, lh)

    c.setFont(FONT_BOLD, 14)
    c.setFillColor(NAVY_HEADER)
    c.drawString(lx + 24, ly + lh - 32, "Deterministic 3-Tier Clinical Normalization Engine")

    tiers = [
        ("Tier 1: Sub-Millisecond Exact Match", "0 ms",
         "O(1) hash table lookup across 300 concepts. Matches Devanagari, English, Romanized aliases, and DDA commercial brands directly. Zero hallucinations possible."),
        ("Tier 2: Orthographic & Matra Fuzzy Match", "< 2 ms",
         "RapidFuzz bounded Levenshtein distance. Recovers OCR-corrupted vowel signs ('jwarou' -> 'jwaro') without semantic drift or concept confusion."),
        ("Tier 3: Gemma 4 Constrained Guardrail", "AI Guard",
         "When ambiguous phrasing is encountered, Gemma 4 is presented with allowed candidates. It must choose an existing ID or output UNKNOWN. Negative rejection enforced."),
    ]

    ty = ly + lh - 70
    for title, speed_tag, desc in tiers:
        c.setFillColor(BG_COLOR)
        c.setStrokeColor(BORDER_COLOR)
        c.roundRect(lx + 20, ty - 65, lw - 40, 78, 8, fill=True, stroke=True)

        c.setFont(FONT_BOLD, 11)
        c.setFillColor(TEXT_PRIMARY)
        c.drawString(lx + 32, ty - 8, title)

        # Speed tag
        c.setFillColor(BADGE_BG_GREEN if "ms" in speed_tag else BADGE_BG_ORANGE)
        c.roundRect(lx + lw - 105, ty - 12, 55, 16, 8, fill=True, stroke=False)
        c.setFont(FONT_BOLD, 7.5)
        c.setFillColor(EMERALD_OK if "ms" in speed_tag else ACCENT_ORANGE)
        c.drawCentredString(lx + lw - 77, ty - 7, speed_tag)

        # Description
        c.setFont(FONT_NORMAL, 9)
        c.setFillColor(TEXT_SECONDARY)
        words = desc.split(" ")
        l1, l2 = " ".join(words[:11]), " ".join(words[11:22])
        l3 = " ".join(words[22:])
        c.drawString(lx + 32, ty - 26, l1)
        c.drawString(lx + 32, ty - 39, l2)
        if l3:
            c.drawString(lx + 32, ty - 52, l3)

        ty -= 92

    # Right Column: Clinical Pillars (Width 330)
    rx = lx + lw + 18
    rw = PAGE_WIDTH - rx - 44
    draw_card(c, rx, ly, rw, lh)

    c.setFont(FONT_BOLD, 14)
    c.setFillColor(NAVY_HEADER)
    c.drawString(rx + 20, ly + lh - 32, "Four Safety Guardrails")

    pillars = [
        ("300 Verified Concepts", "Sourced directly from Nepal DDA, NLEM 2021, and WHO ICD-11."),
        ("Directional Negation", "'jwaro chhaina' (no fever) is captured with 100% accuracy and excluded."),
        ("Brand -> Generic Resolution", "Taxim-O -> Cefixime; prevents dangerous duplicate therapies."),
        ("Approval-Before-Write Gate", "Human clinician reviews and commits before saving to record."),
    ]

    py = ly + lh - 70
    for p_title, p_desc in pillars:
        c.setFillColor(EMERALD_OK)
        c.circle(rx + 28, py - 4, 4, fill=True, stroke=False)

        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(TEXT_PRIMARY)
        c.drawString(rx + 42, py - 6, p_title)

        c.setFont(FONT_NORMAL, 8.5)
        c.setFillColor(TEXT_SECONDARY)
        c.drawString(rx + 42, py - 22, p_desc)

        py -= 65

    draw_footer(c, 3)


# ==============================================================================
# SLIDE 4: Empirical Evaluation (NepClinBench)
# ==============================================================================
def render_slide_4(c: canvas.Canvas):
    draw_background(c)
    draw_header(c, "Empirical Validation", "NepClinBench Live Evaluation & Ablation", 
                "Rigorous benchmark on 60 real bilingual clinical test cases comparing Sanchai vs. Raw Gemma 4")

    # Table Card
    tx, ty, tw, th = 44, 58, PAGE_WIDTH - 88, 360
    draw_card(c, tx, ty, tw, th)

    # Header Row
    headers = [
        ("Evaluation Metric", 280),
        ("Sanchai 3-Tier Pipeline", 180),
        ("Raw Gemma 4 Baseline", 180),
        ("Sanchai Advantage", 170)
    ]

    row_y = ty + th - 44
    c.setFillColor(BG_COLOR)
    c.roundRect(tx + 16, row_y - 6, tw - 32, 34, 8, fill=True, stroke=False)

    cur_x = tx + 32
    for h_title, h_width in headers:
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(NAVY_HEADER)
        c.drawString(cur_x, row_y + 8, h_title.upper())
        cur_x += h_width

    # Table Rows
    data_rows = [
        ("Exact Set Match (N=60 Gold Cases)", "96.7% (58 / 60)", "46.7% (28 / 60)", "+50.0% GAIN", True),
        ("Precision (Zero Hallucination Guarantee)", "1.000 (0% Hallucination)", "0.817 (18.3% Hallucinated)", "+22.4 PTS", True),
        ("Brand to Generic Resolution (DDA)", "100.0% (54 / 54)", "41.7% (23 / 54)", "+58.3% GAIN", True),
        ("Directional Negation Accuracy (Pertinent Negatives)", "100.0% (10 / 10)", "50.0% (5 / 10)", "+50.0% GAIN", True),
        ("Duration & Dosage Parsing", "100.0% (12 / 12)", "66.7% (8 / 12)", "+33.3% GAIN", False),
        ("FHIR R4 Bundle Validity", "100% (Strict Valid JSON)", "0% (Unstructured English)", "100% INTEROPERABLE", True),
        ("Deterministic Edge Latency", "Yes (< 5 ms offline)", "No (> 800 ms cloud API)", "160x FASTER", True),
    ]

    row_y -= 40
    for metric, sanchai_val, raw_val, advantage, is_highlight in data_rows:
        cur_x = tx + 32

        # Metric Name
        c.setFont(FONT_BOLD if is_highlight else FONT_NORMAL, 10)
        c.setFillColor(TEXT_PRIMARY)
        c.drawString(cur_x, row_y + 4, metric)
        cur_x += 280

        # Sanchai Value
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(EMERALD_OK)
        c.drawString(cur_x, row_y + 4, sanchai_val)
        cur_x += 180

        # Raw Gemma 4 Value
        c.setFont(FONT_NORMAL, 10)
        c.setFillColor(CRIMSON_DANGER if "Hallucinated" in raw_val else TEXT_MUTED)
        c.drawString(cur_x, row_y + 4, raw_val)
        cur_x += 180

        # Advantage Badge
        c.setFillColor(BADGE_BG_GREEN)
        c.roundRect(cur_x - 4, row_y - 2, 120, 18, 9, fill=True, stroke=False)
        c.setFont(FONT_BOLD, 8.5)
        c.setFillColor(EMERALD_OK)
        c.drawCentredString(cur_x + 56, row_y + 3, advantage)

        # Light divider
        c.setStrokeColor(BORDER_COLOR)
        c.setLineWidth(0.5)
        c.line(tx + 24, row_y - 8, tx + tw - 24, row_y - 8)

        row_y -= 36

    draw_footer(c, 4)


# ==============================================================================
# SLIDE 5: SanchAI Assistant & Emergency Ecosystem
# ==============================================================================
def render_slide_5(c: canvas.Canvas):
    draw_background(c)
    draw_header(c, "The Clinical Ecosystem", "End-to-End Continuity: SanchAI & Emergency QR", 
                "Empowering patients at home, assisting doctors in OPD, and saving lives in ambulances")

    # 3 Column Cards
    col_w = (PAGE_WIDTH - 88 - 32) / 3
    col_h = 360
    y = 58

    cols = [
        ("SanchAI Copilot", "EHR Grounded Assistant", [
            ("Patient Context Aware", "Knows active conditions, allergies, and ongoing medications completely."),
            ("Multimodal Ingestion", "Uploads prescription photos and lab PDFs for instant interpretation."),
            ("Plain Nepali Explanations", "Translates CBC, Widal, and lipid panel jargon into everyday Nepali."),
            ("Pre-Visit Doctor Briefing", "One-click synthesis preparing complaints and questions for doctors."),
        ], ACCENT_ORANGE),
        ("Critical Safety Guardrails", "Allergy Risk Defense", [
            ("Allergy Cross-Referencing", "Checks user query against documented patient allergies automatically."),
            ("Beta-Lactam Protection", "Flags Amoxicillin/Augmentin if patient has documented Penicillin allergy."),
            ("Zero Autonomous Writes", "Cannot mutate authoritative health ledger without clinician approval."),
            ("Doctor Summary A4 PDF", "One-click print-ready clinical report with embedded QR code verification."),
        ], CRIMSON_DANGER),
        ("Emergency Optical QR", "Ambulance Triage in < 1s", [
            ("High-Contrast Segno QR", "Encodes deterministic token readable by any phone camera or optical scanner."),
            ("Offline Paramedic View", "Instant triage strip: Blood group, severe allergies, chronic diagnoses."),
            ("Unconscious Patient Care", "Paramedics make life-saving decisions before reaching hospital doors."),
            ("HL7 FHIR R4 Export", "Standardized interoperability for hospital EHRs (Bahmni, Epic, Cerner)."),
        ], EMERALD_OK),
    ]

    for i, (title, sub, items, color) in enumerate(cols):
        cx = 44 + i * (col_w + 16)
        draw_card(c, cx, y, col_w, col_h)

        # Top Card Accent
        c.setFillColor(color)
        c.roundRect(cx + 20, y + col_h - 18, col_w - 40, 4, 2, fill=True, stroke=False)

        c.setFont(FONT_BOLD, 14)
        c.setFillColor(TEXT_PRIMARY)
        c.drawString(cx + 20, y + col_h - 42, title)

        c.setFont(FONT_BOLD, 8.5)
        c.setFillColor(color)
        c.drawString(cx + 20, y + col_h - 58, sub.upper())

        item_y = y + col_h - 90
        for it_title, it_desc in items:
            c.setFillColor(color)
            c.circle(cx + 26, item_y - 2, 3.5, fill=True, stroke=False)

            c.setFont(FONT_BOLD, 10)
            c.setFillColor(TEXT_PRIMARY)
            c.drawString(cx + 36, item_y - 4, it_title)

            c.setFont(FONT_NORMAL, 8.5)
            c.setFillColor(TEXT_SECONDARY)
            words = it_desc.split(" ")
            l1 = " ".join(words[:6])
            l2 = " ".join(words[6:])
            c.drawString(cx + 36, item_y - 18, l1)
            if l2:
                c.drawString(cx + 36, item_y - 30, l2)

            item_y -= 62

    draw_footer(c, 5)


# ==============================================================================
# SLIDE 6: Offline-First Resilience
# ==============================================================================
def render_slide_6(c: canvas.Canvas):
    draw_background(c)
    draw_header(c, "The Pitch: Offline-First", "Why Offline Architecture is Life or Death in Nepal", 
                "A digital health system in Nepal that fails when the internet cuts out is a health system that fails when needed most")

    # Callout Quote Banner
    qx, qy, qw, qh = 44, 344, PAGE_WIDTH - 88, 70
    draw_card(c, qx, qy, qw, qh)
    c.setFillColor(BADGE_BG_ORANGE)
    c.roundRect(qx + 4, qy + 4, qw - 8, qh - 8, 8, fill=True, stroke=False)

    c.setFont(FONT_BOLD, 12)
    c.setFillColor(ACCENT_ORANGE)
    c.drawCentredString(qx + qw / 2, qy + 42, '"A digital health system in Nepal that fails when the internet cuts out')
    c.drawCentredString(qx + qw / 2, qy + 22, 'is a health system that fails when it is needed most."')

    # The 3-Layer Resilience Ladder
    steps = [
        ("LAYER 1", "Deterministic Rule Core", "< 5 ms Latency",
         "100% Offline & Local",
         "Exact dictionary matching and fuzzy matra parsing run locally with zero network requirement. Instant clinical lookup even on battery power.",
         EMERALD_OK, BADGE_BG_GREEN),
        ("LAYER 2", "Cloud Acceleration", "High Nuance",
         "Online Gemma 4 (31B)",
         "When connected to internet, routes to gemma4:31b-cloud for complex prescription handwriting OCR, deep reasoning, and doctor summaries.",
         ACCENT_ORANGE, BADGE_BG_ORANGE),
        ("LAYER 3", "Automatic Edge Fallback", "Zero Downtime",
         "Offline Gemma 4 (2B QAT)",
         "If fiber line cuts or mobile data drops, Sanchai seamlessly switches to locally installed gemma4:e2b-it-qat running on the local device.",
         NAVY_HEADER, HexColor("#F1F5F9")),
    ]

    step_w = (PAGE_WIDTH - 88 - 32) / 3
    step_h = 240
    sy = 64

    for i, (badge, title, tag, model_sub, desc, color, badge_bg) in enumerate(steps):
        sx = 44 + i * (step_w + 16)
        draw_card(c, sx, sy, step_w, step_h)

        # Layer Badge
        c.setFillColor(badge_bg)
        c.roundRect(sx + 20, sy + step_h - 30, 75, 18, 9, fill=True, stroke=False)
        c.setFont(FONT_BOLD, 8)
        c.setFillColor(color)
        c.drawCentredString(sx + 57, sy + step_h - 24, badge)

        # Speed tag
        c.setFont(FONT_BOLD, 8)
        c.setFillColor(TEXT_MUTED)
        c.drawRightString(sx + step_w - 20, sy + step_h - 24, tag)

        # Title
        c.setFont(FONT_BOLD, 13)
        c.setFillColor(TEXT_PRIMARY)
        c.drawString(sx + 20, sy + step_h - 56, title)

        # Subtitle
        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(color)
        c.drawString(sx + 20, sy + step_h - 74, model_sub)

        # Divider
        c.setStrokeColor(BORDER_COLOR)
        c.setLineWidth(0.5)
        c.line(sx + 20, sy + step_h - 86, sx + step_w - 20, sy + step_h - 86)

        # Description
        c.setFont(FONT_NORMAL, 9.5)
        c.setFillColor(TEXT_SECONDARY)
        words = desc.split(" ")
        lines = []
        cur = []
        for w in words:
            if len(" ".join(cur + [w])) < 34:
                cur.append(w)
            else:
                lines.append(" ".join(cur))
                cur = [w]
        if cur:
            lines.append(" ".join(cur))

        ly = sy + step_h - 108
        for line in lines[:6]:
            c.drawString(sx + 20, ly, line)
            ly -= 17

    draw_footer(c, 6)


# ==============================================================================
# SLIDE 7: Business Model, Roadmap & Conclusion
# ==============================================================================
def render_slide_7(c: canvas.Canvas):
    draw_background(c)
    draw_header(c, "Vision & Roadmap", "Sustainable Healthcare Infrastructure for Nepal", 
                "Transforming fragmented plastic bag records into permanent health agency for every citizen")

    # Left Column: Business & Deployment Model (Width 440)
    lx, ly, lw, lh = 44, 58, 430, 360
    draw_card(c, lx, ly, lw, lh)

    c.setFont(FONT_BOLD, 15)
    c.setFillColor(NAVY_HEADER)
    c.drawString(lx + 24, ly + lh - 32, "Sustainable B2B2C Healthcare Model")

    b_items = [
        ("Hospital & Clinic OPD SaaS", 
         "Hospitals pay a modest monthly license for the ingestion studio, automated FHIR conversion, and doctor summary generation, eliminating costly manual re-entry.", ACCENT_ORANGE),
        ("National Health Insurance Board", 
         "Partnering with Swasthya Bima Board (Health Insurance Board) to detect duplicate drug dispensing and stop fraudulent claims across districts.", EMERALD_OK),
        ("Free Personal Ledger for Citizens", 
         "Personal records, emergency QR cards, and SanchAI assistance remain completely free for citizens to ensure equitable access.", NAVY_HEADER),
    ]

    by = ly + lh - 70
    for b_title, b_desc, b_color in b_items:
        c.setFillColor(b_color)
        c.roundRect(lx + 24, by - 6, 8, 8, 2, fill=True, stroke=False)

        c.setFont(FONT_BOLD, 11)
        c.setFillColor(TEXT_PRIMARY)
        c.drawString(lx + 40, by - 6, b_title)

        c.setFont(FONT_NORMAL, 9)
        c.setFillColor(TEXT_SECONDARY)
        words = b_desc.split(" ")
        lines = []
        cur = []
        for w in words:
            if len(" ".join(cur + [w])) < 46:
                cur.append(w)
            else:
                lines.append(" ".join(cur))
                cur = [w]
        if cur:
            lines.append(" ".join(cur))

        dy = by - 24
        for l in lines[:3]:
            c.drawString(lx + 40, dy, l)
            dy -= 14

        by -= 94

    # Right Column: Roadmap & The Core Message (Width 430)
    rx = lx + lw + 16
    rw = PAGE_WIDTH - rx - 44
    draw_card(c, rx, ly, rw, lh)

    c.setFont(FONT_BOLD, 15)
    c.setFillColor(NAVY_HEADER)
    c.drawString(rx + 24, ly + lh - 32, "Roadmap & Future Scope")

    r_items = [
        ("Lexicon Scale", "Expanding from 300 to 1,500+ DDA concepts covering tertiary oncology and pediatrics."),
        ("Ministry of Health Integration", "Direct API integration with national DHIS2 and digital health ID."),
        ("Pharmacy Barcode Scanners", "Equipping community pharmacies to verify prescriptions before dispensing."),
    ]

    ry = ly + lh - 70
    for r_title, r_desc in r_items:
        c.setFillColor(EMERALD_OK)
        c.circle(rx + 30, ry - 3, 3.5, fill=True, stroke=False)

        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(TEXT_PRIMARY)
        c.drawString(rx + 42, ry - 5, r_title)

        c.setFont(FONT_NORMAL, 8.5)
        c.setFillColor(TEXT_SECONDARY)
        words = r_desc.split(" ")
        c.drawString(rx + 42, ry - 20, " ".join(words[:8]))
        if len(words) > 8:
            c.drawString(rx + 42, ry - 32, " ".join(words[8:]))

        ry -= 56

    # Bottom Callout in Right Card
    call_y = ly + 20
    c.setFillColor(BADGE_BG_ORANGE)
    c.roundRect(rx + 20, call_y, rw - 40, 78, 8, fill=True, stroke=False)

    c.setFont(FONT_BOLD, 16)
    c.setFillColor(ACCENT_ORANGE)
    c.drawCentredString(rx + rw / 2, call_y + 46, "Sanchai Hunuhunchha?")

    c.setFont(FONT_BOLD, 10.5)
    c.setFillColor(TEXT_PRIMARY)
    c.drawCentredString(rx + rw / 2, call_y + 26, "Turning plastic bags into longitudinal health agency.")

    c.setFont(FONT_NORMAL, 9)
    c.setFillColor(TEXT_SECONDARY)
    c.drawCentredString(rx + rw / 2, call_y + 12, "Thank you! Live Demo starting now.")

    draw_footer(c, 7)


def build_pdf(filename: str = "SANCHAI_PITCH_SLIDES.pdf"):
    """Compiles all 7 presentation slides into a landscape 16:9 PDF."""
    c = canvas.Canvas(filename, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    slides = [
        render_slide_1,
        render_slide_2,
        render_slide_3,
        render_slide_4,
        render_slide_5,
        render_slide_6,
        render_slide_7,
    ]

    for i, slide_fn in enumerate(slides):
        slide_fn(c)
        c.showPage()

    c.save()
    print(f"Successfully generated {filename} ({len(slides)} slides, 16:9 widescreen).")


if __name__ == "__main__":
    build_pdf()
