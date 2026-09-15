"""FastAPI uygulama girişi.

Şimdilik yalnızca sağlık ucu. Tenant middleware (ADR-0007), auth (AuthPort) ve router'lar
bölüm 5'te eklenir. Hata cevapları metin değil kod taşır (ADR-0010).
"""

from fastapi import FastAPI

from geppetto_api import __version__

app = FastAPI(title="Geppetto API", version=__version__)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}
