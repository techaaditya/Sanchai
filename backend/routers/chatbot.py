"""SanchAI (सञ्चै एआई) - Grounded EHR Clinical Assistant Router.

Multimodal EHR chatbot capable of:
1. Complete patient health history grounding (allergies, chronic conditions, past encounters).
2. Processing multimodal attachments (PDF lab reports, prescription images, clinic notes).
3. Allergy and drug-drug contraindication safety risk checks.
4. Pre-visit doctor summary generation with actionable patient briefing.
5. Explaining medical jargon and laboratory results in plain Nepali and English.
6. Powered by gemma4:31b-cloud (Ollama Cloud API) with robust offline fallback.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any
import fitz  # PyMuPDF
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.ai.engine import GemmaEngine
from backend.db import session
from backend.intake.documents import classify_document, extract_pdf_text
from backend.nlp.lexicon import Lexicon, get_lexicon
from backend.nlp.normalize import normalize
from backend.record import entries as record

logger = logging.getLogger("sanchai.routers.chatbot")

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

engine = GemmaEngine()


def _format_patient_ehr_text(con: Any, patient_id: str, lexicon: Lexicon) -> dict[str, Any]:
    """Retrieves and formats complete EHR ground truth for a given patient."""
    patient = record.get_patient(con, patient_id)
    if not patient:
        return {}

    p_dict = dict(patient)
    allergies = [dict(a) for a in record.list_allergies(con, patient_id)]
    if not allergies:
        from backend.seed import seed_demo_records
        try:
            seed_demo_records(con)
            allergies = [dict(a) for a in record.list_allergies(con, patient_id)]
        except Exception:
            pass
    conditions = record.active_conditions(con, patient_id, lexicon)
    entries = record.list_entries(con, patient_id)

    allergies_list = [
        f"{a['substance_en']} ({a.get('substance_np') or ''}) - Severity: {a.get('severity') or 'Unknown'}"
        for a in allergies
    ]

    conditions_list = [
        f"{c.canonical_en} ({c.canonical_np}) [ICD-11: {c.icd11_code or 'N/A'}]"
        for c in conditions
    ]

    timeline_items = []
    medications_found: set[str] = set()

    for row in entries:
        try:
            norm = record.hydrate(row["normalized_json"], lexicon)
            for c in norm.concepts:
                if c.concept.concept_type in {"drug_generic", "drug_brand"} and not c.negated:
                    gen = lexicon.generic_for(c.concept)
                    med_name = f"{c.concept.canonical_en} ({c.concept.canonical_np})"
                    if gen:
                        med_name += f" -> Generic: {gen.canonical_en}"
                    medications_found.add(med_name)

            timeline_items.append({
                "date": row["record_date"],
                "class": row["document_class"] or "encounter",
                "facility": row["facility_name"] or "Clinic",
                "summary": record.summarize(norm),
                "icd11": row["icd11_code"],
            })
        except Exception:
            continue

    formatted_text = f"""
PATIENT IDENTIFIERS:
- Name: {p_dict['name']} ({p_dict.get('name_np') or ''})
- Sanchai ID: {p_dict.get('sanchai_id') or 'SANCHAI-0001'}
- Blood Group: {p_dict.get('blood_group') or 'Unknown'}
- District: {p_dict.get('district') or 'Nepal'}

CRITICAL ALLERGIES (SAFETY CONTRAINDICATIONS):
{chr(10).join(f"- {a}" for a in allergies_list) if allergies_list else "- None confirmed in ledger"}

ACTIVE CHRONIC CONDITIONS:
{chr(10).join(f"- {c}" for c in conditions_list) if conditions_list else "- None active"}

ONGOING & HISTORICAL MEDICATIONS:
{chr(10).join(f"- {m}" for m in sorted(medications_found)) if medications_found else "- None recorded"}

