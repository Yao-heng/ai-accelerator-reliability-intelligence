import json
from collections.abc import Iterable
from typing import Any

from pydantic import ValidationError

from app.models.schemas import TelemetryEnvelope, TelemetryIngestionSummary, TelemetrySample


class TelemetryJsonParser:
    """Parses JSON and JSONL telemetry payloads into typed telemetry samples."""

    def parse(self, payload: str | list[dict[str, Any]] | dict[str, Any]) -> TelemetryEnvelope:
        if isinstance(payload, str):
            source = "jsonl" if "\n" in payload.strip() else "json"
            raw_samples = self._parse_text(payload)
        elif isinstance(payload, dict):
            source = str(payload.get("source", "inline-json"))
            raw_samples = payload.get("samples", [payload])
        else:
            source = "inline-json"
            raw_samples = payload

        samples = [TelemetrySample(**self._normalize_sample(row)) for row in raw_samples]
        return TelemetryEnvelope(source=source, samples=samples)

    def _parse_text(self, payload: str) -> list[dict[str, Any]]:
        text = payload.strip()
        if not text:
            return []

        if "\n" not in text and (text.startswith("[") or text.startswith("{")):
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed.get("samples", [parsed])
            return parsed

        rows: list[dict[str, Any]] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid telemetry JSONL at line {line_number}: {exc.msg}") from exc
        return rows

    def _normalize_sample(self, row: dict[str, Any]) -> dict[str, Any]:
        aliases = {
            "gpu_id": "accelerator_id",
            "tpu_id": "accelerator_id",
            "cluster_rack": "rack_id",
            "fw": "firmware_version",
            "phase": "workload_phase",
            "temp_c": "temperature_c",
            "power_draw_w": "power_watts",
            "latency_ms": "inference_latency_ms",
        }
        normalized = dict(row)
        for old_key, new_key in aliases.items():
            if old_key in normalized and new_key not in normalized:
                normalized[new_key] = normalized.pop(old_key)
        return normalized


class TelemetryIngestionService:
    """Ingests telemetry payloads and reports fleet-level inventory context."""

    def __init__(self, parser: TelemetryJsonParser | None = None) -> None:
        self.parser = parser or TelemetryJsonParser()

    def ingest(self, payload: str | list[dict[str, Any]] | dict[str, Any]) -> tuple[list[TelemetrySample], TelemetryIngestionSummary]:
        try:
            envelope = self.parser.parse(payload)
        except ValidationError as exc:
            raise ValueError(f"Telemetry payload failed schema validation: {exc}") from exc

        samples = envelope.samples
        timestamps = sorted(sample.timestamp for sample in samples)
        summary = TelemetryIngestionSummary(
            source=envelope.source,
            sample_count=len(samples),
            accelerator_count=len({sample.accelerator_id for sample in samples}),
            rack_count=len({sample.rack_id for sample in samples}),
            firmware_versions=sorted({sample.firmware_version for sample in samples}),
            workload_phases=sorted({sample.workload_phase for sample in samples}),
            time_range={
                "start": timestamps[0] if timestamps else "n/a",
                "end": timestamps[-1] if timestamps else "n/a",
            },
        )
        return samples, summary

    def samples_as_rows(self, samples: Iterable[TelemetrySample]) -> list[dict[str, Any]]:
        return [sample.model_dump(mode="json") for sample in samples]
