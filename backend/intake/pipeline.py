from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field

from backend.ai.engine import GemmaEngine
from backend.intake.documents import (
    CLASS_NOTE,
    Classification,
    classify_document,
    extract_pdf_text,
    render_pdf_page,
)
from backend.intake.storage import save_upload
from backend.nlp.correct import Correction, CorrectionResult, correct
from backend.nlp.lexicon import Lexicon, get_lexicon
from backend.nlp.normalize import NormalizationResult, normalize
from backend.schemas import (
    CorrectionOut,
    InlineNote,
    IntakeResponse,
    NormalizeResponse,
)

STATUS_OK = "ok"
STATUS_ENGINE_UNAVAILABLE = "engine_unavailable"
STATUS_EMPTY = "empty"
STATUS_UNSUPPORTED = "unsupported"

STAGE_ROUTING = "routing"
STAGE_EXTRACTING = "extracting"
STAGE_CORRECTING = "correcting"
STAGE_NORMALIZING = "normalizing"
STAGE_DONE = "done"

METHOD_DIRECT = "direct"
METHOD_PYMUPDF = "pymupdf"
METHOD_GEMMA4_VLM = "gemma4_vlm"
METHOD_UNAVAILABLE = "unavailable"

INPUT_TEXT = "text"
INPUT_IMAGE = "image"
INPUT_PDF = "pdf"


@dataclass(frozen=True, slots=True)
class Upload:
    data: bytes
    mime_type: str
    filename: str | None = None


@dataclass(frozen=True, slots=True)
class Note:
    level: str
    message_np: str
    message_en: str


@dataclass(slots=True)
class IntakeResult:
    raw_transcript: str
    corrected_text: str
    extraction_method: str
    extraction_status: str
    input_type: str
    document_class: str
    document_class_evidence: tuple[str, ...] = ()
    corrections: tuple[Correction, ...] = ()
    unverified: tuple[str, ...] = ()
    asset_path: str | None = None
    pages: int | None = None
    notes: list[Note] = field(default_factory=list)
    normalized: NormalizationResult | None = None

    def to_response(self, lexicon: Lexicon) -> IntakeResponse:
        norm_resp = (
            NormalizeResponse.from_result(self.normalized, lexicon)
            if self.normalized is not None
            else None
        )
        return IntakeResponse(
            raw_transcript=self.raw_transcript,
            corrected_text=self.corrected_text,
            extraction_method=self.extraction_method,
            extraction_status=self.extraction_status,
            input_type=self.input_type,
            document_class=self.document_class,
            document_class_evidence=list(self.document_class_evidence),
            corrections=[
                CorrectionOut(
                    original=c.original,
                    replacement=c.replacement,
                    start=c.start,
                    end=c.end,
                    reason=c.reason,
                    confidence=c.confidence,
                )
                for c in self.corrections
            ],
            unverified=list(self.unverified),
            asset_path=self.asset_path,
            pages=self.pages,
            notes=[
                InlineNote(
                    level=n.level,
                    message_np=n.message_np,
                    message_en=n.message_en,
                )
                for n in self.notes
            ],
            normalized=norm_resp,
        )


@dataclass(frozen=True, slots=True)
class IntakeEvent:
    name: str
    data: object


def _detect_type(upload: Upload | None, text: str | None) -> str:
    if upload is None:
        return INPUT_TEXT
    mime = upload.mime_type.split(";")[0].strip().lower()
    if mime == "application/pdf" or (upload.filename and upload.filename.lower().endswith(".pdf")):
        return INPUT_PDF
    if mime.startswith("image/"):
        return INPUT_IMAGE
    return INPUT_TEXT


