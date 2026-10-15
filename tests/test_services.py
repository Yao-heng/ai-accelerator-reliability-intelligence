"""Unit tests for the core analysis services."""
from app.models.schemas import TelemetrySample
from app.services.anomaly_detector import AnomalyDetector
from app.services.log_parser import LogParser
from app.services.risk_scoring import RiskScorer


def make_sample(**overrides) -> TelemetrySample:
    base = dict(
        timestamp="2026-05-12T14:02:13Z",
        accelerator_id="GPU-01",
        rack_id="RACK-01",
        firmware_version="fw-1.0.0",
        workload_id="WL-01",
        workload_phase="training",
        temperature_c=70.0,
        hbm_ecc_corrected=0,
        hbm_ecc_uncorrected=0,
        pcie_replay_count=10,
        power_watts=400.0,
        fabric_crc_errors=0,
        inference_latency_ms=20.0,
    )
    base.update(overrides)
    return TelemetrySample(**base)


def test_nominal_sample_has_no_anomalies() -> None:
    assert AnomalyDetector().detect([make_sample()]) == []


def test_critical_temperature_detected() -> None:
    anomalies = AnomalyDetector().detect([make_sample(temperature_c=95.0)])
    assert len(anomalies) == 1
    assert anomalies[0].metric == "temperature_c"
    assert anomalies[0].severity == "critical"
    assert anomalies[0].failure_mode == "thermal_throttle_boundary"


def test_warning_threshold_detected() -> None:
    anomalies = AnomalyDetector().detect([make_sample(temperature_c=88.0)])
    assert len(anomalies) == 1
    assert anomalies[0].severity == "warning"


def test_risk_scorer_empty() -> None:
    assert RiskScorer().score([]) == []


def test_risk_scorer_scores_grouped_anomalies() -> None:
    anomalies = AnomalyDetector().detect(
        [make_sample(temperature_c=95.0, hbm_ecc_uncorrected=3, fabric_crc_errors=20)]
    )
    scores = RiskScorer().score(anomalies)
    assert len(scores) == 1
    assert scores[0].accelerator_id == "GPU-01"
    assert 0 < scores[0].score <= 100
    assert scores[0].level in {"medium", "high", "critical"}


def test_log_parser_structured_line() -> None:
    line = (
        '2026-05-12T14:02:13Z ERROR accelerator=GPU-01 rack=RACK-01 fw=fw-1.0.0 '
        'subsystem=pcie event=AER_FATAL message="PCIe fatal error detected"'
    )
    entries = LogParser().parse(line)
    assert len(entries) == 1
    assert entries[0].accelerator_id == "GPU-01"
    assert entries[0].subsystem == "pcie"


def test_log_parser_skips_blank_and_comment_lines() -> None:
    assert LogParser().parse("\n# comment only\n\n") == []
