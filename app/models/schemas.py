from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Severity(str, Enum):
    info = "INFO"
    warning = "WARNING"
    error = "ERROR"
    critical = "CRITICAL"


class TelemetrySample(BaseModel):
    timestamp: str
    accelerator_id: str
    rack_id: str
    firmware_version: str
    workload_id: str
    workload_phase: str
    temperature_c: float
    hbm_ecc_corrected: int
    hbm_ecc_uncorrected: int
    pcie_replay_count: int
    power_watts: float
    fabric_crc_errors: int
    inference_latency_ms: float


class AcceleratorLogEntry(BaseModel):
    timestamp: str
    severity: Severity
    accelerator_id: str
    subsystem: str
    event_code: str
    message: str
    firmware_version: str | None = None
    rack_id: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class CorrelatedMetric(BaseModel):
    name: str
    value: float | int | str
    threshold: float | int | None = None
    status: str


class CorrelatedEvent(BaseModel):
    incident_id: str
    timestamp: str
    accelerator_id: str
    rack_id: str | None
    firmware_version: str | None
    event_code: str
    subsystem: str
    severity: Severity
    workload_id: str | None
    workload_phase: str | None
    summary: str
    correlated_metrics: list[CorrelatedMetric]
    likely_failure_mode: str
    confidence: float = Field(ge=0, le=1)


class ValidationScenario(BaseModel):
    scenario_id: str
    failure_mode: str
    firmware_versions: list[str]
    workload_phases: list[str]
    environmental_conditions: list[str]
    coverage_level: str
    last_run: str


class ValidationGap(BaseModel):
    gap_id: str
    incident_id: str
    failure_mode: str
    reason: str
    missing_conditions: list[str]
    suggested_validation: str
    priority: str


class FirmwareComponent(BaseModel):
    name: str
    version: str
    owner: str
    depends_on: list[str]
    impacts: list[str]
    risk_notes: list[str]


class DependencyMap(BaseModel):
    platform: str
    generated_from: str
    components: list[FirmwareComponent]
    adjacency: dict[str, list[str]]
    blast_radius: dict[str, list[str]]


class ReliabilityRecommendation(BaseModel):
    recommendation_id: str
    priority: str
    title: str
    rationale: str
    evidence: list[str]
    affected_components: list[str]
    expected_impact: str
    next_steps: list[str]


class RawFirmwareDependencyDocument(BaseModel):
    platform: str
    generated_from: str
    components: list[dict[str, Any]]


class TelemetryEnvelope(BaseModel):
    source: str = "inline"
    samples: list[TelemetrySample]


class TelemetryIngestionSummary(BaseModel):
    source: str
    sample_count: int
    accelerator_count: int
    rack_count: int
    firmware_versions: list[str]
    workload_phases: list[str]
    time_range: dict[str, str]


class Anomaly(BaseModel):
    anomaly_id: str
    timestamp: str
    accelerator_id: str
    rack_id: str
    firmware_version: str
    workload_id: str
    workload_phase: str
    metric: str
    value: float | int
    threshold: float | int
    severity: str
    failure_mode: str
    description: str


class RiskScore(BaseModel):
    accelerator_id: str
    rack_id: str
    score: int = Field(ge=0, le=100)
    level: str
    drivers: list[str]


class AnalyzeRequest(BaseModel):
    telemetry: list[dict[str, Any]] | None = Field(
        default=None,
        description="Optional telemetry samples. If omitted, bundled GPU telemetry logs are analyzed.",
    )


class AnalyzeResponse(BaseModel):
    ingestion: TelemetryIngestionSummary
    anomalies: list[Anomaly]
    risk_scores: list[RiskScore]
    recommendations: list[ReliabilityRecommendation]