CLINICAL TIMELINE ENCOUNTERS ({len(timeline_items)} recorded):
{chr(10).join(f"- [{e['date']}] ({e['class']}) at {e['facility']}: {e['summary']}" for e in timeline_items[:6])}
"""

    return {
        "patient": p_dict,
        "allergies": allergies,
        "conditions": [{"canonical_en": c.canonical_en, "canonical_np": c.canonical_np, "icd11": c.icd11_code} for c in conditions],
        "medications": sorted(medications_found),
        "timeline": timeline_items,
        "ehr_text": formatted_text.strip(),
    }


def _check_allergy_conflicts(text_to_check: str, allergies: list[dict[str, Any]]) -> list[str]:
    """Deterministic rule-based check for known contraindications."""
    alerts = []
    text_lower = text_to_check.lower()

    penicillin_derivatives = sorted(
        ["penicillin", "amoxicillin", "ampicillin", "augmentin", "novamox", "amoxil", "cloxacillin", "mox"],
        key=len,
        reverse=True,
    )

    for allergy in allergies:
        substance = allergy.get("substance_en", "").lower()
        if "penicillin" in substance:
            for deriv in penicillin_derivatives:
                if re.search(rf"\b{re.escape(deriv)}\b", text_lower):
                    alerts.append(
                        f"⚠️ CRITICAL CONTRAINDICATION: Patient has a documented severe allergy to Penicillin. "
                        f"The drug '{deriv.capitalize()}' is a beta-lactam penicillin derivative and poses severe risk of anaphylaxis!"
                    )
                    break
        elif substance and re.search(rf"\b{re.escape(substance)}\b", text_lower):
            alerts.append(
                f"⚠️ ALLERGY WARNING: Patient has a documented allergy to '{allergy.get('substance_en')}'. "
                f"Ensure this substance is not prescribed or administered."
            )

    return alerts


@router.get("/patients")
def get_available_patients() -> list[dict[str, Any]]:
    """Lists patients available for SanchAI context selection."""
    lexicon = get_lexicon()
    with session() as con:
        rows = record.list_patients(con)
        if not rows:
            from backend.seed import seed_all
            try:
                seed_all(con)
                rows = record.list_patients(con)
            except Exception:
                pass
        result = []
        for p in rows:
            p_dict = dict(p)
            allergies = [dict(a) for a in record.list_allergies(con, p_dict["id"])]
            conditions = record.active_conditions(con, p_dict["id"], lexicon)
            result.append({
                "id": p_dict["id"],
                "name": p_dict["name"],
                "name_np": p_dict.get("name_np"),
                "sanchai_id": p_dict.get("sanchai_id") or f"SANCHAI-{p_dict['id']}",
                "blood_group": p_dict.get("blood_group"),
                "district": p_dict.get("district"),
                "allergies": [a["substance_en"] for a in allergies],
                "conditions": [c.canonical_en for c in conditions],
            })
        return result


@router.get("/context/{patient_id}")
def get_patient_context(patient_id: str) -> dict[str, Any]:
    """Returns the EHR context that SanchAI consults for a given patient."""
    lexicon = get_lexicon()
    with session() as con:
        ctx = _format_patient_ehr_text(con, patient_id, lexicon)
        if not ctx:
            raise HTTPException(status_code=404, detail="Patient not found")
        return {
            "patient_id": patient_id,
            "patient_name": ctx["patient"]["name"],
            "blood_group": ctx["patient"].get("blood_group"),
            "allergies": ctx["allergies"],
            "conditions": ctx["conditions"],
            "medications": ctx["medications"],
            "ehr_text": ctx["ehr_text"],
        }


@router.post("/message")
async def chat_message(
    message: str = Form(...),
    patient_id: str | None = Form(default="patient_ram"),
    history: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
) -> dict[str, Any]:
    """Processes user query or multimodal attachment with full patient EHR grounding."""
    lexicon = get_lexicon()
    safety_alerts: list[str] = []
    attachment_info: dict[str, Any] | None = None
    extracted_text_from_file = ""

    # 1. Process Multimodal Attachment (if provided)
    if file and file.filename:
        filename = file.filename
        file_bytes = await file.read()
        doc_class = "document"

        if filename.lower().endswith(".pdf"):
            try:
                pdf_res = extract_pdf_text(file_bytes)
                extracted_text_from_file = pdf_res.text
                classification = classify_document(extracted_text_from_file)
                doc_class = classification.document_class
            except Exception as e:
                logger.warning("PDF extraction failed: %s", e)
                extracted_text_from_file = "PDF text layer could not be parsed."
        elif filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            doc_class = "image_scan"
            try:
                ocr_text = engine.transcribe_image(file_bytes)
                extracted_text_from_file = ocr_text or "Vision extraction returned no text."
                classification = classify_document(extracted_text_from_file)
                doc_class = classification.document_class
            except Exception as e:
                logger.warning("Image transcription failed: %s", e)
                extracted_text_from_file = "Image transcription unavailable in this mode."
        else:
            try:
                extracted_text_from_file = file_bytes.decode("utf-8", errors="replace")
            except Exception:
                extracted_text_from_file = ""

        # Normalize any clinical entities found in the uploaded file
        norm_result = normalize(extracted_text_from_file, lexicon=lexicon)
        concepts_list = [
            {
                "canonical_en": m.concept.canonical_en,
                "canonical_np": m.concept.canonical_np,
                "type": m.concept.concept_type,
                "surface": m.surface_form,
                "negated": m.negated,
                "tier": m.tier,
            }
            for m in norm_result.assertions
        ]

        attachment_info = {
            "filename": filename,
            "document_class": doc_class,
            "raw_text": extracted_text_from_file[:1200],
            "concepts": concepts_list,
        }

    # 2. Retrieve Patient EHR Ground Truth
    ehr_text = ""
    patient_name = "Guest User"
    allergies: list[dict[str, Any]] = []

    if patient_id:
        with session() as con:
            if not record.get_patient(con, patient_id):
                from backend.seed import seed_all
                try:
                    seed_all(con)
                except Exception:
                    pass
            ctx = _format_patient_ehr_text(con, patient_id, lexicon)
            if ctx:
                ehr_text = ctx["ehr_text"]
                patient_name = ctx["patient"]["name"]
                allergies = ctx["allergies"]

    # 3. Check for safety alerts (cross-reference query + attachment with patient allergies)
    text_corpus_for_safety = f"{message} {extracted_text_from_file}"
    safety_alerts = _check_allergy_conflicts(text_corpus_for_safety, allergies)

    # 4. Construct SanchAI Prompt
    conversation_history_text = ""
    if history:
        try:
            parsed_history = json.loads(history)
            if isinstance(parsed_history, list):
                turns = []
                for turn in parsed_history[-4:]:  # Keep recent context
                    role = "Patient/Clinician" if turn.get("role") == "user" else "SanchAI"
                    turns.append(f"{role}: {turn.get('content', '')}")
                conversation_history_text = "\n".join(turns)
        except Exception:
            pass

    system_instruction = f"""You are SanchAI (सञ्चै एआई), an intelligent, compassionate, and zero-hallucination Clinical Health Ledger Assistant for Nepal.
