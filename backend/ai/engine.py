"""AI Engine for Google Gemma 4 (gemma4:31b-cloud) via Ollama Cloud.

Coordinates:
1. Primary AI Model: gemma4:31b-cloud via Ollama Cloud API.
2. Ingestion modalities:
   - Vision OCR: Medical prescriptions, doctor notes, and printed lab reports.
   - Digital PDF extraction (PyMuPDF).
   - Clinical text.
   (Note: Voice/Audio input is strictly de-scoped for future work).
3. Grounded clinical question answering with mandatory [entry:id] citations.
4. Resilient error handling: failures degrade gracefully without throwing 500 errors.
"""

from __future__ import annotations

import base64
import json
import logging
from typing import Any
import httpx

from backend.ai.prompts import (
    OCR_TRANSCRIBE_PROMPT,
    ASSISTANT_SYSTEM_PROMPT,
    SUMMARY_NARRATIVE_PROMPT,
    MEANING_NP_PROMPT,
)
from backend.config import settings

logger = logging.getLogger("arogyakhata.ai.engine")

VISION_TIMEOUT_SECONDS = 90.0
TEXT_TIMEOUT_SECONDS = 45.0


class GemmaEngine:
    """Unified engine for clinical document extraction and assistant inference."""

    def __init__(self) -> None:
        self.cloud_url = settings.ollama_cloud_url.rstrip("/")
        self.local_url = settings.ollama_url.rstrip("/")
        self.model_name = settings.active_model_name

    # --------------------------------------------------------------------------
    # 1. Vision OCR: Prescription & Lab Document Transcription
    # --------------------------------------------------------------------------

    def transcribe_image(self, image_bytes: bytes, prompt: str | None = None) -> str | None:
        """Extract verbatim Devanagari and Latin text from medical document image.

        Routes to gemma4:31b-cloud with local Ollama fallback if running.
        """
        active_prompt = prompt or OCR_TRANSCRIBE_PROMPT
        b64_image = base64.b64encode(image_bytes).decode("ascii")

        payload = {
            "model": self.model_name,
            "prompt": active_prompt,
            "images": [b64_image],
            "stream": False,
            "options": {"temperature": 0.0},
        }

        # 1. Try Primary Cloud Ollama
        api_key = settings.ollama_api_key.strip()
        if api_key:
            headers = {"Authorization": f"Bearer {api_key}"}
            try:
                with httpx.Client(timeout=VISION_TIMEOUT_SECONDS) as client:
                    res = client.post(f"{self.cloud_url}/api/generate", json=payload, headers=headers)
                    if res.status_code == 200:
                        text = res.json().get("response", "").strip()
                        if text:
                            return text
            except Exception as exc:
                logger.warning("Cloud vision inference failed: %s", exc)

        # 2. Try Local Ollama fallback (if running locally)
        try:
            with httpx.Client(timeout=VISION_TIMEOUT_SECONDS) as client:
                res = client.post(f"{self.local_url}/api/generate", json=payload)
                if res.status_code == 200:
                    text = res.json().get("response", "").strip()
                    if text:
                        return text
        except Exception as exc:
            logger.info("Local Ollama vision unavailable: %s", exc)

        return None

    # --------------------------------------------------------------------------
    # 2. Grounded Clinical Assistant (Conversational Q&A)
    # --------------------------------------------------------------------------

    def chat_grounded(self, record_context_json: str, user_question: str) -> str:
        """Record-grounded assistant answering questions with strict [entry:id] citations."""
        prompt = (
            ASSISTANT_SYSTEM_PROMPT
            .replace("{record_context_json}", record_context_json)
            .replace("{user_question}", user_question)
        )

        response = self._generate_text(prompt, think=True)
        if response:
            return response
        return "I am currently running in offline mode and could not reach the clinical assistant model."

    # --------------------------------------------------------------------------
    # 3. Physician Summary & Plain-Nepali Explanations
    # --------------------------------------------------------------------------

    def generate_doctor_summary(
        self, patient_name: str, age: int | None, gender: str | None, allergies: str, entries_json: str
    ) -> str:
        """Generates 3-sentence clinical handoff note for physician summary."""
        prompt = (
            SUMMARY_NARRATIVE_PROMPT
            .replace("{patient_name}", patient_name)
            .replace("{age}", str(age) if age is not None else "Unknown")
            .replace("{gender}", gender or "Unknown")
            .replace("{allergies}", allergies or "None reported")
            .replace("{entries_json}", entries_json)
        )
        res = self._generate_text(prompt, think=False)
        return res or f"Patient {patient_name} clinical summary: Review chronological entries below."

    def generate_meaning_np(self, normalized_json: str) -> str:
        """Generates patient-accessible plain-Nepali explanation."""
        prompt = MEANING_NP_PROMPT.replace("{normalized_json}", normalized_json)
        res = self._generate_text(prompt, think=False)
        return res or "यो जानकारी मात्र हो। डाक्टरको सल्लाह लिनुहोस्।"

    # --------------------------------------------------------------------------
    # 4. Core Text Generation
    # --------------------------------------------------------------------------

    def _generate_text(self, prompt: str, think: bool = False) -> str | None:
        """Generates text via gemma4:31b-cloud (Ollama Cloud) with local fallback."""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.0},
        }

        # 1. Cloud Ollama
        api_key = settings.ollama_api_key.strip()
        if api_key:
            headers = {"Authorization": f"Bearer {api_key}"}
            try:
                with httpx.Client(timeout=TEXT_TIMEOUT_SECONDS) as client:
                    res = client.post(f"{self.cloud_url}/api/generate", json=payload, headers=headers)
                    if res.status_code == 200:
                        text = res.json().get("response", "").strip()
                        if text:
                            return text
            except Exception:
                pass

        # 2. Local Ollama fallback
        try:
            with httpx.Client(timeout=TEXT_TIMEOUT_SECONDS) as client:
                res = client.post(f"{self.local_url}/api/generate", json=payload)
                if res.status_code == 200:
                    text = res.json().get("response", "").strip()
                    if text:
                        return text
        except Exception:
            pass

        return None

    # --------------------------------------------------------------------------
    # 5. Health & Backend Probing
    # --------------------------------------------------------------------------

    def check_health(self) -> dict[str, Any]:
        """Probes status of model inference backends."""
        local_up = False
        cloud_up = False

        # Probe local Ollama
        try:
            with httpx.Client(timeout=2.0) as client:
                r = client.get(f"{self.local_url}/api/version")
                local_up = (r.status_code == 200)
        except Exception:
            local_up = False

        # Probe cloud if key set
        api_key = settings.ollama_api_key.strip()
        if api_key:
            try:
                with httpx.Client(timeout=3.0) as client:
                    r = client.get(f"{self.cloud_url}/api/version", headers={"Authorization": f"Bearer {api_key}"})
                    cloud_up = (r.status_code == 200)
            except Exception:
                cloud_up = False

        return {
            "model_name": self.model_name,
            "primary_backend": "ollama_cloud (gemma4:31b-cloud)",
            "cloud_configured": bool(api_key),
            "cloud_reachable": cloud_up,
            "local_fallback_available": local_up,
            "supported_modalities": ["image_vision_ocr", "digital_pdf", "clinical_text"],
        }


ai_engine = GemmaEngine()
