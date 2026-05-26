from typing import Any

from app.models.schemas import AnalyzeResponse
from app.services.anomaly_detector import AnomalyDetector
from app.services.infrastructure_advisor import InfrastructureReliabilityAdvisor
from app.services.risk_scoring import RiskScorer
from app.services.telemetry_ingestion import TelemetryIngestionService


class ReliabilityAnalyzer:
    """Runs telemetry ingestion, anomaly detection, risk scoring, and recommendations."""

    def __init__(self) -> None:
        self.ingestion = TelemetryIngestionService()
        self.detector = AnomalyDetector()
        self.scorer = RiskScorer()
        self.advisor = InfrastructureReliabilityAdvisor()

    def analyze(self, payload: str | list[dict[str, Any]] | dict[str, Any]) -> AnalyzeResponse:
        samples, summary = self.ingestion.ingest(payload)
        anomalies = self.detector.detect(samples)
        risk_scores = self.scorer.score(anomalies)
        recommendations = self.advisor.recommend(anomalies, risk_scores)
        return AnalyzeResponse(
            ingestion=summary,
            anomalies=anomalies,
            risk_scores=risk_scores,
            recommendations=recommendations,
        )
