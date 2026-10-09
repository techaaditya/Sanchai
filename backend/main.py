from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings

PROBE_TIMEOUT_SECONDS = 2.0


def _probe_db() -> dict[str, str]:
    """Check database file connectivity and basic integrity."""
    db_file = Path(settings.db_path)
    if not db_file.exists():
        return {"service": "db", "status": "pending_init", "detail": "db file not yet initialized"}
    try:
        import sqlite3
        con = sqlite3.connect(settings.db_path)
        cur = con.cursor()
        cur.execute("SELECT 1")
        cur.close()
        con.close()
        return {"service": "db", "status": "up"}
    except Exception as exc:  # noqa: BLE001
        return {"service": "db", "status": "down", "detail": type(exc).__name__}


async def _probe_remote(client: httpx.AsyncClient, name: str, url: str, **kwargs) -> dict[str, str]:
    try:
        response = await client.get(url, timeout=PROBE_TIMEOUT_SECONDS, **kwargs)
    except Exception as exc:  # noqa: BLE001
        return {"service": name, "status": "down", "detail": type(exc).__name__}
    if response.status_code >= 500:
        return {"service": name, "status": "degraded", "detail": f"HTTP {response.status_code}"}
    return {"service": name, "status": "up"}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Try initializing DB if db module is present
    try:
        from backend.db import init_db
        from backend.seed import seed_all
        init_db()
        from backend.db import session
        with session() as con:
            seed_all(con)
    except ImportError:
        pass
    # Reset lexicon cache if available
    try:
        from backend.nlp.lexicon import reset_lexicon_cache
        reset_lexicon_cache()
    except Exception:
        pass
    yield


app = FastAPI(
    title="Sanchai API",
    description="Sanchai (सञ्चै) - Bilingual Nepali Clinical Record & Interoperability Engine",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = APIRouter(prefix="/api/v1")


@api.get("/health")
async def health() -> dict[str, object]:
    model_probe_url = f"{settings.model_base_url}/api/tags"
    async with httpx.AsyncClient() as client:
        remote = await asyncio.gather(
            _probe_remote(
                client,
                "gemma_model",
                model_probe_url,
                headers=settings.model_headers,
            )
        )

    db_status = _probe_db()
    services = [db_status, *remote]
    
    # Healthy if DB is not down (even if remote model is offline in local dev)
    overall_status = "ok" if db_status["status"] in {"up", "pending_init"} else "degraded"

    return {
        "status": overall_status,
        "service": "sanchai-api",
        "model_backend": settings.resolved_backend,
        "model": settings.active_model_name,
        "services": services,
    }


app.include_router(api)
