from __future__ import annotations

import json
import logging
from collections.abc import Iterator

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from backend.intake.documents import (
    CLASS_BILL,
    CLASS_LAB_REPORT,
    CLASS_NOTE,
    CLASS_PRESCRIPTION,
)
from backend.intake.pipeline import (
    IntakeEvent,
    IntakeResult,
    Upload,
    collect,
    run_intake,
)
from backend.nlp.lexicon import get_lexicon
from backend.nlp.normalize import normalize
from backend.schemas import (
    IntakeRequest,
    IntakeResponse,
    NormalizeRequest,
    NormalizeResponse,
)

router = APIRouter(tags=["intake"])

logger = logging.getLogger("sanchai.intake")

DOCUMENT_CLASSES = {CLASS_PRESCRIPTION, CLASS_LAB_REPORT, CLASS_BILL, CLASS_NOTE}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
READ_CHUNK_BYTES = 1024 * 1024
SIZE_EXCEEDED_DETAIL = f"File exceeds {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit."
# Mirrors IntakeRequest.text max_length so the streaming route enforces the
# same cap as /intake/text instead of accepting unbounded text.
MAX_TEXT_CHARS = 20000


def _validate_hint(hint: str | None) -> str | None:
    if hint is None or hint == "":
        return None
    if hint not in DOCUMENT_CLASSES:
        raise HTTPException(
            status_code=422,
            detail=f"document_class must be one of {sorted(DOCUMENT_CLASSES)}",
        )
    return hint


async def _read_upload(file: UploadFile) -> Upload:
    # Reject on the parsed size before materialising the body in memory.
    if file.size is not None and file.size > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=SIZE_EXCEEDED_DETAIL)
    # Fall back to a bounded chunked read for unknown sizes: abort as soon as
    # the limit is crossed instead of buffering the whole upload first.
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(READ_CHUNK_BYTES)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail=SIZE_EXCEEDED_DETAIL)
        chunks.append(chunk)
    data = b"".join(chunks)
    if not data:
        raise HTTPException(status_code=422, detail="Uploaded file is empty.")
    return Upload(
        data=data,
        mime_type=file.content_type or "application/octet-stream",
        filename=file.filename,
    )


def _respond(result: IntakeResult) -> IntakeResponse:
    return result.to_response(get_lexicon())


@router.post("/intake/text", response_model=IntakeResponse)
def intake_text(payload: IntakeRequest) -> IntakeResponse:
    """Direct clinical text intake with lexicon-constrained correction and 3-tier normalization."""
    return _respond(
        collect(
            run_intake(
                text=payload.text,
                use_model=payload.use_model,
                apply_correction=payload.correct,
            )
        )
    )


@router.post("/intake/ocr", response_model=IntakeResponse)
async def intake_ocr(
    file: UploadFile = File(...),
    document_class: str | None = Form(default=None),
    use_model: bool = Form(default=True),
    correct: bool = Form(default=True),
) -> IntakeResponse:
    """Document intake: digital PDFs are extracted via PyMuPDF instantly; images are processed via vision OCR."""
    upload = await _read_upload(file)
    return _respond(
        collect(
            run_intake(
                upload=upload,
                document_class_hint=_validate_hint(document_class),
                use_model=use_model,
                apply_correction=correct,
            )
        )
    )


def _sse(events: Iterator[IntakeEvent]) -> Iterator[str]:
    """Serialize intake events as SSE frames.

    Guarantees:
    - A pipeline failure mid-stream emits a terminal ``event: error`` frame
      instead of silently truncating the response (streaming headers are
      already sent, so the HTTP status cannot change after the first frame).
    - The upstream ``run_intake`` generator is always closed, including on
      client disconnect (GeneratorExit), so no pipeline state is leaked.
    """
    try:
        lexicon = get_lexicon()
        for event in events:
            if isinstance(event.data, IntakeResult):
                body = event.data.to_response(lexicon).model_dump()
            else:
                body = event.data
            yield f"event: {event.name}\ndata: {json.dumps({'event': event.name, 'data': body}, ensure_ascii=False)}\n\n"
    except Exception as exc:  # noqa: BLE001 — stream is already open; report and terminate
        logger.exception("Intake stream aborted by pipeline error")
        error_body = {"event": "error", "data": {"error": type(exc).__name__, "detail": str(exc)}}
        yield f"event: error\ndata: {json.dumps(error_body, ensure_ascii=False)}\n\n"
    finally:
        closer = getattr(events, "close", None)
        if callable(closer):
            closer()


@router.post("/intake/stream")
async def intake_stream(
    file: UploadFile | None = File(default=None),
    text: str | None = Form(default=None),
    document_class: str | None = Form(default=None),
    use_model: bool = Form(default=True),
    correct: bool = Form(default=True),
) -> StreamingResponse:
    """Streamed intake returning Server-Sent Events (SSE) across extraction, correction, and normalization."""
    if file is None and not (text or "").strip():
        raise HTTPException(status_code=422, detail="Provide either an uploaded file or text.")
    if text is not None and len(text) > MAX_TEXT_CHARS:
        raise HTTPException(
            status_code=422,
            detail=f"text must be at most {MAX_TEXT_CHARS} characters",
        )

    upload = await _read_upload(file) if file is not None else None
    events = run_intake(
        upload=upload,
        text=text,
        document_class_hint=_validate_hint(document_class),
        use_model=use_model,
        apply_correction=correct,
    )
    return StreamingResponse(
        _sse(events),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/intake/normalize", response_model=NormalizeResponse)
def direct_normalize(payload: NormalizeRequest) -> NormalizeResponse:
    """Direct 3-tier normalization endpoint."""
    from backend.nlp.tier3 import GemmaTier3Matcher
    tier3_matcher = GemmaTier3Matcher() if payload.use_model else None
    result = normalize(payload.text, tier3=tier3_matcher)
    return NormalizeResponse.from_result(result, get_lexicon())
