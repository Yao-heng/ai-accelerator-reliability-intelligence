from collections import defaultdict

from app.models.schemas import Anomaly, RiskScore


SEVERITY_POINTS = {"warning": 12, "critical": 28}
FAILURE_MODE_POINTS = {
    "hbm_ecc_escalation": 18,
    "pcie_link_instability": 12,
    "thermal_throttle_boundary": 14,
    "fabric_crc_burst": 16,
    "power_transient_overshoot": 15,
    "latency_slo_degradation": 8,
}


class RiskScorer:
    """Scores operational risk for accelerator and rack-level triage."""

    def score(self, anomalies: list[Anomaly]) -> list[RiskScore]:
        grouped: dict[tuple[str, str], list[Anomaly]] = defaultdict(list)
        for anomaly in anomalies:
            grouped[(anomaly.accelerator_id, anomaly.rack_id)].append(anomaly)

        scores: list[RiskScore] = []
        for (accelerator_id, rack_id), accelerator_anomalies in grouped.items():
            raw_score = 10
            drivers: list[str] = []
            failure_modes = {anomaly.failure_mode for anomaly in accelerator_anomalies}

            for anomaly in accelerator_anomalies:
                raw_score += SEVERITY_POINTS[anomaly.severity]
                raw_score += FAILURE_MODE_POINTS.get(anomaly.failure_mode, 6)
                drivers.append(f"{anomaly.metric}={anomaly.value} ({anomaly.severity})")

            if len(failure_modes) >= 3:
                raw_score += 12
                drivers.append("multiple concurrent failure modes")

            score = min(100, raw_score)
            scores.append(
                RiskScore(
                    accelerator_id=accelerator_id,
                    rack_id=rack_id,
                    score=score,
                    level=self._level(score),
                    drivers=drivers,
                )
            )

        return sorted(scores, key=lambda item: item.score, reverse=True)

    def _level(self, score: int) -> str:
        if score >= 80:
            return "critical"
        if score >= 55:
            return "high"
        if score >= 30:
            return "medium"
        return "low"
