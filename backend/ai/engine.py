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

logger = logging.getLogger("sanchai.ai.engine")

VISION_TIMEOUT_SECONDS = 90.0
TEXT_TIMEOUT_SECONDS = 45.0


class GemmaEngine:
    """Unified engine for clinical document extraction and assistant inference.
    
    Dual-Tier Architecture:
    - Primary Model: gemma4:31b-cloud (Ollama Cloud API)
    - Edge / Offline Fallback: gemma4:e2b-it-qat (Quantized local Ollama instance)
    """

    def __init__(self) -> None:
        self.cloud_url = settings.ollama_cloud_url.rstrip("/")
        self.local_url = settings.ollama_url.rstrip("/")
        self.model_name = settings.active_model_name
        self.fallback_model = settings.fallback_model_name

    # --------------------------------------------------------------------------
    # 1. Vision OCR: Prescription & Lab Document Transcription
    # --------------------------------------------------------------------------

    def transcribe_image(self, image_bytes: bytes, prompt: str | None = None) -> str | None:
        """Extract verbatim Devanagari and Latin text from medical document image.

        Routes to gemma4:31b-cloud with local gemma4:e2b-it-qat Ollama fallback.
        """
        active_prompt = prompt or OCR_TRANSCRIBE_PROMPT
        b64_image = base64.b64encode(image_bytes).decode("ascii")

        # 1. Try Primary Cloud Ollama (gemma4:31b-cloud)
        api_key = settings.ollama_api_key.strip()
        if api_key:
            cloud_payload = {
                "model": self.model_name,
                "prompt": active_prompt,
                "images": [b64_image],
                "stream": False,
                "options": {"temperature": 0.0},
            }
            headers = {"Authorization": f"Bearer {api_key}"}
            try:
                with httpx.Client(timeout=VISION_TIMEOUT_SECONDS) as client:
                    res = client.post(f"{self.cloud_url}/api/generate", json=cloud_payload, headers=headers)
                    if res.status_code == 200:
                        text = res.json().get("response", "").strip()
                        if text:
                            return text
            except Exception as exc:
                logger.warning("Cloud vision inference failed, falling back to local model: %s", exc)

        # 2. Try Local Ollama fallback (gemma4:e2b-it-qat)
        local_payload = {
            "model": self.fallback_model,
            "prompt": active_prompt,
            "images": [b64_image],
            "stream": False,
            "options": {"temperature": 0.0},
        }
        try:
            with httpx.Client(timeout=VISION_TIMEOUT_SECONDS) as client:
                res = client.post(f"{self.local_url}/api/generate", json=local_payload)
                if res.status_code == 200:
                    text = res.json().get("response", "").strip()
                    if text:
                        return text
        except Exception as exc:
            logger.info("Local Ollama vision fallback unavailable: %s", exc)

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
        """Generates text via gemma4:31b-cloud (Ollama Cloud) with local gemma4:e2b-it-qat fallback."""
        # 1. Cloud Ollama (Primary)
        api_key = settings.ollama_api_key.strip()
        if api_key:
            cloud_payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.0},
            }
            headers = {"Authorization": f"Bearer {api_key}"}
            try:
                with httpx.Client(timeout=TEXT_TIMEOUT_SECONDS) as client:
                    res = client.post(f"{self.cloud_url}/api/generate", json=cloud_payload, headers=headers)
                    if res.status_code == 200:
                        text = res.json().get("response", "").strip()
                        if text:
                            return text
            except Exception as exc:
                logger.warning("Cloud generation failed, trying local fallback: %s", exc)

        # 2. Local Ollama fallback (gemma4:e2b-it-qat)
        local_payload = {
            "model": self.fallback_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.0},
        }
        try:
            with httpx.Client(timeout=TEXT_TIMEOUT_SECONDS) as client:
                res = client.post(f"{self.local_url}/api/generate", json=local_payload)
                if res.status_code == 200:
                    text = res.json().get("response", "").strip()
                    if text:
                        return text
        except Exception as exc:
            logger.info("Local Ollama text fallback unavailable: %s", exc)

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
            "fallback_model": self.fallback_model,
            "primary_backend": f"ollama_cloud ({self.model_name})",
            "offline_backend": f"ollama_local ({self.fallback_model})",
            "cloud_configured": bool(api_key),
            "cloud_reachable": cloud_up,
            "local_fallback_available": local_up,
            "supported_modalities": ["image_vision_ocr", "digital_pdf", "clinical_text"],
        }


ai_engine = GemmaEngine()
