from collections.abc import Iterable
from datetime import datetime

from app.models.schemas import (
    AcceleratorLogEntry,
    CorrelatedEvent,
    CorrelatedMetric,
    TelemetrySample,
)


METRIC_THRESHOLDS = {
    "temperature_c": 88,
    "hbm_ecc_uncorrected": 0,
    "pcie_replay_count": 1000,
    "power_watts": 650,
    "fabric_crc_errors": 0,
    "inference_latency_ms": 45,
}


class TelemetryCorrelator:
    """Connects log events to nearest telemetry samples for the same accelerator."""

    def correlate(
        self,
        logs: Iterable[AcceleratorLogEntry],
        telemetry_rows: Iterable[dict],
    ) -> list[CorrelatedEvent]:
        telemetry = [TelemetrySample(**row) for row in telemetry_rows]
        correlated: list[CorrelatedEvent] = []

        for index, log in enumerate(logs, start=1):
            if log.severity.value not in {"WARNING", "ERROR", "CRITICAL"}:
                continue

            sample = self._find_best_sample(log, telemetry)
            metrics = self._extract_metrics(sample) if sample else []
            failure_mode = self._classify_failure_mode(log, metrics)

            correlated.append(
                CorrelatedEvent(
                    incident_id=f"INC-{index:04d}",
                    timestamp=log.timestamp,
                    accelerator_id=log.accelerator_id,
                    rack_id=log.rack_id or (sample.rack_id if sample else None),
                    firmware_version=log.firmware_version
                    or (sample.firmware_version if sample else None),
                    event_code=log.event_code,
                    subsystem=log.subsystem,
                    severity=log.severity,
                    workload_id=sample.workload_id if sample else None,
                    workload_phase=sample.workload_phase if sample else None,
                    summary=f"{log.event_code}: {log.message}",
                    correlated_metrics=metrics,
                    likely_failure_mode=failure_mode,
                    confidence=self._confidence(metrics),
                )
            )

        return correlated

    def _find_best_sample(
        self,
        log: AcceleratorLogEntry,
        telemetry: list[TelemetrySample],
    ) -> TelemetrySample | None:
        candidates = [
            row
            for row in telemetry
            if row.accelerator_id == log.accelerator_id
            and (not log.firmware_version or row.firmware_version == log.firmware_version)
        ]
        if not candidates:
            return None
        return min(
            candidates,
            key=lambda row: abs(
                self._parse_timestamp(row.timestamp) - self._parse_timestamp(log.timestamp)
            ),
        )

    def _parse_timestamp(self, value: str) -> float:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()

    def _extract_metrics(self, sample: TelemetrySample) -> list[CorrelatedMetric]:
        metrics: list[CorrelatedMetric] = []

        for metric_name, threshold in METRIC_THRESHOLDS.items():
            value = getattr(sample, metric_name)
            status = self._metric_status(metric_name, value, threshold)
            if status != "nominal":
                metrics.append(
                    CorrelatedMetric(
                        name=metric_name,
                        value=value,
                        threshold=threshold,
                        status=status,
                    )
                )

        return metrics

    def _metric_status(self, metric_name: str, value: float | int, threshold: int) -> str:
        if metric_name in {"hbm_ecc_uncorrected", "fabric_crc_errors"}:
            return "anomalous" if value > threshold else "nominal"
        return "anomalous" if value >= threshold else "nominal"

    def _classify_failure_mode(
        self,
        log: AcceleratorLogEntry,
        metrics: list[CorrelatedMetric],
    ) -> str:
        metric_names = {metric.name for metric in metrics}
        event = log.event_code.upper()

        if "HBM" in event or "hbm_ecc_uncorrected" in metric_names:
            return "hbm_ecc_escalation"
        if "PCIE" in event or "pcie_replay_count" in metric_names:
            return "pcie_link_instability"
        if "THERMAL" in event or "temperature_c" in metric_names:
            return "thermal_throttle_boundary"
        if "FABRIC" in event or "fabric_crc_errors" in metric_names:
            return "fabric_crc_burst"
        if "POWER" in event or "power_watts" in metric_names:
            return "power_transient_overshoot"
        return "unknown_platform_degradation"

    def _confidence(self, metrics: list[CorrelatedMetric]) -> float:
        if not metrics:
            return 0.45
        return round(min(0.95, 0.65 + (0.1 * len(metrics))), 2)
