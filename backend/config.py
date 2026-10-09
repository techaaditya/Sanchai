from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for ArogyaKhata backend.

    Values are resolved from the environment and optional .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=(),
    )

    port: int = 8000
    model_backend: str = "auto"  # "local", "cloud", "llamacpp", or "auto"

    # Local Gemma 4 E2B Multimodal inference (Ollama or llama.cpp)
    ollama_url: str = "http://localhost:11434"
    local_gemma_model: str = "google/gemma-4-E2B-it"
    gemma_model: str = "google/gemma-4-E2B-it"

    # Cloud fallback (Google AI Studio / Ollama Cloud / Gemini)
    ollama_cloud_url: str = "https://ollama.com"
    fallback_model: str = "gemma4:31b-cloud"
    gemma_cloud_model: str = "gemma4:31b-cloud"
    ollama_api_key: str = ""

    # llama.cpp server endpoint for multimodal GGUF
    llama_cpp_url: str = "http://localhost:8081"
    llama_cpp_model: str = "google/gemma-4-E2B-it"

    # Database & Data asset paths
    db_path: str = "./data/arogyakhata.db"
    lexicon_path: str = "./data/nepali_clinical_lexicon.json"
    benchmark_path: str = "./data/nepclinbench.json"
    upload_dir: str = "./uploads"

    # Allowed CORS Origins
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def resolved_backend(self) -> str:
        """Determines active model backend based on environment and availability."""
        choice = self.model_backend.strip().lower()
        if choice in {"cloud", "local", "llamacpp"}:
            return choice
        return "cloud" if self.ollama_api_key.strip() else "local"

    @property
    def model_base_url(self) -> str:
        if self.resolved_backend == "cloud":
            return self.ollama_cloud_url.rstrip("/")
        if self.resolved_backend == "llamacpp":
            return self.llama_cpp_url.rstrip("/")
        return self.ollama_url.rstrip("/")

    @property
    def active_model_name(self) -> str:
        if self.resolved_backend == "cloud":
            return self.fallback_model or self.gemma_cloud_model
        if self.resolved_backend == "llamacpp":
            return self.llama_cpp_model
        return self.local_gemma_model or self.gemma_model

    @property
    def model_headers(self) -> dict[str, str]:
        key = self.ollama_api_key.strip()
        if self.resolved_backend == "cloud" and key:
            return {"Authorization": f"Bearer {key}"}
        return {}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
