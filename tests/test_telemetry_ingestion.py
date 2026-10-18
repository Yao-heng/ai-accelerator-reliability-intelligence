"""Unit tests for TelemetryJsonParser and TelemetryIngestionService.

Covers the payload shapes the API accepts (single JSON object, JSON array,
JSONL text, inline envelope dict), the field-alias normalization, the
summary aggregation, and the error paths for malformed payloads.
"""

import json

import pytest

from app.services.telemetry_ingestion import TelemetryIngestionService, TelemetryJsonParser


def sample_row(**overrides: object) -> dict:
    row = {
        "timestamp": "2026-01-01T00:00:00Z",
        "accelerator_id": "GPU-1",
        "rack_id": "RACK-1",
        "firmware_version": "FW-1.0",
        "workload_id": "WL-1",
        "workload_phase": "training",
        "temperature_c": 65.0,
        "hbm_ecc_corrected": 0,
        "hbm_ecc_uncorrected": 0,
        "pcie_replay_count": 0,
        "power_watts": 350.0,
        "fabric_crc_errors": 0,
        "inference_latency_ms": 12.5,
    }
    row.update(overrides)
    return row


def test_parse_single_json_object_string() -> None:
    envelope = TelemetryJsonParser().parse(json.dumps(sample_row()))

    assert envelope.source == "json"
    assert len(envelope.samples) == 1
    assert envelope.samples[0].accelerator_id == "GPU-1"


def test_parse_jsonl_skips_blank_and_comment_lines() -> None:
    payload = "# header comment\n\n" + json.dumps(sample_row()) + "\n" + json.dumps(
        sample_row(accelerator_id="GPU-2")
    )

    envelope = TelemetryJsonParser().parse(payload)

    assert envelope.source == "jsonl"
    assert [s.accelerator_id for s in envelope.samples] == ["GPU-1", "GPU-2"]


def test_alias_fields_are_normalized() -> None:
    row = sample_row()
    # Replace canonical fields with their vendor-style aliases.
    row["gpu_id"] = row.pop("accelerator_id")
    row["cluster_rack"] = row.pop("rack_id")
    row["fw"] = row.pop("firmware_version")
    row["phase"] = row.pop("workload_phase")
    row["temp_c"] = row.pop("temperature_c")
    row["power_draw_w"] = row.pop("power_watts")
    row["latency_ms"] = row.pop("inference_latency_ms")

    envelope = TelemetryJsonParser().parse([row])
    sample = envelope.samples[0]

    assert sample.accelerator_id == "GPU-1"
    assert sample.rack_id == "RACK-1"
    assert sample.firmware_version == "FW-1.0"
    assert sample.workload_phase == "training"
    assert sample.temperature_c == 65.0
    assert sample.power_watts == 350.0
    assert sample.inference_latency_ms == 12.5


def test_canonical_field_wins_over_alias() -> None:
    row = sample_row()
    row["gpu_id"] = "GPU-SHADOW"

    envelope = TelemetryJsonParser().parse([row])

    assert envelope.samples[0].accelerator_id == "GPU-1"


def test_malformed_jsonl_line_reports_line_number() -> None:
    payload = json.dumps(sample_row()) + "\n{not valid json"

    with pytest.raises(ValueError, match="line 2"):
        TelemetryJsonParser().parse(payload)


def test_jsonl_line_that_is_not_an_object_is_rejected() -> None:
    with pytest.raises(ValueError, match="expected a JSON object"):
        TelemetryJsonParser().parse("[1, 2, 3]\n[4, 5, 6]")


def test_envelope_dict_preserves_source_and_samples() -> None:
    payload = {"source": "lab-capture", "samples": [sample_row(), sample_row(accelerator_id="GPU-2")]}

    envelope = TelemetryJsonParser().parse(payload)

    assert envelope.source == "lab-capture"
    assert len(envelope.samples) == 2


def test_ingest_empty_payload_produces_empty_summary() -> None:
    samples, summary = TelemetryIngestionService().ingest("")

    assert samples == []
    assert summary.sample_count == 0
    assert summary.accelerator_count == 0
    assert summary.time_range == {"start": "n/a", "end": "n/a"}


def test_ingest_summary_aggregates_inventory() -> None:
    rows = [
        sample_row(timestamp="2026-01-01T02:00:00Z", firmware_version="FW-2.0"),
        sample_row(
            timestamp="2026-01-01T01:00:00Z",
            accelerator_id="GPU-2",
            rack_id="RACK-2",
            workload_phase="inference",
        ),
    ]

    samples, summary = TelemetryIngestionService().ingest(rows)

    assert len(samples) == 2
    assert summary.sample_count == 2
    assert summary.accelerator_count == 2
    assert summary.rack_count == 2
    assert summary.firmware_versions == ["FW-1.0", "FW-2.0"]
    assert summary.workload_phases == ["inference", "training"]
    assert summary.time_range == {"start": "2026-01-01T01:00:00Z", "end": "2026-01-01T02:00:00Z"}


def test_ingest_schema_violation_is_wrapped_as_value_error() -> None:
    row = sample_row()
    del row["temperature_c"]

    with pytest.raises(ValueError, match="failed schema validation"):
        TelemetryIngestionService().ingest([row])
