from app.models.schemas import Anomaly, TelemetrySample


ANOMALY_THRESHOLDS = {
    "temperature_c": {"warning": 86, "critical": 92},
    "hbm_ecc_uncorrected": {"warning": 1, "critical": 2},
    "pcie_replay_count": {"warning": 900, "critical": 1500},
    "power_watts": {"warning": 640, "critical": 680},
    "fabric_crc_errors": {"warning": 1, "critical": 12},
    "inference_latency_ms": {"warning": 45, "critical": 60},
}

FAILURE_MODES = {
    "temperature_c": "thermal_throttle_boundary",
    "hbm_ecc_uncorrected": "hbm_ecc_escalation",
    "pcie_replay_count": "pcie_link_instability",
    "power_watts": "power_transient_overshoot",
    "fabric_crc_errors": "fabric_crc_burst",
    "inference_latency_ms": "latency_slo_degradation",
}


class AnomalyDetector:
    """Detects threshold-based reliability anomalies in accelerator telemetry."""

    def detect(self, samples: list[TelemetrySample]) -> list[Anomaly]:
        anomalies: list[Anomaly] = []
        counter = 1

        for sample in samples:
            for metric, thresholds in ANOMALY_THRESHOLDS.items():
                value = getattr(sample, metric)
                severity = self._severity(value, thresholds["warning"], thresholds["critical"])
                if severity == "nominal":
                    continue

                anomalies.append(
                    Anomaly(
                        anomaly_id=f"ANOM-{counter:04d}",
                        timestamp=sample.timestamp,
                        accelerator_id=sample.accelerator_id,
                        rack_id=sample.rack_id,
                        firmware_version=sample.firmware_version,
                        workload_id=sample.workload_id,
                        workload_phase=sample.workload_phase,
                        metric=metric,
                        value=value,
                        threshold=thresholds[severity],
                        severity=severity,
                        failure_mode=FAILURE_MODES[metric],
                        description=self._description(metric, value, thresholds[severity], sample),
                    )
                )
                counter += 1

        return anomalies

    def _severity(self, value: float | int, warning: float | int, critical: float | int) -> str:
        if value >= critical:
            return "critical"
        if value >= warning:
            return "warning"
        return "nominal"

    def _description(
        self,
        metric: str,
        value: float | int,
        threshold: float | int,
        sample: TelemetrySample,
    ) -> str:
        return (
            f"{metric}={value} crossed {threshold} on {sample.accelerator_id} "
            f"during {sample.workload_phase}."
        )
