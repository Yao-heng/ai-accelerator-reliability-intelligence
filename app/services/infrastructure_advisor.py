from app.models.schemas import Anomaly, ReliabilityRecommendation, RiskScore


class InfrastructureReliabilityAdvisor:
    """Creates operations recommendations from telemetry anomalies and risk scores."""

    def recommend(
        self,
        anomalies: list[Anomaly],
        risk_scores: list[RiskScore],
    ) -> list[ReliabilityRecommendation]:
        recommendations: list[ReliabilityRecommendation] = []
        anomalies_by_accelerator = {
            score.accelerator_id: [
                anomaly
                for anomaly in anomalies
                if anomaly.accelerator_id == score.accelerator_id
            ]
            for score in risk_scores
        }

        for index, risk in enumerate(risk_scores, start=1):
            accelerator_anomalies = anomalies_by_accelerator[risk.accelerator_id]
            modes = sorted({anomaly.failure_mode for anomaly in accelerator_anomalies})
            recommendations.append(
                ReliabilityRecommendation(
                    recommendation_id=f"OPS-{index:04d}",
                    priority=self._priority(risk),
                    title=f"Contain {risk.accelerator_id} {risk.level} infrastructure risk",
                    rationale=(
                        f"{risk.accelerator_id} in {risk.rack_id} reached risk score "
                        f"{risk.score}/100 from {len(accelerator_anomalies)} telemetry anomaly signal(s)."
                    ),
                    evidence=[
                        anomaly.description for anomaly in accelerator_anomalies[:5]
                    ],
                    affected_components=self._affected_components(modes),
                    expected_impact=self._expected_impact(risk),
                    next_steps=self._next_steps(risk, modes),
                )
            )

        return recommendations

    def _priority(self, risk: RiskScore) -> str:
        if risk.level == "critical":
            return "critical"
        if risk.level == "high":
            return "high"
        return "medium"

    def _affected_components(self, modes: list[str]) -> list[str]:
        mapping = {
            "hbm_ecc_escalation": "HBM memory subsystem",
            "pcie_link_instability": "host PCIe fabric",
            "thermal_throttle_boundary": "rack thermal envelope",
            "fabric_crc_burst": "accelerator interconnect fabric",
            "power_transient_overshoot": "rack power delivery",
            "latency_slo_degradation": "serving runtime SLO path",
        }
        return [mapping.get(mode, mode) for mode in modes]

    def _expected_impact(self, risk: RiskScore) -> str:
        if risk.level == "critical":
            return "Prevent accelerator resets, workload evacuation, and correlated rack incidents."
        if risk.level == "high":
            return "Reduce performance collapse risk and improve incident containment time."
        return "Improve early warning precision for fleet operations."

    def _next_steps(self, risk: RiskScore, modes: list[str]) -> list[str]:
        steps = [
            "Attach the telemetry envelope to the incident ticket and freeze firmware rollout for the affected rack.",
            "Compare the accelerator against same-rack peers for correlated power, thermal, and fabric signals.",
        ]
        if "power_transient_overshoot" in modes:
            steps.append("Run rack power headroom verification before allowing larger prefill batches.")
        if "thermal_throttle_boundary" in modes:
            steps.append("Check fan curves, inlet temperature, and workload placement for thermal coupling.")
        if risk.level == "critical":
            steps.append("Drain or quarantine the accelerator until replay validation passes.")
        return steps