def run_intake(
    *,
    upload: Upload | None = None,
    text: str | None = None,
    document_class_hint: str | None = None,
    use_model: bool = True,
    apply_correction: bool = True,
    engine: GemmaEngine | None = None,
) -> Iterator[IntakeEvent]:
    """Execute pipeline: routing -> extracting -> correcting -> normalizing."""
    input_type = _detect_type(upload, text)
    yield IntakeEvent(STAGE_ROUTING, {"input_type": input_type})

    asset_path: str | None = None
    if upload is not None:
        asset_path = save_upload(upload.data, upload.mime_type, upload.filename)

    raw_transcript = ""
    extraction_method = METHOD_DIRECT
    extraction_status = STATUS_OK
    pages: int | None = None
    notes: list[Note] = []

    ai_engine = engine or GemmaEngine()

    yield IntakeEvent(STAGE_EXTRACTING, {"stage": "extracting", "input_type": input_type})

    if input_type == INPUT_TEXT:
        raw_transcript = (text or "").strip()
        if not raw_transcript:
            extraction_status = STATUS_EMPTY
            notes.append(
                Note(
                    level="warning",
                    message_np="कुनै पाठ प्राप्त भएन।",
                    message_en="No text provided for intake.",
                )
            )

    elif input_type == INPUT_PDF and upload is not None:
        try:
            pdf = extract_pdf_text(upload.data)
            pages = pdf.pages
        except Exception as exc:
            # Corrupted/unsupported file content — the AI engine was never
            # involved, so do not claim engine_unavailable or direct method.
            extraction_method = METHOD_UNAVAILABLE
            extraction_status = STATUS_UNSUPPORTED
            notes.append(
                Note(
                    level="error",
                    message_np=f"पीडीएफ पढ्न सकिएन: {str(exc)}",
                    message_en=f"Unsupported or corrupted PDF: {str(exc)}",
                )
            )
        else:
            if pdf.is_digital:
                raw_transcript = pdf.text
                extraction_method = METHOD_PYMUPDF
                extraction_status = STATUS_OK
            else:
                # Scanned PDF: rasterize first page for vision OCR
                try:
                    image_bytes = render_pdf_page(upload.data, page_number=0)
                except Exception as exc:
                    extraction_method = METHOD_UNAVAILABLE
                    extraction_status = STATUS_UNSUPPORTED
                    notes.append(
                        Note(
                            level="error",
                            message_np=f"पीडीएफ पृष्ठ रूपान्तरण असफल: {str(exc)}",
                            message_en=f"Unsupported or corrupted PDF page: {str(exc)}",
                        )
                    )
                else:
                    extracted = ai_engine.transcribe_image(image_bytes) if use_model else None
                    if extracted:
                        raw_transcript = extracted
                        extraction_method = METHOD_GEMMA4_VLM
                        extraction_status = STATUS_OK
                    else:
                        extraction_method = METHOD_UNAVAILABLE
                        extraction_status = STATUS_ENGINE_UNAVAILABLE
                        notes.append(
                            Note(
                                level="warning",
                                message_np="स्क्यान गरिएको पीडीएफ पढ्न AI भिजन उपलब्ध भएन।",
                                message_en="AI vision model unavailable to read scanned PDF.",
                            )
                        )

    elif input_type == INPUT_IMAGE and upload is not None:
        if use_model:
            extracted = ai_engine.transcribe_image(upload.data)
            if extracted:
                raw_transcript = extracted
                extraction_method = METHOD_GEMMA4_VLM
                extraction_status = STATUS_OK
            else:
                extraction_method = METHOD_UNAVAILABLE
                extraction_status = STATUS_ENGINE_UNAVAILABLE
                notes.append(
                    Note(
                        level="warning",
                        message_np="तस्बिरबाट पाठ निकाल्न AI मोडल उपलब्ध भएन। कृपया सिधै पाठ प्रविष्ट गर्नुहोस्।",
                        message_en="Vision model unavailable for image OCR. Please enter clinical text directly.",
                    )
                )
        else:
            extraction_method = METHOD_UNAVAILABLE
            extraction_status = STATUS_ENGINE_UNAVAILABLE

    # Step 2: Lexicon Correction
    yield IntakeEvent(STAGE_CORRECTING, {"raw_transcript": raw_transcript})

    corrections: tuple[Correction, ...] = ()
    unverified: tuple[str, ...] = ()
    corrected_text = raw_transcript

    if raw_transcript and apply_correction:
        corr_res = correct(raw_transcript)
        corrected_text = corr_res.text
        corrections = corr_res.corrections
        unverified = corr_res.unverified

    # Step 3: Document Classification
    classification = classify_document(corrected_text or raw_transcript)
    doc_class = document_class_hint or classification.document_class

    # Step 4: Normalization
    yield IntakeEvent(STAGE_NORMALIZING, {"corrected_text": corrected_text})

    normalized: NormalizationResult | None = None
    if corrected_text:
        from backend.nlp.tier3 import GemmaTier3Matcher
        tier3_matcher = GemmaTier3Matcher() if use_model else None
        normalized = normalize(corrected_text, tier3=tier3_matcher)

    result = IntakeResult(
        raw_transcript=raw_transcript,
        corrected_text=corrected_text,
        extraction_method=extraction_method,
        extraction_status=extraction_status,
        input_type=input_type,
        document_class=doc_class,
        document_class_evidence=classification.evidence,
        corrections=corrections,
        unverified=unverified,
        asset_path=asset_path,
        pages=pages,
        notes=notes,
        normalized=normalized,
    )

    yield IntakeEvent(STAGE_DONE, result)


def collect(events: Iterator[IntakeEvent]) -> IntakeResult:
    """Drain events and return final IntakeResult."""
    last_res: IntakeResult | None = None
    for event in events:
        if event.name == STAGE_DONE and isinstance(event.data, IntakeResult):
            last_res = event.data
    if last_res is None:
        raise RuntimeError("Intake pipeline finished without emitting done event")
    return last_res