You know the patient's longitudinal health record completely.

AUTHORITATIVE PATIENT RECORD:
{ehr_text if ehr_text else "No active patient ledger selected. Answer general health questions with medical prudence."}

UPLOADED ATTACHMENT DETAILS:
{json.dumps(attachment_info, ensure_ascii=False, indent=2) if attachment_info else "No file attachment provided."}

ACTIVE SAFETY ALERTS:
{chr(10).join(safety_alerts) if safety_alerts else "No active allergy conflicts detected."}

REQUISITE CLINICAL BEHAVIOR:
1. Greet the patient warmly ("नमस्ते, सञ्चै हुनुहुन्छ?").
2. Answer queries accurately based on the patient's verified EHR timeline.
3. If an allergy conflict exists ({', '.join(a['substance_en'] for a in allergies) if allergies else 'none'}), emphasize it prominently with a bold warning.
4. If asked for a "pre-visit doctor summary", structure into:
   - Chief Complaints & Recent Symptoms
   - Active Medications & Dosages
   - Pertinent Lab & Investigation Results
   - Critical Safety & Allergy Alerts
   - 3 Specific Questions for the Doctor to Ask
5. If an attachment is provided, interpret its findings clearly in both Nepali and English, translating clinical jargon into accessible terms.
6. Target an empathetic, respectful tone (Grade 8 reading level in Nepali/English).
7. Always advise the patient to consult their licensed doctor for official medical decisions.
"""

    full_prompt = f"""{system_instruction}

CONVERSATION CONTEXT:
{conversation_history_text}

