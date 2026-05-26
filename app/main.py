from fastapi import FastAPI, HTTPException

from app.api.routes import analyze_telemetry, router
from app.models.schemas import AnalyzeRequest, AnalyzeResponse


app = FastAPI(
    title="AI Accelerator Reliability Intelligence",
    description=(
        "MVP service for parsing accelerator logs, correlating telemetry, "
        "detecting anomalies, scoring infrastructure risk, mapping firmware "
        "dependencies, and generating reliability recommendations."
    ),
    version="0.2.0",
)

app.include_router(router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Return a lightweight readiness signal for local demos."""
    return {"status": "ok", "service": "ai-accelerator-reliability-intelligence"}


@app.post("/analyze", response_model=AnalyzeResponse, tags=["reliability"])
def analyze(request: AnalyzeRequest | None = None) -> AnalyzeResponse:
    """Root-level alias for the telemetry analysis endpoint."""
    try:
        return analyze_telemetry(request)
    except HTTPException:
        raise
