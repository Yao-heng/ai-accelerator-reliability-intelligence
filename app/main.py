from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="AI Accelerator Reliability Intelligence",
    description=(
        "MVP service for parsing accelerator logs, correlating telemetry, "
        "finding validation gaps, mapping firmware dependencies, and "
        "generating reliability recommendations."
    ),
    version="0.1.0",
)

app.include_router(router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Return a lightweight readiness signal for local demos."""
    return {"status": "ok", "service": "ai-accelerator-reliability-intelligence"}