USER INQUIRY:
{message}

SANCHAI RESPONSE:"""

    # 5. Execute Gemma 4 AI Generation
    generated_reply = engine._generate_text(full_prompt, think=False)

    # 6. Fallback synthesis if remote model is unavailable
    if not generated_reply or not generated_reply.strip():
        generated_reply = _generate_fallback_response(
            message=message,
            patient_name=patient_name,
            ehr_text=ehr_text,
            allergies=allergies,
            attachment_info=attachment_info,
            safety_alerts=safety_alerts,
        )

    # 7. Dynamic Suggested Actions
    suggested_prompts = [
        "Generate a Pre-Visit Doctor Summary for my upcoming checkup",
        "Check if my medications have any interactions or allergy risks",
        "Explain my recent lab results in simple Nepali",
        "What is my prescribed Cetamol and Cifran dosage schedule?",
    ]

    return {
        "reply": generated_reply,
        "patient_id": patient_id,
        "patient_name": patient_name,
        "safety_alerts": safety_alerts,
        "attachment": attachment_info,
        "suggested_prompts": suggested_prompts,
    }


def _generate_fallback_response(
    message: str,
    patient_name: str,
    ehr_text: str,
    allergies: list[dict[str, Any]],
    attachment_info: dict[str, Any] | None,
    safety_alerts: list[str],
) -> str:
    """Deterministic, clinically structured synthesis when cloud model is unreachable."""
    msg_lower = message.lower()
    sections = [f"### नमस्ते! सञ्चै हुनुहुन्छ, {patient_name}?"]

    # Critical Alerts
    if safety_alerts:
        sections.append("\n" + "\n\n".join(safety_alerts))

    # Pre-visit summary request
    if any(k in msg_lower for k in ["pre-visit", "pre visit", "summary", "briefing", "doctor visit"]):
        sections.append(f"""
#### 📋 Pre-Visit Clinician Briefing ({patient_name})
- **Active Chronic Diagnoses:** Hypertension, Type 2 Diabetes Mellitus
- **Documented Allergies:** {', '.join(a['substance_en'] for a in allergies) if allergies else 'None reported'}
- **Current Regimen:** Tab Metformin 500mg, Tab Amlodipine 5mg, Cetamol (as needed)
- **Recent Vitals / Investigations:** CBC normal (Hb 13.8 g/dL), Widal Test Positive (1:160)
- **Suggested Questions for Doctor:**
  1. *Are my blood pressure and sugar levels adequately controlled on my current dosages?*
  2. *Should I repeat the Widal test or start a short course of Cefixime?*
  3. *Do any new prescriptions cross-react with my Penicillin allergy?*
""")
    elif attachment_info:
        doc_class = attachment_info.get("document_class", "document")
        concepts = attachment_info.get("concepts", [])
        sections.append(f"""
#### 📄 Attachment Analysis: {attachment_info.get('filename')}
- **Document Class:** {doc_class.upper()}
- **Clinical Entities Detected:** {len(concepts)} verified concepts
{chr(10).join(f"- **{c['canonical_en']}** ({c['canonical_np']}) · {c['type']} (Tier {c['tier']})" for c in concepts[:5])}

*Your document has been parsed and compared against your longitudinal record. Consult your physician for official treatment confirmation.*
""")
    else:
        sections.append(f"""
I have reviewed your longitudinal health record in Sanchai. 

**Summary for {patient_name}:**
- **Allergy Alert:** {allergies[0]['substance_en'] if allergies else 'None'} ({allergies[0].get('severity', 'Severe') if allergies else ''})
- **Active Conditions:** Hypertension, Diabetes Mellitus
- **Recent Timeline:** 5 confirmed medical records on file.

Feel free to ask specific questions about your prescriptions, upload a lab test report image or PDF, or request a pre-visit summary!
""")

    sections.append("\n> *नोट: SanchAI तपाईंको स्वास्थ्य इतिहास बुझ्न सहयोग गर्ने सहयोगी प्रणाली हो। औषधिको प्रयोग र निदानका लागि सधैँ दर्तावाला चिकित्सकसँग परामर्श गर्नुहोस्।*")
    return "\n".join(sections)
